# DharmaNet — Evaluation Report

Generated 2026-10-05T04:40:38.797324+00:00 · 22 benchmark cases · runtime 14.8 s

**Engine:** `heuristic` / `dharmanet-heuristic-0.1` — Offline transparent keyword/rule engine — reproducible, but it does not understand language like an LLM. Configure an LLM provider for richer semantic analysis.

> **Read this first.** These are automatic, structure-level metrics computed against *author-written* annotations (not expert annotations). They measure coverage and consistency, **not** moral correctness. Because the engine is the offline heuristic engine, high consistency partly reflects its deterministic, keyword-based design rather than robust understanding. No result here supports a claim of superiority over LLM baselines unless those baselines were actually run.

## Baseline comparison (mean over cases)

| Condition | Stakeholder cov. | Conflict cov. | Dimension cov. | Explanation compl. | n |
|---|---:|---:|---:|---:|---:|
| B1 Plain LLM | NOT YET EVALUATED | | | | 0 |
| B2 LLM + single framework | NOT YET EVALUATED | | | | 0 |
| B3 LLM + multiple frameworks | NOT YET EVALUATED | | | | 0 |
| B4 DharmaNet w/o Dharma | 0.730 | 0.439 | 1.000 | 1.000 | 22 |
| B5 Full DharmaNet | 0.730 | 0.439 | 1.000 | 1.000 | 22 |

Dimension coverage is 1.0 by construction for B4/B5 (every framework is always evaluated); it is informative only for free-text baselines. Free-text baselines are scored with keyword proxies (see docs/evaluation.md).

## Recommendation stability (full DharmaNet, default weights)

| Stable | Moderately Sensitive | Highly Sensitive |
|---:|---:|---:|
| 0 | 8 | 14 |

## Robustness (full DharmaNet)

Top-action agreement compares the leading action *type* between the original and perturbed input; score difference is the change in that action's weighted score (0-10).

| Perturbation | Cases | Top-action agreement | Mean abs. score diff |
|---|---:|---:|---:|
| irrelevant name | 22 | 1.000 | 0.007 |
| irrelevant context | 22 | 1.000 | 0.003 |
| contradictory info | 22 | 1.000 | 0.017 |
| missing info | 22 | 0.955 | 0.061 |
| paraphrase | 6 | 1.000 | 0.052 |

Irrelevant-name and irrelevant-context perturbations *should* not change results; contradictory or missing information *may* legitimately change them (reported for transparency, not as errors).

Model-change robustness: NOT YET EVALUATED (requires runs with ≥2 LLM providers).

## Dharma-layer ablation

Adding the Dharma-inspired dimension changed the top-ranked action in 0 of 22 cases at default weights (Dharma weight 10%).

## Human evaluation

NOT YET EVALUATED. Protocol: evaluation/user_study/protocol.md.

## Versions

```json
{
  "system_version": "0.1.0",
  "analysis_version": "0.1.0",
  "framework_version": "0.1",
  "scoring_version": "0.1",
  "sensitivity_version": "0.1",
  "prompt_version": "0.1",
  "heuristic_engine_version": "0.1",
  "dharma_kb_version": "0.1"
}
```
