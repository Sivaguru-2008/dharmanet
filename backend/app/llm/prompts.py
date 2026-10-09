"""Versioned prompt registry. One prompt per pipeline stage (no monolithic prompt).
Each prompt's SHA-256 prefix is recorded on every LLM-backed run for reproducibility."""
from __future__ import annotations

import hashlib
from string import Template

from app.core.versions import PROMPT_VERSION

_COMMON = """
Rules:
- Output a single JSON object only, matching the schema exactly.
- Do not claim the analysis is objectively correct. Do not invent facts beyond the dilemma; record assumptions instead.
- Scores are 0-10. "uncertainty" is a ± half-width on that scale (0-5). "confidence" is 0-1 and is a model estimate, not a probability.
"""

PROMPTS: dict[str, str] = {
    "dilemma_extraction": """Structure the following ethical dilemma.
Dilemma: $dilemma
Context: $context

Return JSON: {"summary": str (<=2 sentences, neutral), "domain": one of [healthcare, workplace, business, education,
ai_ethics, privacy, environment, public_policy, family_social, professional, technology_governance, general],
"decision_maker": str, "constraints": [str], "uncertainties": [str], "assumptions": [str],
"cues": {"severity","vulnerability","relational_closeness","uncertainty","legal_dimension","urgency","scale": each 0-1}}
""" + _COMMON,

    "stakeholder_extraction": """Identify ALL stakeholders in this dilemma, including the decision-maker, indirect and vulnerable parties.
Dilemma: $dilemma
Summary: $summary

Return JSON: {"stakeholders": [{"name": str, "category": one of [decision_maker, organization, management, employees,
customers, patients, public, regulators, children, family, friend, students, shareholders, environment, data_subjects, other],
"roles": subset of [primary, secondary, vulnerable, decision_maker, direct, indirect], "interests": [str], "rights": [str],
"responsibilities": [str], "vulnerabilities": [str], "potential_benefits": [str], "potential_harms": [str], "salience": 0-1}]}
The first stakeholder must be the decision-maker.
""" + _COMMON,

    "conflict_identification": """Identify the ethical conflicts (competing duties/values) in this dilemma.
Dilemma: $dilemma
Stakeholders: $stakeholders

Return JSON: {"conflicts": [{"type": one of [duty_vs_consequence, individual_vs_collective, truth_vs_loyalty,
justice_vs_mercy, short_vs_long_term, self_interest_vs_social_responsibility, legal_vs_moral,
organizational_loyalty_vs_public_safety, autonomy_vs_beneficence, privacy_vs_safety, other], "title": str,
"description": str, "between": [stakeholder names], "intensity": 0-1}]}
""" + _COMMON,

    "action_generation": """Generate 6-8 distinct, plausible candidate actions for the decision-maker. You MUST include at least
one of each kind: direct, escalate_internal, escalate_external, compromise, gather_info, delay, status_quo.
Dilemma: $dilemma
Conflicts: $conflicts

For each action estimate interpretable 0-1 features: prevents_harm, causes_harm (collateral), honesty, role_duty,
due_process, protects_vulnerable, preserves_relationships, self_interest, reversibility, information_gain, timeliness, courage.
Return JSON: {"actions": [{"label": str (<=8 words), "description": str, "kind": str, "features": {...}}]}
""" + _COMMON,

    "framework_evaluation": """You are evaluating actions using ONE ethical framework only: $framework_name.
Definition: $definition
Guiding principle: $principle
Key questions: $questions
Do not use or mention other frameworks.

Dilemma: $dilemma
Stakeholders: $stakeholders
Actions (id: label - description):
$actions

Return JSON: {"scores": [{"action_id": str, "score": 0-10, "uncertainty": 0-5, "confidence": 0-1, "rationale": str (<=3 sentences),
"assumptions": [str], "strengths": [str], "weaknesses": [str], "uncertainties": [str]}]}  — one entry per action id.
""" + _COMMON,

    "dharma_evaluation": """Provide a Dharma-inspired reading of each action, grounded ONLY in the knowledge-base entries below.
Every contribution must cite one or more entry ids from the list; claims citing anything else will be discarded.
Do not quote scripture beyond the given paraphrases and do not invent verses. Present this as one interpretation, not religious authority.
Svadharma must be read as role/commitment-based responsibility, never by birth or caste.

Dilemma: $dilemma
Actions:
$actions
Knowledge-base entries (id | citation | concept | paraphrase | interpretation):
$entries

Return JSON: {"readings": [{"action_id": str, "score": 0-10, "uncertainty": 0-5, "confidence": 0-1, "interpretation": str,
"contributions": [{"concept": str, "entry_ids": [str], "effect": -3..3, "note": str}], "limitations": [str]}]}
""" + _COMMON,

    # --- evaluation baselines (used only by evaluation/run_benchmark.py) ---
    "baseline_plain": "Analyze this ethical dilemma.\n\n$dilemma\n\nRespond as JSON: {\"analysis\": str, \"recommendation\": str}",
    "baseline_single_framework": ("Analyze this ethical dilemma using consequentialism.\n\n$dilemma\n\n"
                                  "Respond as JSON: {\"analysis\": str, \"recommendation\": str}"),
    "baseline_multi_framework": ("Analyze this ethical dilemma using consequentialism, deontology, justice, virtue ethics and "
                                 "care ethics. Identify stakeholders and conflicts, compare several options.\n\n$dilemma\n\n"
                                 "Respond as JSON: {\"analysis\": str, \"recommendation\": str}"),
}


def render(name: str, **kwargs: str) -> str:
    return Template(PROMPTS[name]).safe_substitute(**kwargs)


def prompt_hashes() -> dict[str, str]:
    return {k: f"{PROMPT_VERSION}:{hashlib.sha256(v.encode()).hexdigest()[:12]}" for k, v in PROMPTS.items()}
