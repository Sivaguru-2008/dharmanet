"""Automatic evaluation metrics (structural coverage, explanation completeness, consistency).

Metrics for structured DharmaNet outputs read the structured fields. Metrics for free-text
baselines use transparent keyword detectors (documented as a weak proxy in docs/evaluation.md).
"""
from __future__ import annotations

import re
import statistics

from app.schemas.analysis import AnalysisResult
from app.services.dilemma import lexicon as L

EXPLANATION_FIELDS = ("why", "principles", "key_stakeholders", "assumptions", "what_could_change", "disagreements")

CONFLICT_KEYWORDS: dict[str, list[str]] = {
    "duty_vs_consequence": ["duty", "obligation", "consequence", "outcome"],
    "individual_vs_collective": ["collective", "greater good", "many", "community", "jobs"],
    "truth_vs_loyalty": ["loyal", "truth", "honest", "betray"],
    "justice_vs_mercy": ["mercy", "compassion", "punish", "accountab"],
    "short_vs_long_term": ["long-term", "long term", "short-term", "short term", "future"],
    "self_interest_vs_social_responsibility": ["career", "retaliat", "personal risk", "self-interest", "your job"],
    "legal_vs_moral": ["legal", "law", "policy", "regulation"],
    "organizational_loyalty_vs_public_safety": ["public safety", "company", "employer", "loyalty"],
    "autonomy_vs_beneficence": ["autonomy", "consent", "wishes", "independence"],
    "privacy_vs_safety": ["privacy", "data", "confidential"],
}
DIMENSION_KEYWORDS: dict[str, list[str]] = {
    "consequences": ["consequen", "outcome", "utilitarian", "harm", "benefit"],
    "duty": ["duty", "deontolog", "obligation", "rights"],
    "fairness": ["fair", "justice", "equit"],
    "virtue": ["virtue", "character", "integrity", "courage"],
    "care": ["care ethics", "relationship", "empathy", "compassion"],
    "stakeholder_impact": ["stakeholder"],
    "dharma": ["dharma", "gita", "mahabharata"],
}
EXPLANATION_MARKERS: dict[str, list[str]] = {
    "why": ["because", "since", "therefore"],
    "principles": ["principle", "framework", "ethic"],
    "key_stakeholders": ["stakeholder", "affected"],
    "assumptions": ["assum", "if we take"],
    "what_could_change": ["would change", "depends on", "if ", "unless"],
    "disagreements": ["however", "on the other hand", "disagree", "alternatively", "tension"],
}


def _ratio(found: set[str], expected: list[str]) -> float:
    return len(found & set(expected)) / len(expected) if expected else 1.0


def structured_metrics(r: AnalysisResult, case: dict) -> dict:
    cats = {s.category for s in r.structured.stakeholders}
    types = {c.type for c in r.structured.conflicts}
    exp = r.explanation.model_dump()
    filled = sum(1 for f in EXPLANATION_FIELDS if exp.get(f))
    labels = {a.id: a for a in r.structured.actions}
    top = labels[r.matrix.recommendation.action_id]
    return {
        "stakeholder_coverage": round(_ratio(cats, case["expected_stakeholders"]), 3),
        "conflict_coverage": round(_ratio(types, case["expected_conflicts"]), 3),
        "dimension_coverage": round(_ratio(set(r.matrix.dimensions), case["expected_dimensions"]), 3),
        "explanation_completeness": round(filled / len(EXPLANATION_FIELDS), 3),
        "n_actions": len(r.structured.actions),
        "n_stakeholders": len(r.structured.stakeholders),
        "has_uncertainty": all(c.uncertainty > 0 for row in r.matrix.cells.values() for c in row.values()),
        "top_action_kind": top.kind,
        "top_action_label": top.label,
        "clear_preference": r.matrix.recommendation.clear_preference,
        "stability_label": r.sensitivity.label,
        "weight_stability": r.sensitivity.weight_stability,
        "score_stability": r.sensitivity.score_stability,
        "dharma_citations": (sum(len(c.entry_ids) for rd in r.dharma.readings for c in rd.contributions) if r.dharma else 0),
        "dharma_dropped_claims": r.dharma.dropped_claims if r.dharma else 0,
    }


def _hit(text: str, kws: list[str]) -> bool:
    return any(re.search(r"(?<![a-z])" + re.escape(k.strip()), text) for k in kws)


def text_metrics(text: str, case: dict) -> dict:
    """Keyword-proxy metrics for free-text LLM baselines."""
    t = " " + text.lower() + " "
    cats = {cat for cat, _, pats, _, _ in L.STAKEHOLDER_LEXICON if _hit(t, pats)}
    if _hit(t, ["you ", "decision-maker", "decision maker", "yourself"]):
        cats.add("decision_maker")
    types = {k for k, kws in CONFLICT_KEYWORDS.items() if _hit(t, kws)}
    dims = {k for k, kws in DIMENSION_KEYWORDS.items() if _hit(t, kws)}
    expl = sum(1 for k in EXPLANATION_FIELDS if _hit(t, EXPLANATION_MARKERS[k]))
    return {
        "stakeholder_coverage": round(_ratio(cats, case["expected_stakeholders"]), 3),
        "conflict_coverage": round(_ratio(types, case["expected_conflicts"]), 3),
        "dimension_coverage": round(_ratio(dims, case["expected_dimensions"]), 3),
        "explanation_completeness": round(expl / len(EXPLANATION_FIELDS), 3),
        "has_uncertainty": _hit(t, ["uncertain", "unclear", "depends", "might", "may "]),
    }


def consistency(base: AnalysisResult, others: list[AnalysisResult]) -> dict:
    """Agreement of the top action (compared by action *kind*, since labels/ids may differ) and
    score drift of the base leader's kind across perturbed variants."""
    def top_kind(r: AnalysisResult) -> str:
        return next(a.kind for a in r.structured.actions if a.id == r.matrix.recommendation.action_id)

    def score_of(r: AnalysisResult, kind: str) -> float | None:
        ids = [a.id for a in r.structured.actions if a.kind == kind]
        ws = [w.score for w in r.matrix.weighted if w.action_id in ids]
        return ws[0] if ws else None

    k0 = top_kind(base)
    s0 = score_of(base, k0)
    agree = [top_kind(o) == k0 for o in others]
    diffs = [abs(s - s0) for o in others if (s := score_of(o, k0)) is not None and s0 is not None]
    return {
        "top_agreement": round(sum(agree) / len(agree), 3) if agree else None,
        "mean_abs_score_diff": round(statistics.fmean(diffs), 4) if diffs else None,
        "max_abs_score_diff": round(max(diffs), 4) if diffs else None,
    }
