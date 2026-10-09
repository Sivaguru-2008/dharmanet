"""Persistence of analysis runs and their normalised child records."""
from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.privacy import text_hash
from app.models import orm
from app.schemas.analysis import AnalysisResult, AnalysisSummary
from app.schemas.dharma import KnowledgeBase

ANON_USER = "anonymous"


class Repository:
    def __init__(self, factory: sessionmaker, store_text: bool = True):
        self.factory = factory
        self.store_text = store_text
        with self.factory() as s:
            if s.get(orm.User, ANON_USER) is None:
                s.add(orm.User(id=ANON_USER, display_name="anonymous"))
                s.commit()

    def sync_knowledge(self, kb: KnowledgeBase) -> None:
        with self.factory() as s:
            if s.scalar(select(orm.KnowledgeSource).where(orm.KnowledgeSource.kb_version == kb.version).limit(1)):
                return
            for e in kb.entries:
                s.add(orm.KnowledgeSource(entry_id=e.id, kb_version=kb.version, concept=e.concept, source=e.source,
                                          chapter=e.chapter, verse=e.verse, data=e.model_dump()))
            s.commit()

    def save(self, r: AnalysisResult, request_input: dict, duration_ms: int) -> None:
        payload = r.model_dump(mode="json")
        text = r.structured.dilemma_text
        if not self.store_text:
            payload["structured"]["dilemma_text"] = "[not stored]"
            request_input = {**request_input, "dilemma": "[not stored]"}
        with self.factory() as s:
            dl = orm.Dilemma(user_id=ANON_USER, text=text if self.store_text else None, text_hash=text_hash(text),
                             context=r.structured.context.model_dump())
            s.add(dl)
            s.flush()
            v = r.versions
            s.add(orm.AnalysisRun(
                id=r.id, dilemma_id=dl.id, parent_run_id=r.parent_id, provider=r.provider.provider,
                model=r.provider.model, analysis_version=v["analysis_version"], framework_version=v["framework_version"],
                prompt_version=v["prompt_version"], kb_version=v["dharma_kb_version"], scoring_version=v["scoring_version"],
                seed=r.seed, weights=r.matrix.weights, input=request_input, result=payload, fallbacks=r.fallbacks,
                duration_ms=duration_ms, created_at=r.created_at))
            s.flush()
            self._children(s, r)
            s.commit()

    def _children(self, s: Session, r: AnalysisResult) -> None:
        for st in r.structured.stakeholders:
            s.add(orm.StakeholderRow(run_id=r.id, sid=st.id, name=st.name, category=st.category,
                                     user_edited=st.user_edited, data=st.model_dump()))
        for a in r.structured.actions:
            s.add(orm.ActionRow(run_id=r.id, aid=a.id, label=a.label, kind=a.kind, user_added=a.user_added,
                                data=a.model_dump()))
        for ev in r.evaluations:
            for sc in ev.scores:
                s.add(orm.EthicalEvaluationRow(run_id=r.id, framework_id=ev.framework_id,
                                               framework_version=ev.framework_version, source=ev.source,
                                               action_aid=sc.action_id, score=sc.score, uncertainty=sc.uncertainty,
                                               confidence=sc.confidence, data=sc.model_dump()))
        if r.dharma:
            for rd in r.dharma.readings:
                s.add(orm.DharmaEvaluationRow(run_id=r.id, action_aid=rd.action_id, score=rd.score,
                                              uncertainty=rd.uncertainty, data=rd.model_dump()))
        self._matrix(s, r)

    def _matrix(self, s: Session, r: AnalysisResult) -> None:
        s.add(orm.DecisionMatrixRow(run_id=r.id, weights=r.matrix.weights, matrix=r.matrix.model_dump(),
                                    sensitivity=r.sensitivity.model_dump()))
        s.add(orm.ExplanationRow(run_id=r.id, data=r.explanation.model_dump()))

    def update_scoring(self, r: AnalysisResult) -> None:
        """After a deterministic rescore: store the new current result and append matrix/explanation history."""
        with self.factory() as s:
            run = s.get(orm.AnalysisRun, r.id)
            if run is None:
                raise KeyError(r.id)
            payload = r.model_dump(mode="json")
            if not self.store_text:
                payload["structured"]["dilemma_text"] = "[not stored]"
            run.result, run.weights = payload, r.matrix.weights
            self._matrix(s, r)
            s.commit()

    def get(self, run_id: str) -> AnalysisResult | None:
        with self.factory() as s:
            run = s.get(orm.AnalysisRun, run_id)
            return AnalysisResult.model_validate(run.result) if run else None

    def raw(self, run_id: str) -> orm.AnalysisRun | None:
        with self.factory() as s:
            return s.get(orm.AnalysisRun, run_id)

    def list(self, limit: int = 100) -> list[AnalysisSummary]:
        with self.factory() as s:
            runs = s.scalars(select(orm.AnalysisRun).order_by(orm.AnalysisRun.created_at.desc()).limit(limit)).all()
            out = []
            for run in runs:
                res = run.result
                labels = {a["id"]: a["label"] for a in res["structured"]["actions"]}
                out.append(AnalysisSummary(
                    id=run.id, parent_id=run.parent_run_id, created_at=run.created_at,
                    summary=res["structured"]["summary"], domain=res["structured"]["domain"],
                    recommended_label=labels.get(res["matrix"]["recommendation"]["action_id"], ""),
                    stability=res["sensitivity"]["label"], provider=run.provider,
                    decision=(res.get("decision") or {}).get("choice")))
            return out

    def record_decision(self, run_id: str, decision: dict) -> None:
        with self.factory() as s:
            run = s.get(orm.AnalysisRun, run_id)
            if run is None:
                raise KeyError(run_id)
            run.result = {**run.result, "decision": decision}
            s.add(orm.Feedback(run_id=run_id, kind="decision", decision=decision["choice"],
                               chosen_action=decision.get("action_id"), comment=decision.get("note", "")))
            s.commit()

    def record_feedback(self, run_id: str, useful: bool | None, ratings: dict, comment: str) -> None:
        with self.factory() as s:
            if s.get(orm.AnalysisRun, run_id) is None:
                raise KeyError(run_id)
            s.add(orm.Feedback(run_id=run_id, kind="feedback", useful=useful, ratings=ratings, comment=comment))
            s.commit()

    def feedback_for(self, run_id: str) -> list[dict]:
        with self.factory() as s:
            rows = s.scalars(select(orm.Feedback).where(orm.Feedback.run_id == run_id)).all()
            return [{"kind": f.kind, "decision": f.decision, "chosen_action": f.chosen_action, "useful": f.useful,
                     "ratings": f.ratings, "comment": f.comment, "created_at": f.created_at.isoformat()} for f in rows]

    def delete(self, run_id: str) -> bool:
        with self.factory() as s:
            run = s.get(orm.AnalysisRun, run_id)
            if run is None:
                return False
            dilemma_id = run.dilemma_id
            for model in (orm.StakeholderRow, orm.ActionRow, orm.EthicalEvaluationRow, orm.DharmaEvaluationRow,
                          orm.DecisionMatrixRow, orm.ExplanationRow, orm.Feedback):
                s.execute(delete(model).where(model.run_id == run_id))
            s.delete(run)
            s.flush()
            if not s.scalar(select(orm.AnalysisRun).where(orm.AnalysisRun.dilemma_id == dilemma_id).limit(1)):
                s.execute(delete(orm.Dilemma).where(orm.Dilemma.id == dilemma_id))
            s.commit()
            return True
