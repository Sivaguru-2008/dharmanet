# Ethical frameworks (v0.1)

Each framework owns one dimension, is evaluated **independently** (it receives only the structured dilemma), and
returns per action: score 0–10, ± (model-estimated), confidence (model-estimated, not a probability), rationale,
principle, assumptions, strengths, weaknesses, uncertainties, flags. "Potential disagreement" is filled afterwards by
deterministic code naming the dimension that diverges most for the same action (≥1.5 points).

## Action features (heuristic engine)

Each candidate action carries twelve interpretable 0–1 features. Base profiles by action kind
(`services/dilemma/action_templates.py`; themes may override individual values):

| kind | prevents_harm | causes_harm | honesty | role_duty | due_process | protects_vuln | relationships | self_interest | reversibility | info_gain | timeliness | courage |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| direct | .85 | .55 | .90 | .75 | .50 | .85 | .30 | .20 | .20 | .20 | .95 | .90 |
| escalate_internal | .65 | .30 | .75 | .85 | .85 | .60 | .65 | .35 | .70 | .50 | .60 | .60 |
| escalate_external | .80 | .50 | .85 | .70 | .75 | .80 | .25 | .25 | .25 | .35 | .80 | .85 |
| compromise | .70 | .35 | .70 | .70 | .70 | .75 | .60 | .30 | .55 | .45 | .65 | .65 |
| gather_info | .35 | .15 | .60 | .60 | .75 | .40 | .70 | .45 | .90 | .95 | .30 | .35 |
| delay | .20 | .10 | .40 | .30 | .50 | .20 | .75 | .70 | .80 | .50 | .10 | .15 |
| status_quo | .05 | .05 | .40 | .20 | .40 | .10 | .80 | .85 | .50 | .10 | .00 | .05 |

These profiles are **authored judgments**, not empirical measurements. They are the main lever of the heuristic engine
and the main threat to its validity (see limitations). With an LLM provider, features and scores are estimated per dilemma.

## Context cues

`severity, vulnerability, relational_closeness, uncertainty, legal_dimension, urgency, scale` ∈ [0,1], computed from
keyword hits (`services/dilemma/lexicon.py`); the evidence words are shown in the UI.

## Formulas (heuristic path; `services/ethics/frameworks.py`)

Notation: `f` = action features, `c` = cues, clip to [0,10].

**Consequentialism** — stakes `S = c.severity·(0.6+0.4·c.vulnerability)`;
`raw = f.prevents·S − (1−f.prevents)·S·0.6 − f.causes·(0.5+0.3·c.scale)·0.8 + 0.15(f.honesty−.5) + 0.1(f.reversibility−.5)·c.uncertainty`;
score = 5 + 6·raw.

**Deontology** — `10·(0.4·role_duty + 0.35·honesty + 0.25·due_process + 0.1·c.legal·(due_process−.5) + 0.15·c.severity·(prevents−.5))`;
−1 and flag `duty_violation:deception_or_concealment` if honesty < 0.3.

**Justice / fairness** — `10·(0.35·protects_vuln + 0.3·due_process + 0.2·(1−causes) + 0.15·honesty + 0.1·c.vulnerability·(protects_vuln−.5))`.

**Virtue** — weighted mean of honesty .25, courage .2, selflessness (1−self_interest) .2, compassion
((protects_vuln+relationships)/2) .2, practical wisdom ((info_gain+reversibility)/2) with weight 0.1+0.15·c.uncertainty.

**Care** — weighted mean of relationships (0.2+0.3·closeness), protects_vuln .35, avoids collateral (1−causes) .2,
reversibility .1, responsiveness (timeliness·(0.5+0.5·vulnerability)) .15.

**Stakeholder impact** — each stakeholder gets an impact ∈ [−1,1] from its category (protected parties: harm
prevention & honesty; institutional: collateral harm, due process; relational: relationships; decision-maker:
self-interest, role integrity; oversight: process & honesty). Score = 5 + 5·(salience-weighted mean, ×1.5 for vulnerable).

**Uncertainty** — `± = 0.5 + 1.5·c.uncertainty + 1.2·ambiguity`; `confidence = clip(0.9 − 0.35·c.uncertainty − 0.3·ambiguity, .3, .9)`,
with framework-specific ambiguity (e.g. consequences: 0.3 + 0.4·(1−reversibility)).

## Aggregation (`services/decision/engine.py`)

Normalised weights `w`; weighted score `Σ w_d·s_d`; propagated ± `sqrt(Σ (w_d·σ_d)²)` (assumes independent errors);
confidence `Σ w_d·conf_d`. Ties broken by action order. A **clear preference** requires
`margin ≥ max(0.3, 0.5·sqrt(σ₁²+σ₂²))`.

Linear compensatory aggregation lets strong scores offset a rights violation; the `duty_violation` flag is surfaced in
the matrix and trace so the user can see it. Non-compensatory rules (vetoes) are future work.

## Sensitivity (`services/decision/sensitivity.py`)

1. **Flip thresholds (exact).** For dimension d, weight t ∈ [0,1], others rescaled proportionally: each action's score is
   linear in t; pairwise line crossings give the exact interval in which the current leader stays first.
2. **Weight stability.** 2000 Dirichlet samples, α = 25·w + 0.3, seeded.
3. **Score stability.** 2000 samples with each cell ~ N(score, (±/2)²), clipped to [0,10], seeded.
Label from min(weight, score stability): ≥0.80 Stable, ≥0.55 Moderately Sensitive, else Highly Sensitive.
