# API

Base path `/api`. Interactive OpenAPI docs at `http://localhost:8000/docs`. If `DHARMANET_API_TOKEN` is set, every
route except `/health` and `/meta` requires `Authorization: Bearer <token>`. Per-IP rate limit: `DHARMANET_RATE_LIMIT_PER_MINUTE`.

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/health` | — | `{status}` |
| GET | `/meta` | — | versions, provider, frameworks, default weights, disclaimer |
| POST | `/analyses` | `{dilemma (20–8000 chars), context?: {role, domain, cultural_context, time_pressure, additional}, weights?: {values: {dim: w}}, include_dharma?: bool}` | `AnalysisResult` |
| GET | `/analyses?limit=50` | — | `AnalysisSummary[]` |
| GET | `/analyses/{id}` | — | `AnalysisResult` |
| DELETE | `/analyses/{id}` | — | deletes run and child records |
| POST | `/analyses/{id}/rescore` | `{weights: {values}}` | `AnalysisResult` (deterministic; stored as current scoring) |
| POST | `/analyses/{id}/revise` | `{stakeholders?, actions?, assumptions?, additional_context?, weights?}` | new `AnalysisResult` with `parent_id` |
| POST | `/analyses/{id}/decision` | `{choice: accept\|alternative\|modify\|reject, action_id?, note?}` | recorded decision (never executed) |
| POST | `/analyses/{id}/feedback` | `{useful?, ratings: {item: 1–5}, comment?}` | `{recorded}` |
| GET | `/analyses/{id}/export` | — | research-log record (see below) |
| GET | `/knowledge?q=` | — | `KBEntry[]` (all, or retrieval-ranked) |

Dimensions: `consequences, duty, fairness, virtue, care, stakeholder_impact, dharma`.

`AnalysisResult` fields: `id, parent_id, created_at, versions, provider, structured, evaluations[], dharma, matrix,
sensitivity, explanation, comparison[], fallbacks[], include_dharma, seed, disclaimer, decision`. Schemas:
`backend/app/schemas/`; TypeScript mirror: `frontend/types/api.ts`.

Export record keys: `analysis_id, parent_id, timestamp, dilemma, context, stakeholders, conflicts, actions,
framework_scores, dharma_analysis, weights, ranking, equal_weight_ranking, recommendation, uncertainty, sensitivity,
explanation, model, versions, seed, fallbacks, duration_ms, decision, feedback`.

Errors: 401 (auth), 404 (unknown id), 413 (too long), 422 (validation), 429 (rate limit).
