"""AnalysisPipeline: orchestrates the staged, explainable analysis.

understanding → stakeholders → conflicts → actions → isolated framework evaluations →
Dharma (RAG-grounded) → deterministic matrix → sensitivity → explanation → comparison.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.config import Settings
from app.core.versions import DISCLAIMER, version_record
from app.llm.base import LLMProvider
from app.llm.prompts import prompt_hashes
from app.schemas.analysis import AnalysisResult, ProviderInfo, RevisionRequest
from app.schemas.decision import DEFAULT_WEIGHTS
from app.schemas.dharma import KnowledgeBase
from app.schemas.dilemma import DilemmaContext, StructuredDilemma
from app.services.decision.engine import build_matrix
from app.services.decision.sensitivity import analyze
from app.services.dharma.engine import DharmaEngine
from app.services.dilemma import heuristic as H
from app.services.ethics.frameworks import REGISTRY
from app.services.explanation.engine import annotate_disagreements, compare, explain
from app.services.llm_backend import LLMBackend


class AnalysisPipeline:
    def __init__(self, settings: Settings, kb: KnowledgeBase, provider: LLMProvider | None = None):
        self.s = settings
        self.kb = kb
        self.provider = provider
        self.llm = LLMBackend(provider, settings) if provider else None
        self.dharma_engine = DharmaEngine(kb)

    def provider_info(self) -> ProviderInfo:
        if self.provider:
            return ProviderInfo(provider=self.provider.name, model=self.provider.model, is_llm=True,
                                note="Semantic stages use the LLM; aggregation, ranking and sensitivity are deterministic code.")
        return ProviderInfo(provider="heuristic", model="dharmanet-heuristic-0.1", is_llm=False,
                            note="Offline transparent keyword/rule engine — reproducible, but it does not understand "
                                 "language like an LLM. Configure an LLM provider for richer semantic analysis.")

    # ------------------------------------------------------------------ entry points

    def run(self, text: str, context: DilemmaContext | None = None, weights: dict[str, float] | None = None,
            include_dharma: bool = True) -> AnalysisResult:
        context = context or DilemmaContext()
        fallbacks: list[str] = []
        if self.llm:
            try:
                d = self.llm.structure(text, context, fallbacks)
            except Exception as e:
                fallbacks.append(f"structure→heuristic ({e})")
                d = H.structure_dilemma(text, context)
        else:
            d = H.structure_dilemma(text, context)
        return self._evaluate(d, weights or dict(DEFAULT_WEIGHTS), include_dharma, fallbacks, parent_id=None)

    def revise(self, parent: AnalysisResult, rev: RevisionRequest) -> AnalysisResult:
        d = parent.structured.model_copy(deep=True)
        if rev.stakeholders is not None:
            before = {s.id: s for s in parent.structured.stakeholders}
            d.stakeholders = [s if before.get(s.id) == s else s.model_copy(update={"user_edited": True})
                              for s in rev.stakeholders]
        if rev.actions is not None:
            known = {a.id: a for a in parent.structured.actions}
            acts = []
            for a in rev.actions:
                if a.id not in known:
                    upd: dict = {"user_added": True}
                    if a.kind != "custom" and a.features == type(a.features)():
                        upd["features"] = H.features_for(a.kind)  # template profile for new typed actions
                    a = a.model_copy(update=upd)
                acts.append(a)
            d.actions = acts
        if rev.assumptions is not None:
            d.assumptions = rev.assumptions
        if rev.additional_context:
            d.context.additional = (d.context.additional + " " + rev.additional_context).strip()
            d.cues = H.compute_cues(H._norm(d.dilemma_text + " " + d.context.additional))
        weights = rev.weights.values if rev.weights else parent.matrix.weights
        return self._evaluate(d, weights, parent.include_dharma, ["human revision of parent analysis"],
                              parent_id=parent.id)

    def rescore(self, r: AnalysisResult, weights: dict[str, float]) -> AnalysisResult:
        """Deterministic re-ranking with new weights; no semantic stage is re-run."""
        labels = {a.id: a.label for a in r.structured.actions}
        ids = [a.id for a in r.structured.actions]
        m = build_matrix(r.evaluations, r.dharma, ids, labels, weights, r.include_dharma)
        sens = analyze(m, self.s.sensitivity_samples, r.seed)
        exp = explain(r.structured, r.evaluations, r.dharma, m, sens, r.fallbacks)
        return r.model_copy(update={"matrix": m, "sensitivity": sens, "explanation": exp,
                                    "comparison": compare(r.structured, r.evaluations, r.dharma, m)})

    # ------------------------------------------------------------------ core

    def _evaluate(self, d: StructuredDilemma, weights: dict[str, float], include_dharma: bool,
                  fallbacks: list[str], parent_id: str | None) -> AnalysisResult:
        if len(d.actions) < 2:
            raise ValueError("at least two candidate actions are required")
        evaluations = []
        for fw in REGISTRY:
            if self.llm:
                try:
                    evaluations.append(self.llm.evaluate_framework(fw, d, fallbacks))
                except Exception as e:
                    fallbacks.append(f"{fw.id}→heuristic ({e})")
                    heur = fw.evaluate(d)
                    heur.source = "heuristic_fallback"
                    evaluations.append(heur)
            else:
                evaluations.append(fw.evaluate(d))
        dharma = None
        if include_dharma:
            retrieved = self.dharma_engine.retrieve(d)
            dharma = self.dharma_engine.evaluate(d, retrieved)
            if self.llm:
                try:
                    dharma = self.llm.dharma(d, retrieved, self.kb, dharma, fallbacks)
                except Exception as e:
                    fallbacks.append(f"dharma→heuristic ({e})")
            for r in dharma.readings:  # surface grounded Dharma claims as matrix-cell citations
                r.contributions = [c for c in r.contributions if c.entry_ids]
        annotate_disagreements(evaluations, dharma)
        labels = {a.id: a.label for a in d.actions}
        ids = [a.id for a in d.actions]
        m = build_matrix(evaluations, dharma, ids, labels, weights, include_dharma)
        sens = analyze(m, self.s.sensitivity_samples, self.s.sensitivity_seed)
        exp = explain(d, evaluations, dharma, m, sens, fallbacks)
        versions = version_record(self.kb.version)
        if self.provider:
            versions.update({f"prompt:{k}": v for k, v in prompt_hashes().items()})
        return AnalysisResult(
            id=uuid.uuid4().hex[:12], parent_id=parent_id, created_at=datetime.now(timezone.utc),
            versions=versions, provider=self.provider_info(), structured=d, evaluations=evaluations,
            dharma=dharma, matrix=m, sensitivity=sens, explanation=exp,
            comparison=compare(d, evaluations, dharma, m), fallbacks=fallbacks,
            include_dharma=include_dharma, seed=self.s.sensitivity_seed, disclaimer=DISCLAIMER,
        )
