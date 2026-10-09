"""Modular ethical framework evaluators.

Each framework:
  * owns exactly one decision-matrix dimension,
  * receives ONLY the structured dilemma (never another framework's output → no contamination),
  * has a deterministic heuristic evaluator (formulas documented in docs/ethical-frameworks.md)
    and an LLM prompt (app/llm/prompts/v0_1/framework_<id>.md).

To add a framework: subclass `Framework`, implement `_raw`, and register it in `REGISTRY`.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.versions import FRAMEWORK_VERSION
from app.schemas.dilemma import Action, ActionFeatures, ContextCues, Stakeholder, StructuredDilemma
from app.schemas.evaluation import DimensionScore, FrameworkEvaluation, StakeholderImpact

FEATURE_TEXT: dict[str, tuple[str, str]] = {
    "prevents_harm": ("substantially prevents the threatened harm", "does little to prevent the threatened harm"),
    "causes_harm": ("imposes significant collateral harm", "imposes little collateral harm"),
    "honesty": ("is transparent and truthful", "involves concealment or limited transparency"),
    "role_duty": ("fulfils the decision-maker's role responsibilities", "neglects role responsibilities"),
    "due_process": ("respects fair process and proper channels", "bypasses fair process"),
    "protects_vulnerable": ("protects the most vulnerable stakeholders", "leaves vulnerable stakeholders exposed"),
    "preserves_relationships": ("preserves relationships and trust", "strains important relationships"),
    "self_interest": ("primarily serves the decision-maker's self-interest", "requires setting self-interest aside"),
    "reversibility": ("keeps options open / can be corrected later", "is hard to reverse"),
    "information_gain": ("reduces uncertainty before irreversible steps", "acts without reducing uncertainty"),
    "timeliness": ("acts before harm materialises", "allows harm to continue in the meantime"),
    "courage": ("requires moral courage", "avoids personal risk"),
}


def clip(x: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, x))


def describe(f: ActionFeatures, names: list[str]) -> tuple[list[str], list[str]]:
    """Plain-language strengths/weaknesses for the features a framework cares about."""
    strengths, weaknesses = [], []
    for n in names:
        v = getattr(f, n)
        good_when_high = n not in ("causes_harm", "self_interest")
        hi_text, lo_text = FEATURE_TEXT[n]
        if v >= 0.65:
            (strengths if good_when_high else weaknesses).append(hi_text)
        elif v <= 0.35:
            (weaknesses if good_when_high else strengths).append(lo_text)
    return strengths, weaknesses


def uncertainty_for(cues: ContextCues, ambiguity: float) -> tuple[float, float]:
    """Model-estimated ± (0-10 scale) and confidence. NOT a calibrated probability."""
    pm = round(0.5 + 1.5 * cues.uncertainty + 1.2 * ambiguity, 1)
    conf = round(max(0.3, min(0.9, 0.9 - 0.35 * cues.uncertainty - 0.3 * ambiguity)), 2)
    return pm, conf


@dataclass
class RawEval:
    score: float
    rationale: str
    ambiguity: float
    assumptions: list[str]
    flags: list[str]
    feature_focus: list[str]
    uncertainties: list[str]


class Framework:
    id: str = ""
    name: str = ""
    dimension: str = ""
    definition: str = ""
    principle: str = ""
    key_questions: list[str] = []
    version: str = FRAMEWORK_VERSION

    def describe_meta(self) -> dict:
        return {"id": self.id, "name": self.name, "dimension": self.dimension,
                "definition": self.definition, "principle": self.principle,
                "key_questions": self.key_questions, "version": self.version}

    def _raw(self, a: Action, d: StructuredDilemma) -> RawEval:  # pragma: no cover - abstract
        raise NotImplementedError

    def impacts(self, d: StructuredDilemma) -> list[StakeholderImpact]:
        return []

    def evaluate(self, d: StructuredDilemma) -> FrameworkEvaluation:
        scores = []
        for a in d.actions:
            r = self._raw(a, d)
            pm, conf = uncertainty_for(d.cues, r.ambiguity)
            strengths, weaknesses = describe(a.features, r.feature_focus)
            scores.append(DimensionScore(
                dimension=self.dimension, action_id=a.id, score=round(clip(r.score), 2),
                uncertainty=pm, confidence=conf, rationale=r.rationale, principle=self.principle,
                assumptions=r.assumptions, evidence=list(d.cues.evidence[:3]),
                strengths=strengths, weaknesses=weaknesses, uncertainties=r.uncertainties,
                flags=r.flags,
            ))
        best = max(scores, key=lambda s: s.score)
        label = next(a.label for a in d.actions if a.id == best.action_id)
        return FrameworkEvaluation(
            framework_id=self.id, framework_name=self.name, framework_version=self.version,
            source="heuristic", scores=scores, stakeholder_impacts=self.impacts(d),
            summary=f"{self.name} rates '{label}' highest ({best.score:.1f}/10).",
        )


class Consequentialism(Framework):
    id, name, dimension = "consequentialism", "Consequentialism", "consequences"
    definition = "Judges actions by their expected outcomes: benefits and harms to everyone affected, weighted by severity and likelihood, over short and long term."
    principle = "Choose the action with the best expected balance of benefits over harms."
    key_questions = ["What harms are prevented or caused?", "How severe and how likely?", "Who bears them?", "What are the long-term effects?"]

    def _raw(self, a: Action, d: StructuredDilemma) -> RawEval:
        f, c = a.features, d.cues
        stakes = c.severity * (0.6 + 0.4 * c.vulnerability)
        benefit = f.prevents_harm * stakes
        allowed = (1 - f.prevents_harm) * stakes * 0.6
        cost = f.causes_harm * (0.5 + 0.3 * c.scale) * 0.8
        long_term = 0.15 * (f.honesty - 0.5) + 0.1 * (f.reversibility - 0.5) * c.uncertainty
        raw = benefit - allowed - cost + long_term
        return RawEval(
            score=5 + 6 * raw,
            rationale=(f"Expected harm prevented {benefit:.2f} vs. harm left in place {allowed:.2f} and collateral "
                       f"harm {cost:.2f} (stakes = severity {c.severity:.2f} × vulnerability adj.); "
                       f"long-term trust/reversibility adjustment {long_term:+.2f}."),
            ambiguity=0.3 + 0.4 * (1 - f.reversibility),
            assumptions=["Severity and vulnerability inferred from the description are roughly right.",
                         "Collateral harms scale with the number of people affected."],
            flags=[], feature_focus=["prevents_harm", "causes_harm", "timeliness", "reversibility"],
            uncertainties=["Actual probabilities of outcomes are unknown."],
        )


class Deontology(Framework):
    id, name, dimension = "deontology", "Deontology / Duty ethics", "duty"
    definition = "Judges actions by whether they honour duties, rights and constraints (e.g., honesty, role obligations, fair process), regardless of outcome."
    principle = "Act according to duties and rights; some actions are wrong even if they produce good outcomes."
    key_questions = ["What duties does the decision-maker hold?", "Does the action involve deception?", "Are anyone's rights violated?", "Does it respect proper process?"]

    def _raw(self, a: Action, d: StructuredDilemma) -> RawEval:
        f, c = a.features, d.cues
        base = 0.4 * f.role_duty + 0.35 * f.honesty + 0.25 * f.due_process
        legal = 0.1 * c.legal_dimension * (f.due_process - 0.5)
        rescue = 0.15 * c.severity * (f.prevents_harm - 0.5)
        flags, penalty = [], 0.0
        if f.honesty < 0.3:
            flags.append("duty_violation:deception_or_concealment")
            penalty = 1.0
        return RawEval(
            score=10 * (base + legal + rescue) - penalty,
            rationale=(f"Role duty {f.role_duty:.2f}, honesty {f.honesty:.2f}, due process {f.due_process:.2f}; "
                       f"duty to prevent serious harm adjustment {10 * rescue:+.2f}"
                       + ("; penalised for concealment/deception." if penalty else ".")),
            ambiguity=0.25, flags=flags,
            assumptions=["The decision-maker's role carries the usual professional/relational duties.",
                         "A positive duty to prevent serious harm exists (contested by some deontologists)."],
            feature_focus=["role_duty", "honesty", "due_process"],
            uncertainties=["Which duty takes precedence when duties conflict is philosophically contested."],
        )


class Justice(Framework):
    id, name, dimension = "justice", "Justice / Fairness", "fairness"
    definition = "Judges how benefits and burdens are distributed, whether the vulnerable are protected, and whether procedures are fair and non-discriminatory."
    principle = "Treat people fairly: protect the vulnerable, distribute burdens equitably, use fair procedures."
    key_questions = ["Who bears the burdens?", "Are vulnerable groups protected?", "Is the procedure fair?", "Is anyone discriminated against?"]

    def _raw(self, a: Action, d: StructuredDilemma) -> RawEval:
        f, c = a.features, d.cues
        base = 0.35 * f.protects_vulnerable + 0.3 * f.due_process + 0.2 * (1 - f.causes_harm) + 0.15 * f.honesty
        vul = 0.1 * c.vulnerability * (f.protects_vulnerable - 0.5)
        return RawEval(
            score=10 * (base + vul),
            rationale=(f"Protection of vulnerable {f.protects_vulnerable:.2f}, procedural fairness "
                       f"{f.due_process:.2f}, burden imposed {f.causes_harm:.2f}, transparency {f.honesty:.2f}."),
            ambiguity=0.3, flags=[],
            assumptions=["Vulnerable stakeholders identified are the ones most at risk."],
            feature_focus=["protects_vulnerable", "due_process", "causes_harm"],
            uncertainties=["Equality vs. equity readings of fairness can disagree."],
        )


class VirtueEthics(Framework):
    id, name, dimension = "virtue", "Virtue ethics", "virtue"
    definition = "Asks what a person of good character (honest, courageous, compassionate, practically wise) would do, and what the action expresses about the agent."
    principle = "Act as a person of honesty, courage, compassion and practical wisdom would act."
    key_questions = ["Is the action honest?", "Does it show courage?", "Is it compassionate?", "Is it practically wise given uncertainty?"]

    def _raw(self, a: Action, d: StructuredDilemma) -> RawEval:
        f, c = a.features, d.cues
        compassion = (f.protects_vulnerable + f.preserves_relationships) / 2
        prudence = (f.information_gain + f.reversibility) / 2
        w_pru = 0.1 + 0.15 * c.uncertainty
        parts = {"honesty": (0.25, f.honesty), "courage": (0.2, f.courage),
                 "selflessness": (0.2, 1 - f.self_interest), "compassion": (0.2, compassion),
                 "practical wisdom": (w_pru, prudence)}
        total_w = sum(w for w, _ in parts.values())
        val = sum(w * v for w, v in parts.values()) / total_w
        return RawEval(
            score=10 * val,
            rationale="Character profile: " + ", ".join(f"{k} {v:.2f}" for k, (_, v) in parts.items())
                      + f" (practical-wisdom weight rises with uncertainty: {w_pru:.2f}).",
            ambiguity=0.25, flags=[],
            assumptions=["Virtues are weighed roughly equally; traditions differ on their ordering."],
            feature_focus=["honesty", "courage", "self_interest", "information_gain"],
            uncertainties=["Different virtues (e.g., loyalty vs. honesty) may point in different directions."],
        )


class CareEthics(Framework):
    id, name, dimension = "care", "Care ethics", "care"
    definition = "Focuses on relationships, dependency and responsiveness to the needs of particular people, especially those who depend on the decision-maker."
    principle = "Attend and respond to the needs of those in relationships of care and dependency."
    key_questions = ["Who depends on the decision-maker?", "Which relationships are affected?", "Is the response attentive to concrete needs?"]

    def _raw(self, a: Action, d: StructuredDilemma) -> RawEval:
        f, c = a.features, d.cues
        w = {"preserves_relationships": 0.2 + 0.3 * c.relational_closeness, "protects_vulnerable": 0.35,
             "avoids_collateral": 0.2, "reversibility": 0.1, "responsiveness": 0.15}
        v = {"preserves_relationships": f.preserves_relationships, "protects_vulnerable": f.protects_vulnerable,
             "avoids_collateral": 1 - f.causes_harm, "reversibility": f.reversibility,
             "responsiveness": f.timeliness * (0.5 + 0.5 * c.vulnerability)}
        val = sum(w[k] * v[k] for k in w) / sum(w.values())
        return RawEval(
            score=10 * val,
            rationale="Care profile: " + ", ".join(f"{k.replace('_', ' ')} {v[k]:.2f}" for k in w)
                      + f" (relationship weight scales with closeness {c.relational_closeness:.2f}).",
            ambiguity=0.3 + 0.2 * c.relational_closeness, flags=[],
            assumptions=["Relationships named in the dilemma are ones of genuine care or dependency."],
            feature_focus=["preserves_relationships", "protects_vulnerable", "causes_harm"],
            uncertainties=["The emotional dynamics of the relationships are not described in detail."],
        )


IMPACT_GROUP = {
    "protected": {"customers", "patients", "public", "children", "environment", "data_subjects", "students"},
    "institutional": {"organization", "management", "shareholders", "employees"},
    "relational": {"family", "friend"},
    "oversight": {"regulators"},
}


def stakeholder_impact(s: Stakeholder, f: ActionFeatures) -> tuple[float, str]:
    def sc(x: float) -> float:  # 0..1 -> -1..1
        return 2 * x - 1

    if s.category == "decision_maker":
        val = 0.5 * sc(f.self_interest) + 0.2 * sc(f.preserves_relationships) + 0.3 * sc(f.role_duty)
        note = "personal cost/benefit and integrity"
    elif s.category in IMPACT_GROUP["protected"]:
        val = 0.8 * sc(f.prevents_harm) + 0.2 * sc(f.honesty)
        note = "protection from harm and honest information"
    elif s.category in IMPACT_GROUP["institutional"]:
        val = -0.6 * sc(f.causes_harm) + 0.25 * sc(f.due_process) + 0.15 * sc(f.preserves_relationships)
        note = "collateral costs vs. fair chance to respond"
    elif s.category in IMPACT_GROUP["relational"]:
        val = 0.6 * sc(f.preserves_relationships) + 0.2 * sc(f.honesty) - 0.2 * sc(f.causes_harm)
        note = "relationship and trust"
    elif s.category in IMPACT_GROUP["oversight"]:
        val = 0.5 * sc(f.due_process) + 0.5 * sc(f.honesty)
        note = "access to accurate information through proper process"
    else:
        val = 0.6 * sc(f.prevents_harm) - 0.4 * sc(f.causes_harm)
        note = "general harm/benefit"
    return max(-1.0, min(1.0, val)), note


class StakeholderImpactFramework(Framework):
    id, name, dimension = "stakeholder", "Stakeholder impact analysis", "stakeholder_impact"
    definition = "Aggregates the estimated impact of each action on every identified stakeholder, weighting by salience and giving extra weight to vulnerable stakeholders."
    principle = "Account explicitly for every affected party, with extra weight for the vulnerable."
    key_questions = ["Who is helped and who is harmed?", "Are vulnerable stakeholders prioritised?", "Are indirect effects considered?"]

    def _weight(self, s: Stakeholder) -> float:
        return s.salience * (1.5 if s.is_vulnerable else 1.0)

    def impacts(self, d: StructuredDilemma) -> list[StakeholderImpact]:
        out = []
        for a in d.actions:
            for s in d.stakeholders:
                v, note = stakeholder_impact(s, a.features)
                out.append(StakeholderImpact(stakeholder_id=s.id, action_id=a.id, impact=round(v, 3), note=note))
        return out

    def _raw(self, a: Action, d: StructuredDilemma) -> RawEval:
        total_w, acc, parts = 0.0, 0.0, []
        for s in d.stakeholders:
            v, _ = stakeholder_impact(s, a.features)
            w = self._weight(s)
            total_w += w
            acc += w * v
            parts.append((abs(w * v), s.name, v))
        mean = acc / total_w if total_w else 0.0
        top = sorted(parts, reverse=True)[:3]
        return RawEval(
            score=5 + 5 * mean,
            rationale=f"Salience-weighted mean impact {mean:+.2f} across {len(d.stakeholders)} stakeholders; largest drivers: "
                      + "; ".join(f"{n} ({v:+.2f})" for _, n, v in top) + ".",
            ambiguity=0.35, flags=[],
            assumptions=["Stakeholder salience and vulnerability flags are correct (user-editable)."],
            feature_focus=["prevents_harm", "causes_harm", "preserves_relationships"],
            uncertainties=["Indirect stakeholders may be missing from the list."],
        )


REGISTRY: list[Framework] = [
    Consequentialism(), Deontology(), Justice(), VirtueEthics(), CareEthics(), StakeholderImpactFramework(),
]


def get_framework(fid: str) -> Framework:
    for f in REGISTRY:
        if f.id == fid:
            return f
    raise KeyError(fid)
