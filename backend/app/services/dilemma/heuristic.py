"""Heuristic (offline, deterministic) dilemma understanding: structure, stakeholders, conflicts,
candidate actions. Every rule is a visible keyword rule; outputs record the evidence used."""
from __future__ import annotations

import re

from app.schemas.dilemma import (
    Action, ActionFeatures, Conflict, ContextCues, DilemmaContext, Stakeholder, StructuredDilemma,
)
from app.services.dilemma import lexicon as L
from app.services.dilemma.action_templates import BASE_FEATURES, KIND_ORDER, THEMES


def _norm(text: str) -> str:
    return " " + re.sub(r"\s+", " ", text.lower()) + " "


def hits(text: str, patterns: list[str]) -> list[str]:
    """Patterns are matched at a word start (so 'injur' matches 'injury')."""
    return [p for p in patterns if re.search(r"(?<![a-z])" + re.escape(p.strip()), text)]


def _clip(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---------------------------------------------------------------- domain / theme / cues

def detect_domain(text: str, hint: str = "") -> str:
    if hint and hint in L.DOMAINS:
        return hint
    scores = {d: len(hits(text, kws)) for d, kws in L.DOMAINS.items()}
    best = max(scores, key=lambda d: (scores[d], -list(L.DOMAINS).index(d)))
    return best if scores[best] > 0 else "general"


def detect_theme(text: str, domain: str) -> str:
    conceal = bool(hits(text, L.CONCEAL))
    org = bool(hits(text, ["company", "employer", "organization", "organisation", "firm", "manager",
                           "boss", "corporation", "agency", "factory", "plant"]))
    if domain == "healthcare":
        return "healthcare"
    if domain in ("ai_ethics", "privacy", "technology_governance"):
        return "data_technology"
    if domain == "education":
        return "academic"
    if org and (conceal or hits(text, L.SEVERE) or hits(text, ["fraud", "violat", "illegal"])):
        return "organizational_wrongdoing"
    if domain == "family_social":
        return "personal_relationship"
    if org:
        return "organizational_wrongdoing"
    return "generic"


def compute_cues(text: str) -> ContextCues:
    ev: list[str] = []

    def note(name: str, found: list[str]) -> None:
        if found:
            ev.append(f"{name}: " + ", ".join(sorted(set(f.strip() for f in found))[:6]))

    sev_h, harm_h = hits(text, L.SEVERE), hits(text, L.HARM)
    vul_h, close_h = hits(text, L.VULNERABLE), hits(text, L.CLOSE)
    hedge_h, cert_h = hits(text, L.HEDGES), hits(text, L.CERTAIN)
    legal_h, urg_h, scale_h = hits(text, L.LEGAL), hits(text, L.URGENT), hits(text, L.SCALE)
    for n, f in [("severity", sev_h), ("harm", harm_h), ("vulnerability", vul_h),
                 ("closeness", close_h), ("hedging", hedge_h), ("certainty", cert_h),
                 ("legal", legal_h), ("urgency", urg_h), ("scale", scale_h)]:
        note(n, f)
    return ContextCues(
        severity=round(_clip(0.35 + 0.18 * min(len(sev_h), 3) + 0.06 * min(len(harm_h), 3)), 2),
        vulnerability=round(_clip(0.25 + 0.2 * min(len(vul_h), 3)), 2),
        relational_closeness=round(_clip(0.15 + 0.25 * min(len(close_h), 3)), 2),
        uncertainty=round(_clip(0.3 + 0.1 * min(len(hedge_h), 4) - 0.12 * min(len(cert_h), 2)), 2),
        legal_dimension=round(_clip(0.1 + 0.2 * min(len(legal_h), 4)), 2),
        urgency=round(_clip(0.25 + 0.2 * min(len(urg_h), 3)), 2),
        scale=round(_clip(0.2 + 0.15 * min(len(scale_h), 4)), 2),
        evidence=ev,
    )


# ---------------------------------------------------------------- stakeholders

def extract_stakeholders(text: str, cues: ContextCues, role_hint: str = "") -> list[Stakeholder]:
    t = L.STAKEHOLDER_TEMPLATES["decision_maker"]
    dm_name = f"You ({role_hint})" if role_hint else "You (the decision-maker)"
    out = [Stakeholder(
        id="s1", name=dm_name, category="decision_maker",
        roles=["decision_maker", "primary", "direct"], salience=0.7,
        interests=list(t["interests"]), rights=list(t["rights"]),
        responsibilities=list(t["responsibilities"]), vulnerabilities=list(t["vulnerabilities"]),
        potential_benefits=["acting in line with own values"],
        potential_harms=["career, legal or relationship consequences"],
    )]
    harmful = cues.severity >= 0.5
    for category, name, patterns, roles, vuln in L.STAKEHOLDER_LEXICON:
        found = hits(text, patterns)
        if not found:
            continue
        r = list(roles)
        is_vuln = vuln or (category in ("customers", "public", "students") and harmful
                           and cues.vulnerability >= 0.45)
        if is_vuln and "vulnerable" not in r:
            r.append("vulnerable")
        if is_vuln and "primary" not in r:
            r = ["primary"] + [x for x in r if x != "secondary"]
        tmpl = L.STAKEHOLDER_TEMPLATES.get(category, {})
        sal = _clip(0.35 + 0.1 * len(found) + (0.2 if is_vuln else 0) + (0.1 if "primary" in r else 0))
        benefits, harms = _impacts_for(category)
        out.append(Stakeholder(
            id=f"s{len(out) + 1}", name=name, category=category, roles=r, salience=round(sal, 2),
            interests=list(tmpl.get("interests", [])), rights=list(tmpl.get("rights", [])),
            responsibilities=list(tmpl.get("responsibilities", [])),
            vulnerabilities=list(tmpl.get("vulnerabilities", [])),
            potential_benefits=benefits, potential_harms=harms,
        ))
    if len(out) == 1:  # always surface at least one affected party
        out.append(Stakeholder(
            id="s2", name="Others affected by the decision", category="public",
            roles=["secondary", "indirect"], salience=0.4,
            interests=["not being harmed"], rights=["fair consideration"],
            potential_benefits=["harm avoided"], potential_harms=["harm if concern is ignored"],
        ))
    return out


def _impacts_for(category: str) -> tuple[list[str], list[str]]:
    protected = ("customers", "patients", "public", "children", "environment", "data_subjects", "students")
    if category in protected:
        return (["protection from the threatened harm", "access to honest information"],
                ["continued exposure to harm if nothing is done"])
    if category in ("organization", "management", "shareholders"):
        return (["chance to correct the problem before it escalates"],
                ["financial, legal or reputational damage"])
    if category == "employees":
        return (["safer, more honest workplace"], ["job or income loss if the organization suffers"])
    if category in ("family", "friend"):
        return (["honest relationship", "support"], ["emotional distress", "damaged trust"])
    if category == "regulators":
        return (["accurate information to do their job"], [])
    return ([], [])


# ---------------------------------------------------------------- conflicts

def identify_conflicts(text: str, stakeholders: list[Stakeholder], cues: ContextCues) -> list[Conflict]:
    cats = {s.category for s in stakeholders}
    by_cat = {s.category: s.id for s in stakeholders}
    out: list[Conflict] = []

    def add(ctype: str, title: str, desc: str, between: list[str], intensity: float) -> None:
        out.append(Conflict(id=f"c{len(out) + 1}", type=ctype, title=title, description=desc,
                            between=[b for b in between if b], intensity=round(_clip(intensity), 2)))

    org = cats & {"organization", "management"}
    protected = cats & {"customers", "patients", "public", "children", "environment", "data_subjects"}
    if org and protected and (hits(text, L.SEVERE) or hits(text, L.CONCEAL)):
        add("organizational_loyalty_vs_public_safety", "Organizational loyalty vs. public safety",
            "Duties owed to the organization (loyalty, confidentiality) pull against protecting people exposed to harm.",
            [by_cat.get(sorted(org)[0]), by_cat.get(sorted(protected)[0])], 0.5 + 0.4 * cues.severity)
    if hits(text, L.CONCEAL + ["truth", "tell", "disclose", "honest"]) and (
            cats & {"friend", "family", "employees", "management", "organization"}):
        add("truth_vs_loyalty", "Truth vs. loyalty",
            "Honesty and disclosure conflict with loyalty or confidentiality owed to someone close.",
            ["s1", by_cat.get(next(iter(sorted(cats & {"friend", "family", "employees", "management", "organization"}))))],
            0.4 + 0.4 * cues.relational_closeness)
    if (cats & {"employees", "public", "customers", "community", "students"}) and hits(
            text, ["jobs", "employees", "livelihood", "income", "lose their", "lay off", "layoff", "closure"]):
        add("individual_vs_collective", "Protecting some vs. costs to others",
            "Preventing harm to one group may impose serious costs (e.g., job losses) on another.",
            [by_cat.get("employees", ""), by_cat.get(next(iter(sorted(protected))), "") if protected else ""],
            0.4 + 0.3 * cues.scale)
    if hits(text, L.LEGAL):
        add("legal_vs_moral", "Legal / policy obligations vs. moral obligations",
            "Formal rules, contracts or policies may not align with what seems morally required.",
            ["s1", by_cat.get("regulators", "")], 0.3 + 0.5 * cues.legal_dimension)
    if hits(text, ["cheat", "steal", "mistake", "broke the rule", "violat", "punish", "fire him",
                   "fire her", "fire them", "report him", "report her"]) and hits(
            text, ["struggling", "desperate", "poor", "sick", "first time", "sorry", "family",
                   "single parent", "mental health", "pressure"]):
        add("justice_vs_mercy", "Justice vs. mercy",
            "Holding someone accountable conflicts with compassion for their circumstances.",
            ["s1"], 0.6)
    if hits(text, L.SELF_RISK):
        add("self_interest_vs_social_responsibility", "Personal risk vs. social responsibility",
            "Acting responsibly may carry personal costs (career, reputation, safety) for the decision-maker.",
            ["s1"], 0.5 + 0.3 * cues.severity)
    if hits(text, ["refuse", "refuses", "insist", "consent", "their choice", "his choice", "her choice",
                   "own choice", "autonomy", "independence", "against medical advice"]) and hits(text, ["health", "patient", "safety", "harm", "treatment", "risk"]):
        add("autonomy_vs_beneficence", "Respecting autonomy vs. preventing harm",
            "A person's own choices conflict with protecting their (or others') wellbeing.",
            ["s1"], 0.6)
    if hits(text, ["privacy", "personal data", "confidential", "surveil", "monitor", "personal information"]) and hits(
            text, L.SEVERE + ["threat", "risk", "danger"]):
        add("privacy_vs_safety", "Privacy vs. safety",
            "Protecting personal information conflicts with preventing harm.",
            [by_cat.get("data_subjects", "s1")], 0.55)
    if hits(text, ["future", "long term", "long-term", "years", "eventually", "later"]) or (
            out and any(c.type == "individual_vs_collective" for c in out)):
        add("short_vs_long_term", "Short-term costs vs. long-term consequences",
            "The option that minimises immediate disruption may create larger long-term harms (or vice versa).",
            [], 0.35 + 0.2 * cues.severity)
    if not out or not any(c.type == "duty_vs_consequence" for c in out):
        add("duty_vs_consequence", "Duty vs. consequences",
            "What one's role or principles require may differ from what produces the best overall outcome.",
            ["s1"], 0.45)
    return out


# ---------------------------------------------------------------- actions

def features_for(kind: str, overrides: dict[str, float] | None = None,
                 cues: ContextCues | None = None) -> ActionFeatures:
    base = dict(BASE_FEATURES.get(kind, {}))
    base.update(overrides or {})
    if cues is not None and kind in ("direct", "escalate_external"):
        # broad, public action has larger collateral impact when many people are involved
        base["causes_harm"] = _clip(base.get("causes_harm", 0.5) + 0.1 * (cues.scale - 0.4))
    return ActionFeatures(**{k: round(v, 3) for k, v in base.items()}) if base else ActionFeatures()


def generate_actions(theme: str, cues: ContextCues) -> list[Action]:
    tmpl = THEMES.get(theme, THEMES["generic"])
    return [
        Action(id=f"a{i + 1}", label=tmpl[k][0], description=tmpl[k][1], kind=k,  # type: ignore[arg-type]
               features=features_for(k, tmpl[k][2], cues))
        for i, k in enumerate(KIND_ORDER)
    ]


# ---------------------------------------------------------------- full structuring

def _summary(text: str, conflicts: list[Conflict]) -> str:
    first = re.split(r"(?<=[.!?])\s+", text.strip())[0]
    if len(first) > 220:
        first = first[:217].rsplit(" ", 1)[0] + "..."
    if conflicts:
        top = max(conflicts, key=lambda c: c.intensity)
        return f"{first} Central tension: {top.title.lower()}."
    return first


def structure_dilemma(text: str, context: DilemmaContext | None = None) -> StructuredDilemma:
    context = context or DilemmaContext()
    full = text + (" " + context.additional if context.additional else "")
    nt = _norm(full)
    domain = detect_domain(nt, context.domain)
    theme = detect_theme(nt, domain)
    cues = compute_cues(nt)
    if context.time_pressure.lower() in ("high", "urgent", "immediate"):
        cues.urgency = max(cues.urgency, 0.8)
    stakeholders = extract_stakeholders(nt, cues, context.role)
    conflicts = identify_conflicts(nt, stakeholders, cues)
    actions = generate_actions(theme, cues)

    uncertainties = []
    if cues.uncertainty >= 0.45:
        uncertainties.append("The account contains hedged or unverified claims; facts may be incomplete.")
    uncertainties += [
        "Probability and severity of the threatened harm are not quantified.",
        "How other parties (e.g., management, the person involved) would respond is unknown.",
    ]
    if cues.legal_dimension >= 0.3:
        uncertainties.append("Applicable legal obligations and protections depend on jurisdiction.")
    assumptions = [
        "The facts as described are accurate and complete enough to reason about.",
        "The decision-maker has standing and the practical ability to take each listed action.",
        f"Situation type was inferred as '{theme.replace('_', ' ')}' from keywords (heuristic engine).",
    ]
    constraints = []
    if hits(nt, ["nda", "contract", "confidential", "agreement", "promised"]):
        constraints.append("Confidentiality or contractual commitments may restrict disclosure.")
    if cues.urgency >= 0.6:
        constraints.append("Time pressure limits how much information can be gathered.")
    if hits(nt, L.SELF_RISK):
        constraints.append("Personal risk to the decision-maker (career, retaliation).")
    if cues.legal_dimension >= 0.3:
        constraints.append("Legal or regulatory requirements apply.")

    dims = ["consequences", "duty", "fairness", "virtue", "care", "stakeholder_impact", "dharma"]
    return StructuredDilemma(
        dilemma_text=text, summary=_summary(text, conflicts), domain=domain,
        decision_maker=stakeholders[0].name, context=context, stakeholders=stakeholders,
        actions=actions, conflicts=conflicts, constraints=constraints,
        uncertainties=uncertainties, assumptions=assumptions, ethical_dimensions=dims, cues=cues,
    )
