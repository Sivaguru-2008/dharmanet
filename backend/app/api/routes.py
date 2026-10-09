"""REST API (prefix /api). See docs/api.md."""
from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import AppState, get_state, require_auth
from app.core.privacy import anonymize
from app.core.versions import DISCLAIMER, version_record
from app.schemas.analysis import (
    AnalysisRequest, AnalysisResult, AnalysisSummary, DecisionRequest, FeedbackRequest, RescoreRequest,
    RevisionRequest,
)
from app.schemas.decision import DEFAULT_WEIGHTS
from app.schemas.dharma import KBEntry
from app.schemas.evaluation import DIMENSION_LABELS
from app.services.ethics.frameworks import REGISTRY

log = logging.getLogger("dharmanet.api")
public = APIRouter(prefix="/api")
router = APIRouter(prefix="/api", dependencies=[Depends(require_auth)])


@public.get("/health")
def health() -> dict:
    return {"status": "ok"}


@public.get("/meta")
def meta(state: AppState = Depends(get_state)) -> dict:
    return {
        "versions": version_record(state.kb.version),
        "provider": state.pipeline.provider_info().model_dump(),
        "frameworks": [f.describe_meta() for f in REGISTRY],
        "dimensions": DIMENSION_LABELS,
        "default_weights": DEFAULT_WEIGHTS,
        "disclaimer": DISCLAIMER,
        "auth_required": bool(state.settings.api_token),
    }


def _get(state: AppState, run_id: str) -> AnalysisResult:
    r = state.repo.get(run_id)
    if r is None:
        raise HTTPException(404, "analysis not found")
    return r


@router.post("/analyses", response_model=AnalysisResult)
def create_analysis(req: AnalysisRequest, state: AppState = Depends(get_state)) -> AnalysisResult:
    if len(req.dilemma) > state.settings.max_dilemma_chars:
        raise HTTPException(413, "dilemma too long")
    text = anonymize(req.dilemma) if state.settings.anonymize_input else req.dilemma
    t0 = time.perf_counter()
    try:
        r = state.pipeline.run(text, req.context, req.weights.values if req.weights else None, req.include_dharma)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    ms = int((time.perf_counter() - t0) * 1000)
    state.repo.save(r, req.model_dump(mode="json") | {"dilemma": text}, ms)
    log.info("analysis %s created provider=%s ms=%d fallbacks=%d", r.id, r.provider.provider, ms, len(r.fallbacks))
    return r


@router.get("/analyses", response_model=list[AnalysisSummary])
def list_analyses(limit: int = Query(50, ge=1, le=500), state: AppState = Depends(get_state)):
    return state.repo.list(limit)


@router.get("/analyses/{run_id}", response_model=AnalysisResult)
def get_analysis(run_id: str, state: AppState = Depends(get_state)):
    return _get(state, run_id)


@router.delete("/analyses/{run_id}")
def delete_analysis(run_id: str, state: AppState = Depends(get_state)) -> dict:
    if not state.repo.delete(run_id):
        raise HTTPException(404, "analysis not found")
    return {"deleted": run_id}


@router.post("/analyses/{run_id}/rescore", response_model=AnalysisResult)
def rescore(run_id: str, req: RescoreRequest, state: AppState = Depends(get_state)):
    r = state.pipeline.rescore(_get(state, run_id), req.weights.values)
    state.repo.update_scoring(r)
    return r


@router.post("/analyses/{run_id}/revise", response_model=AnalysisResult)
def revise(run_id: str, req: RevisionRequest, state: AppState = Depends(get_state)):
    parent = _get(state, run_id)
    t0 = time.perf_counter()
    try:
        r = state.pipeline.revise(parent, req)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    state.repo.save(r, {"revision_of": run_id, **req.model_dump(mode="json")}, int((time.perf_counter() - t0) * 1000))
    return r


@router.post("/analyses/{run_id}/decision")
def decide(run_id: str, req: DecisionRequest, state: AppState = Depends(get_state)) -> dict:
    r = _get(state, run_id)
    ids = {a.id for a in r.structured.actions}
    if req.choice in ("alternative", "modify") and req.action_id not in ids:
        raise HTTPException(422, "action_id must reference one of the analysed actions")
    action_id = req.action_id or (r.matrix.recommendation.action_id if req.choice == "accept" else None)
    decision = {"choice": req.choice, "action_id": action_id, "note": req.note,
                "recommended_action_id": r.matrix.recommendation.action_id,
                "statement": "Decision recorded. DharmaNet does not execute any action."}
    state.repo.record_decision(run_id, decision)
    return decision


@router.post("/analyses/{run_id}/feedback")
def feedback(run_id: str, req: FeedbackRequest, state: AppState = Depends(get_state)) -> dict:
    if any(not 1 <= v <= 5 for v in req.ratings.values()):
        raise HTTPException(422, "ratings must be Likert values 1-5")
    try:
        state.repo.record_feedback(run_id, req.useful, req.ratings, req.comment)
    except KeyError:
        raise HTTPException(404, "analysis not found") from None
    return {"recorded": True}


@router.get("/analyses/{run_id}/export")
def export(run_id: str, state: AppState = Depends(get_state)) -> dict:
    """Machine-readable research-log record."""
    r = _get(state, run_id)
    run = state.repo.raw(run_id)
    labels = {a.id: a.label for a in r.structured.actions}
    return {
        "analysis_id": r.id, "parent_id": r.parent_id, "timestamp": r.created_at.isoformat(),
        "dilemma": r.structured.dilemma_text, "context": r.structured.context.model_dump(),
        "stakeholders": [s.model_dump() for s in r.structured.stakeholders],
        "conflicts": [c.model_dump() for c in r.structured.conflicts],
        "actions": [a.model_dump() for a in r.structured.actions],
        "framework_scores": {ev.framework_id: {s.action_id: {"score": s.score, "uncertainty": s.uncertainty,
                                                            "confidence": s.confidence} for s in ev.scores}
                             for ev in r.evaluations},
        "dharma_analysis": r.dharma.model_dump() if r.dharma else None,
        "weights": r.matrix.weights,
        "ranking": [w.model_dump() for w in r.matrix.weighted],
        "equal_weight_ranking": [w.model_dump() for w in r.matrix.equal_weighted],
        "recommendation": {**r.matrix.recommendation.model_dump(), "label": labels[r.matrix.recommendation.action_id]},
        "uncertainty": {a: {"score": w.score, "pm": w.uncertainty, "confidence": w.confidence}
                        for a, w in ((w.action_id, w) for w in r.matrix.weighted)},
        "sensitivity": r.sensitivity.model_dump(),
        "explanation": r.explanation.model_dump(),
        "model": {"provider": r.provider.provider, "model": r.provider.model},
        "versions": r.versions, "seed": r.seed, "fallbacks": r.fallbacks,
        "duration_ms": run.duration_ms if run else None,
        "decision": r.decision, "feedback": state.repo.feedback_for(run_id),
    }


@router.get("/knowledge", response_model=list[KBEntry])
def knowledge(q: str = Query("", max_length=200), state: AppState = Depends(get_state)):
    if not q:
        return state.kb.entries
    ids = [r.entry_id for r in state.pipeline.dharma_engine.retriever.retrieve(q, [], k=50)]
    idx = {e.id: e for e in state.kb.entries}
    return [idx[i] for i in ids]
