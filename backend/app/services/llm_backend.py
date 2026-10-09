"""LLM-backed implementations of the semantic pipeline stages.

Every stage validates output against a Pydantic schema; on failure the stage falls back to the
heuristic engine and the fallback is recorded on the run (never silently)."""
from __future__ import annotations

import json

from pydantic import BaseModel, Field

from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.prompts import render
from app.llm.structured import StructuredOutputError, generate_structured
from app.rag.knowledge import kb_index
from app.schemas.dharma import (
    ConceptContribution, DharmaActionReading, DharmaEvaluation, KnowledgeBase, RetrievedEntry,
)
from app.schemas.dilemma import (
    Action, ActionFeatures, ActionKind, Conflict, ConflictType, ContextCues, DilemmaContext, Stakeholder,
    StakeholderRole, StructuredDilemma,
)
from app.schemas.evaluation import DimensionScore, FrameworkEvaluation
from app.services.dharma.engine import validate_citations
from app.services.dilemma import heuristic as H
from app.services.ethics.frameworks import Framework


# ---- LLM response schemas (validated before use) -------------------------------------------

class _Cues(BaseModel):
    severity: float = Field(ge=0, le=1)
    vulnerability: float = Field(ge=0, le=1)
    relational_closeness: float = Field(ge=0, le=1)
    uncertainty: float = Field(ge=0, le=1)
    legal_dimension: float = Field(ge=0, le=1)
    urgency: float = Field(ge=0, le=1)
    scale: float = Field(ge=0, le=1)


class DilemmaLLM(BaseModel):
    summary: str
    domain: str = "general"
    decision_maker: str = "You (the decision-maker)"
    constraints: list[str] = []
    uncertainties: list[str] = []
    assumptions: list[str] = []
    cues: _Cues


class _SH(BaseModel):
    name: str
    category: str = "other"
    roles: list[StakeholderRole] = []
    interests: list[str] = []
    rights: list[str] = []
    responsibilities: list[str] = []
    vulnerabilities: list[str] = []
    potential_benefits: list[str] = []
    potential_harms: list[str] = []
    salience: float = Field(0.5, ge=0, le=1)


class StakeholdersLLM(BaseModel):
    stakeholders: list[_SH] = Field(min_length=2)


class _CF(BaseModel):
    type: ConflictType = "other"
    title: str
    description: str = ""
    between: list[str] = []
    intensity: float = Field(0.5, ge=0, le=1)


class ConflictsLLM(BaseModel):
    conflicts: list[_CF] = Field(min_length=1)


class _AC(BaseModel):
    label: str
    description: str = ""
    kind: ActionKind = "custom"
    features: ActionFeatures


class ActionsLLM(BaseModel):
    actions: list[_AC] = Field(min_length=3, max_length=10)


class _SC(BaseModel):
    action_id: str
    score: float = Field(ge=0, le=10)
    uncertainty: float = Field(ge=0, le=5)
    confidence: float = Field(ge=0, le=1)
    rationale: str
    assumptions: list[str] = []
    strengths: list[str] = []
    weaknesses: list[str] = []
    uncertainties: list[str] = []


class FrameworkLLM(BaseModel):
    scores: list[_SC]


class _RD(BaseModel):
    action_id: str
    score: float = Field(ge=0, le=10)
    uncertainty: float = Field(ge=0, le=5)
    confidence: float = Field(ge=0, le=1)
    interpretation: str
    contributions: list[ConceptContribution] = []
    limitations: list[str] = []


class DharmaLLM(BaseModel):
    readings: list[_RD]


REQUIRED_KINDS = ("escalate_internal", "compromise", "gather_info", "delay")


class LLMBackend:
    def __init__(self, provider: LLMProvider, settings: Settings):
        self.p = provider
        self.retries = settings.llm_max_retries

    def _call(self, prompt_name: str, schema, **kw):
        return generate_structured(self.p, render(prompt_name, **kw), schema, self.retries)

    def structure(self, text: str, context: DilemmaContext, fallbacks: list[str]) -> StructuredDilemma:
        base = H.structure_dilemma(text, context)  # heuristic result is the fallback for every sub-stage
        ctx = context.model_dump_json()
        try:
            dl = self._call("dilemma_extraction", DilemmaLLM, dilemma=text, context=ctx)
            base.summary, base.domain, base.decision_maker = dl.summary, dl.domain, dl.decision_maker
            base.constraints, base.uncertainties = dl.constraints or base.constraints, dl.uncertainties or base.uncertainties
            base.assumptions = dl.assumptions + [a for a in base.assumptions if "inferred" not in a]
            base.cues = ContextCues(**dl.cues.model_dump(), evidence=["LLM-estimated context cues"])
        except StructuredOutputError as e:
            fallbacks.append(f"dilemma_extraction→heuristic ({e})")
        try:
            sh = self._call("stakeholder_extraction", StakeholdersLLM, dilemma=text, summary=base.summary)
            base.stakeholders = [Stakeholder(id=f"s{i + 1}", **s.model_dump()) for i, s in enumerate(sh.stakeholders)]
        except StructuredOutputError as e:
            fallbacks.append(f"stakeholder_extraction→heuristic ({e})")
        names = {s.name.lower(): s.id for s in base.stakeholders}
        try:
            cf = self._call("conflict_identification", ConflictsLLM, dilemma=text,
                            stakeholders=", ".join(s.name for s in base.stakeholders))
            base.conflicts = [Conflict(id=f"c{i + 1}", type=c.type, title=c.title, description=c.description,
                                       between=[names.get(b.lower(), b) for b in c.between], intensity=c.intensity)
                              for i, c in enumerate(cf.conflicts)]
        except StructuredOutputError as e:
            fallbacks.append(f"conflict_identification→heuristic ({e})")
        try:
            ac = self._call("action_generation", ActionsLLM, dilemma=text,
                            conflicts="; ".join(c.title for c in base.conflicts))
            actions = [Action(id=f"a{i + 1}", label=a.label, description=a.description, kind=a.kind, features=a.features)
                       for i, a in enumerate(ac.actions)]
            kinds = {a.kind for a in actions}
            for h in base.actions:  # never silently lose the required option types
                if h.kind in REQUIRED_KINDS and h.kind not in kinds:
                    actions.append(h.model_copy(update={"id": f"a{len(actions) + 1}"}))
                    fallbacks.append(f"action_generation: added heuristic '{h.kind}' option missing from LLM output")
            base.actions = actions
        except StructuredOutputError as e:
            fallbacks.append(f"action_generation→heuristic ({e})")
        return base

    def evaluate_framework(self, fw: Framework, d: StructuredDilemma, fallbacks: list[str]) -> FrameworkEvaluation:
        heur = fw.evaluate(d)
        try:
            out = self._call(
                "framework_evaluation", FrameworkLLM, framework_name=fw.name, definition=fw.definition,
                principle=fw.principle, questions="; ".join(fw.key_questions), dilemma=d.dilemma_text,
                stakeholders=", ".join(f"{s.name}{' (vulnerable)' if s.is_vulnerable else ''}" for s in d.stakeholders),
                actions="\n".join(f"{a.id}: {a.label} - {a.description}" for a in d.actions))
            got = {s.action_id: s for s in out.scores}
            missing = [a.id for a in d.actions if a.id not in got]
            if missing:
                raise StructuredOutputError(f"missing scores for {missing}")
        except StructuredOutputError as e:
            fallbacks.append(f"{fw.id}→heuristic ({e})")
            heur.source = "heuristic_fallback"
            return heur
        hmap = {s.action_id: s for s in heur.scores}
        scores = [DimensionScore(dimension=fw.dimension, action_id=a.id, principle=fw.principle,
                                 flags=hmap[a.id].flags, evidence=["LLM judgment"],
                                 **got[a.id].model_dump(exclude={"action_id"})) for a in d.actions]
        best = max(scores, key=lambda s: s.score)
        return FrameworkEvaluation(framework_id=fw.id, framework_name=fw.name, framework_version=fw.version,
                                   source="llm", scores=scores, stakeholder_impacts=heur.stakeholder_impacts,
                                   summary=f"{fw.name} (LLM) rates '{best.action_id}' highest ({best.score:.1f}/10).")

    def dharma(self, d: StructuredDilemma, retrieved: list[RetrievedEntry], kb: KnowledgeBase,
               heuristic_eval: DharmaEvaluation, fallbacks: list[str]) -> DharmaEvaluation:
        idx = kb_index(kb)
        entries = "\n".join(f"{r.entry_id} | {idx[r.entry_id].citation} | {idx[r.entry_id].concept} | "
                            f"{idx[r.entry_id].paraphrase} | {idx[r.entry_id].interpretation}" for r in retrieved)
        try:
            out = self._call("dharma_evaluation", DharmaLLM, dilemma=d.dilemma_text, entries=entries,
                             actions="\n".join(f"{a.id}: {a.label} - {a.description}" for a in d.actions))
            got = {r.action_id: r for r in out.readings}
            if any(a.id not in got for a in d.actions):
                raise StructuredOutputError("missing readings")
        except StructuredOutputError as e:
            fallbacks.append(f"dharma→heuristic ({e})")
            heuristic_eval.source = "heuristic_fallback"
            return heuristic_eval
        ev = DharmaEvaluation(source="llm", kb_version=kb.version, retrieved=retrieved,
                              readings=[DharmaActionReading(**got[a.id].model_dump()) for a in d.actions],
                              overview=heuristic_eval.overview)
        return validate_citations(ev, kb, allowed={r.entry_id for r in retrieved})


def free_text_baseline(provider: LLMProvider, prompt_name: str, dilemma: str) -> str:
    """Used by the evaluation harness for LLM-only baselines."""
    class Out(BaseModel):
        analysis: str
        recommendation: str = ""
    o = generate_structured(provider, render(prompt_name, dilemma=dilemma), Out, 1)
    return json.dumps(o.model_dump())
