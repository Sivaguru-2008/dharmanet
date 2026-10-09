# DharmaNet — Master Plan

**DharmaNet: An Explainable Multi-Framework AI System for Culturally Contextualized Ethical Decision Support**

Status: Phase 0 complete. This file is the single source of truth for the architecture; the
focused docs in `docs/` expand individual sections.

---

## 0. Workspace inspection (2026-10-05)

| Item | Finding |
|---|---|
| Repository | Empty folder, not a git repo → greenfield monorepo |
| Python | 3.10.11 (backend targets 3.10+) |
| Node / npm | 24.13 / 11.6 (frontend: Next.js 15, React 19) |
| Docker | 29.6 (docker-compose for full stack) |
| LLM keys | None present → the system **must run fully offline** |
| Path | Contains spaces and lives under OneDrive → avoid path-sensitive tooling; keep `node_modules`/`.venv` git-ignored |

**Consequence of "no LLM key":** DharmaNet ships with a deterministic, transparent
**heuristic analysis engine** that implements every pipeline stage without an LLM. LLM
providers (Gemini, any OpenAI-compatible API incl. local Ollama/LM Studio/vLLM) plug into the
same stage interfaces. The heuristic engine is labelled as such everywhere; it is a
reproducible reference implementation and test oracle, *not* a claim of semantic understanding.

---

## 1. Research framing

**Research question.** Can an explainable, structured AI ethical decision-support framework that
combines established ethical theories with culturally contextualized Mahābhārata-inspired
reasoning provide more transparent, consistent, and human-controllable ethical decision support
than an unconstrained LLM response?

**What DharmaNet produces:** structured analysis + competing perspectives + uncertainty +
alternatives + explanations. **What it never produces:** a final moral verdict. Final decision → human.

**Candidate contributions** (none claimed as novel until a literature review supports it):
1. Structured multi-framework decision-support architecture.
2. Culturally contextualized (Gita / Mahābhārata-inspired) reasoning layer, grounded in a cited KB.
3. Explainable decision matrix with per-cell rationale, assumptions, confidence, disagreement.
4. Human-controlled recommendation with explicit uncertainty.
5. Weight-sensitivity analysis (exact flip thresholds + Monte-Carlo stability).
6. Benchmark methodology for consistency/transparency of AI ethical reasoning.

**Hypotheses (to be tested, NOT YET EVALUATED):**
- H1 (transparency): DharmaNet outputs answer more of the six explanation questions than baseline LLM output.
- H2 (consistency): DharmaNet's preferred action is more stable under ethically irrelevant perturbations.
- H3 (coverage): DharmaNet identifies more annotated stakeholders/conflicts than baseline.
- H4 (usefulness / trust calibration): users rate DharmaNet higher on usefulness without higher over-trust.
- H5 (cultural relevance): the Dharma layer adds perspectives users judge relevant and not misrepresentative.

---

## 2. Requirements

### Functional
F1 free-text dilemma + optional context → structured dilemma.
F2 stakeholders (primary/secondary/vulnerable/decision-maker/direct/indirect) with interests, rights,
responsibilities, vulnerabilities, benefits, harms; **user-editable**.
F3 conflicts (typed: duty-vs-consequence, truth-vs-loyalty, …).
F4 ≥5 candidate actions incl. compromise, delay, escalation, information-gathering; user can add/remove; none silently dropped.
F5 six framework evaluations + Dharma-inspired evaluation, each cell with score, ±, confidence, rationale, assumptions, principle, disagreement.
F6 weights: equal-weight and user-weighted analyses, live re-ranking.
F7 sensitivity: flip thresholds per dimension, Monte-Carlo weight and score stability, label Stable / Moderately Sensitive / Highly Sensitive.
F8 explanation engine (why / principle / who / assumptions / what-could-change / disagreement) + structured reasoning trace (never hidden CoT).
F9 alternative comparison (strengths, weaknesses, helped/harmed, short/long-term, risks, uncertainty, disagreement, Dharma view).
F10 human decision interface (accept / choose alternative / modify / reject) + feedback; nothing is executed.
F11 history, reproducible run records, research log export.
F12 evaluation harness: baselines, perturbation consistency, report generation.

### Non-functional
Runs locally with zero keys; swappable LLM; deterministic math; schema-validated LLM output
(retry → repair → safe fallback); versioned prompts/frameworks/KB/scoring; privacy-conscious
logging; no secrets in source; rate limiting; optional token auth; tests for the deterministic core.

---

## 3. Architecture

```
            ┌──────────────────────── Frontend (Next.js / TS / Tailwind) ────────────────────────┐
            │ Home · New Dilemma · Analysis(Overview/Matrix/Dharma/Explain/Compare/Sensitivity/   │
            │ Decision) · History · Knowledge                                                      │
            └───────────────────────────────────────┬──────────────────────────────────────────────┘
                                                    │ REST/JSON
┌───────────────────────────────── Backend (FastAPI) ┴──────────────────────────────────────────────┐
│ API gateway: validation · rate limit · optional bearer auth · CORS                                 │
│                                                                                                    │
│ AnalysisPipeline (orchestrator, records trace + fallbacks)                                         │
│  1 DilemmaService ──► 2 StakeholderService ──► 3 ConflictService ──► 4 ActionService               │
│  5 EthicsEngine  (6 isolated FrameworkEvaluators, registry-based, pluggable)                       │
│  6 DharmaEngine  (Retriever over KB ► grounded concept rules / LLM ► citation validator)           │
│  7 DecisionEngine (deterministic: normalise weights, aggregate, rank, uncertainty propagation)     │
│  8 SensitivityEngine (deterministic: flip thresholds, seeded Monte-Carlo)                          │
│  9 ExplanationEngine (structured answers + reasoning trace from recorded pipeline events)          │
│ 10 ComparisonBuilder                                                                               │
│                                                                                                    │
│ Stage backends:  HeuristicBackend (offline, deterministic)  |  LLMBackend (prompts + schemas)      │
│ LLM layer: LLMProvider protocol → Gemini · OpenAI-compatible (OpenAI, Ollama, vLLM…) · Fake(tests) │
│ Structured output: JSON extraction → Pydantic validate → retry → repair → fallback to heuristic    │
│ RAG: KnowledgeBase (JSON, versioned) → Retriever protocol → LexicalRetriever (TF-IDF, default)     │
│ Persistence: SQLAlchemy → SQLite (default) / PostgreSQL (docker)                                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
evaluation/ : benchmark dataset · perturbation generator · baseline runner · metrics · report
```

**Separation of concerns (the defensibility core)**

| Concern | Owner |
|---|---|
| Semantic interpretation (extraction, framework judgements) | LLM *or* heuristic backend |
| Structured reasoning | framework definitions (versioned) |
| Scoring / aggregation / ranking / sensitivity / confidence aggregation | deterministic Python |
| Philosophical grounding | RAG over cited KB + citation validator |
| Final decision | human |

**Vector DB decision.** Default retriever is an in-process TF-IDF + tag-overlap retriever: the KB is
small (tens of records), retrieval must be deterministic for reproducibility, and it needs no
external service. The `Retriever` protocol allows a Qdrant/embedding retriever later; this is
recorded as a deliberate deviation from "Qdrant" in the original brief.

---

## 4. Data model (core schemas — `backend/app/schemas`)

```
StructuredDilemma { summary, dilemma_text, context, domain, decision_maker, stakeholders[], actions[],
                    conflicts[], constraints[], uncertainties[], assumptions[], ethical_dimensions[], cues{} }
Stakeholder { id, name, category, roles[primary|secondary|vulnerable|decision_maker|direct|indirect],
              interests[], rights[], responsibilities[], vulnerabilities[], potential_benefits[],
              potential_harms[], salience 0-1, user_edited }
Action      { id, label, description, kind[direct|escalate_internal|escalate_external|gather_info|
              compromise|delay|status_quo|custom], features{12 attrs 0-1}, user_added }
Conflict    { id, type, description, between[stakeholder ids or values], intensity 0-1 }
DimensionScore { dimension, action_id, score 0-10, uncertainty (±), confidence 0-1,
                 confidence_type="model-estimated", rationale, principle, assumptions[],
                 evidence[], potential_disagreement, strengths[], weaknesses[], citations[] }
FrameworkEvaluation { framework_id, framework_version, scores[DimensionScore], summary }
DharmaEvaluation    { retrieved[ {entry_id, relevance} ], action_readings[ {action_id, score, ±,
                      concept_contributions[{concept, entry_ids, effect, note}], interpretation,
                      limitations[] } ], disclaimer }
DecisionMatrix { dimensions[], actions[], cells[action][dim], weights, weighted[action→{score,±,conf}],
                 ranking[], equal_weight_ranking[], recommendation{action_id, margin, clear_preference} }
Sensitivity { flip_thresholds[dim→{current, stays_top_range[lo,hi], next_action_if_exceeded}],
              weight_stability, score_stability, label, samples, seed }
Explanation { why, principles[], key_stakeholders[], assumptions[], what_could_change[],
              disagreements[], trace[ordered steps] }
AnalysisResult { id, parent_id, versions{}, provider{}, structured, evaluations, dharma, matrix,
                 sensitivity, explanation, comparison, fallbacks[], created_at }
```

Action **features** (0–1, heuristic or LLM-estimated): `prevents_harm, causes_harm, honesty,
role_duty, due_process, protects_vulnerable, preserves_relationships, self_interest,
reversibility, information_gain, timeliness, courage`.

---

## 5. Database schema (SQLAlchemy)

| Table | Key columns |
|---|---|
| users | id, display_name, created_at (auth-ready; anonymous default user) |
| dilemmas | id, user_id, text (nullable if anonymised), text_hash, context JSON, created_at |
| analysis_runs | id, dilemma_id, parent_run_id, status, provider, model, analysis/framework/prompt/kb/scoring versions, weights JSON, input JSON, result JSON, fallbacks JSON, created_at, duration_ms |
| stakeholders | id, run_id, sid, name, category, data JSON, user_edited |
| actions | id, run_id, aid, label, kind, data JSON, user_added |
| ethical_evaluations | id, run_id, framework_id, framework_version, action_aid, score, uncertainty, confidence, data JSON |
| dharma_evaluations | id, run_id, action_aid, score, uncertainty, data JSON |
| decision_matrices | id, run_id, weights JSON, matrix JSON, sensitivity JSON |
| explanations | id, run_id, data JSON |
| feedback | id, run_id, kind (decision/feedback), decision, chosen_action, useful, ratings JSON, comment, created_at |
| knowledge_sources | id, entry_id, concept, source, chapter, verse, data JSON, kb_version |

Every run stores model, prompt versions, framework versions, KB version, scoring version, weights,
seed, input, output, assumptions → reproducible. Human edits create a **new run** linked by `parent_run_id`.

---

## 6. API (prefix `/api`)

| Method | Path | Purpose |
|---|---|---|
| GET | /health | liveness |
| GET | /meta | versions, frameworks, default weights, provider, disclaimer |
| POST | /analyses | run full pipeline `{dilemma, context?, weights?}` |
| GET | /analyses | history (summaries) |
| GET | /analyses/{id} | full result |
| DELETE | /analyses/{id} | delete run (privacy) |
| POST | /analyses/{id}/rescore | deterministic re-rank with new weights (no LLM) |
| POST | /analyses/{id}/revise | human edits (stakeholders/actions/assumptions/context) → new run |
| POST | /analyses/{id}/decision | record human decision |
| POST | /analyses/{id}/feedback | usefulness / ratings |
| GET | /analyses/{id}/export | research-log JSON record |
| GET | /knowledge | KB entries; `?q=` search |

---

## 7. Ethical reasoning model

Seven dimensions: `consequences, duty, fairness, virtue, care, stakeholder_impact, dharma`.
Each framework is a class with `id, version, definition, questions, evaluate()`; evaluators
receive only the structured dilemma — never another framework's output (no contamination).
Default weights: consequences .20, duty .20, fairness .15, virtue .10, care .10, stakeholder .15, dharma .10.

Heuristic scoring formulas are published in `docs/ethical-frameworks.md` and unit-tested.

---

## 8. Dharma knowledge model

`knowledge/dharma_kb.json` (versioned). Record:
```
{ id, concept, sanskrit_term, source, chapter, verse, citation, text_type:"paraphrase",
  paraphrase, interpretation, alternative_interpretations[], ethical_dimension[], applicability[tags],
  keywords[], limitations[], verification_status }
```
Rules: references limited to well-attested Bhagavad Gītā verses and Mahābhārata episodes
cited at *parva* level (verse numbering differs between the BORI Critical Edition and vulgate,
so no verse is invented). Text is **paraphrase written for this project**, never presented as a
translation. Every Dharma claim in output carries `entry_ids`; a validator drops any claim citing
an unknown id. `verification_status` = `needs_scholarly_review` until checked by a scholar.

---

## 9. Evaluation methodology

Conditions: B1 plain LLM · B2 LLM + single framework · B3 LLM + multiple frameworks ·
B4 DharmaNet without Dharma · B5 full DharmaNet. B1–B3 require an LLM provider; without one they
are reported **NOT YET EVALUATED**.

Automatic metrics: stakeholder coverage, conflict coverage, dimension coverage (vs author
annotations — labelled as such, not expert), explanation completeness (6 questions),
recommendation stability (sensitivity), perturbation consistency (top-action agreement,
score variance) under name swaps, irrelevant context, paraphrase, missing info.
Human metrics (Likert user study, protocol in `evaluation/user_study/`): NOT YET EVALUATED.

---

## 10. Phased plan

| Phase | Deliverable | Verification |
|---|---|---|
| 0 | this plan + docs | internal review |
| 1 | monorepo, FastAPI, Next.js, DB, Docker, config, logging, pytest | app boots, tests run |
| 2 | dilemma/stakeholder/conflict/action extraction + endpoints | tests on ≥10 dilemmas |
| 3 | 6 isolated framework evaluators | unit tests |
| 4 | KB, retriever, Dharma engine, citation validator | KB integrity + grounding tests |
| 5 | decision + sensitivity engines | math unit tests |
| 6 | explanation + trace | tests (no free-form CoT fields) |
| 7 | frontend dashboard | build + browser check |
| 8 | evaluation runner + report | generated results files |
| 9 | robustness perturbations | consistency tests |
| 10 | demo scenario | end-to-end in browser |

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| Heuristic engine mistaken for real understanding | labelled in UI, docs, run metadata |
| Scores read as moral truth | ±, confidence type label, disclaimers, stability label, "no clear preference" state |
| Misrepresenting Hindu philosophy / scripture fabrication | paraphrase-only, attested refs, alternative interpretations, limitations, scholar-review flag, caste-reading caveat for svadharma |
| LLM invalid JSON / hallucinated citations | Pydantic validation, retry, repair, citation validator, heuristic fallback |
| Over-trust / automation bias | human decision step, no auto-execution, override buttons |
| Sensitive data in dilemmas | no text in logs, optional anonymisation, delete endpoint, local DB |
| Weight sensitivity hides arbitrariness | sensitivity analysis shown prominently |
| Evaluation circularity (author annotations) | labelled; expert annotation listed as future work |

## 12. Assumptions needing validation
1. A 0–10 per-dimension scale is interpretable for users.
2. Linear weighted aggregation is an acceptable first model (non-compensatory alternatives, e.g. veto on rights violations, are future work; a "duty violation" flag is surfaced instead).
3. Selected Gita concepts are relevant across the benchmark domains.
4. Author-written benchmark annotations are a reasonable proxy until expert annotation.
5. Model-estimated confidence is not calibrated probability.
