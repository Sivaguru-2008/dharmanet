# Evaluation methodology

## Benchmark (`evaluation/benchmark/dilemmas.json`, v0.1)

22 author-written dilemmas: 11 categories (healthcare, workplace, education, AI ethics, privacy, business, environment,
public policy, family/social, professional responsibility, technology governance) × 2, across difficulty levels
easy / medium / hard / highly conflicting. Each case lists `expected_stakeholders` (categories), `expected_conflicts`
(types) and `expected_dimensions`. **These are author annotations, not expert annotations, and there is no single
correct answer for any case.** Six cases have author-written paraphrases (`paraphrases.json`).

## Conditions

| ID | Condition | Implementation |
|---|---|---|
| B1 | Plain LLM | prompt "Analyze this ethical dilemma." |
| B2 | LLM + single framework | consequentialism-only prompt |
| B3 | LLM + multiple frameworks | five-framework free-text prompt |
| B4 | DharmaNet without Dharma | full pipeline, `include_dharma=False` |
| B5 | Full DharmaNet | full pipeline |

B1–B3 run only when an LLM provider is configured; otherwise they are reported **NOT YET EVALUATED**. For a fair
comparison B4/B5 should use the *same* LLM as B1–B3 (set the provider and rerun).

## Automatic metrics (`backend/app/services/evaluation/metrics.py`)

* **Stakeholder / conflict / dimension coverage** — share of annotated categories present. For B4/B5, read from
  structured output; for free-text baselines, detected with keyword proxies (a weak, lenient proxy — it can credit a
  word mention as coverage, and it can miss paraphrased coverage).
* **Explanation completeness** — share of the six explanation questions answered (structured fields for B4/B5; keyword
  markers for baselines).
* **Recommendation stability** — sensitivity label and stability shares.
* **Consistency under perturbation** (Phase 9) — top-action agreement (by action *type*) and mean absolute change in
  the leader's weighted score for: irrelevant names (4 names), irrelevant context sentence, contradictory information,
  missing information (first sentence only), paraphrase. Names are used only as ethically irrelevant attributes.
* **Dharma ablation** — how often the Dharma dimension changes the top action.
* **Model-change robustness** — NOT YET EVALUATED (requires ≥2 providers).

Run: `backend/.venv/Scripts/python evaluation/run_benchmark.py` → `evaluation/results.json`, `results.csv`, `report.md`.

## Current results (heuristic engine)

See `evaluation/report.md` for the latest generated numbers. Interpretation notes for the v0.1 run:
* Consistency under irrelevant perturbations is near-perfect largely **because the engine is deterministic and
  keyword-based**; this is a property of the design, not evidence of robust understanding.
* Contradictory information ("the problem might not be real") does **not** change results — a known weakness of the
  heuristic engine.
* Conflict coverage against author annotations is moderate (~0.44), showing the conflict lexicon is incomplete.
* Most cases are labelled Highly or Moderately Sensitive, mainly due to score uncertainty: the engine rarely expresses
  false certainty, which is intended, but it also means the recommendation is often a near-tie.
* At 10% weight the Dharma dimension did not change any top action; its contribution is mainly explanatory unless the
  user raises its weight.

## Human evaluation (NOT YET EVALUATED)

Protocol and questionnaire: `evaluation/user_study/protocol.md`, `evaluation/user_study/questionnaire.md`.
Within-subjects comparison of LLM-only vs DharmaNet on usefulness, transparency, trust calibration, explanation
quality, consistency, ease of understanding, cultural relevance, decision confidence, willingness to use (5-point Likert).
