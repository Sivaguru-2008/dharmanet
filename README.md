# DharmaNet

**An Explainable Multi-Framework AI System for Culturally Contextualized Ethical Decision Support**

> DharmaNet is an AI-assisted ethical decision-support system. It does not determine objectively correct moral
> decisions and does not replace human judgment, professional advice, institutional policies, or legal requirements.
> Its Dharma-inspired analysis represents a computational interpretation of selected philosophical concepts and should
> not be treated as definitive religious authority.

## Problem & motivation

Asking an LLM "what should I do?" gives a single fluent answer whose reasoning, assumptions, and sensitivity to
wording are hidden. Ethics frameworks give principles but rarely an interactive tool. DharmaNet tests whether a
**structured, explainable, multi-framework pipeline** — with a clearly separated, source-grounded perspective drawn from
the Bhagavad Gita and Mahābhārata — gives more transparent, consistent, and human-controllable support.

```
LLM / heuristic engine = interpretation      Ethical frameworks = structured reasoning
Deterministic code     = scoring & ranking   RAG over cited KB  = philosophical grounding
Human                  = final authority
```

## What it does

1. Structures a free-text dilemma: stakeholders (editable), conflicts, constraints, uncertainties, assumptions.
2. Generates ≥7 candidate actions (direct, internal/external escalation, compromise, information-gathering, delay, status quo); the user can add or remove actions.
3. Scores every action on 7 dimensions — consequences, duty, fairness, virtue, care, stakeholder impact, Dharma-inspired — each cell with rationale, principle, assumptions, ±, model-estimated confidence and disagreement.
4. The Dharma layer retrieves knowledge-base entries and cites one for every claim; a validator drops uncited claims.
5. Deterministic aggregation with user weights *and* equal weights; exact weight-flip thresholds; Monte-Carlo stability → **Stable / Moderately Sensitive / Highly Sensitive**; "no clear preference" when options are within uncertainty.
6. Explanation (why / principles / who / assumptions / what could change / disagreement) + structured reasoning trace (never hidden chain-of-thought).
7. Side-by-side comparison, then a human decision screen (accept / alternative / modify / reject). Nothing is executed.
8. Every run is persisted with versions, weights, seed and model, and is exportable as a research-log record.

## Architecture

See [docs/architecture.md](docs/architecture.md) and the full [master plan](docs/DHARMANET_MASTER_PLAN.md).

```
frontend/  Next.js 15 + TypeScript + Tailwind (proxies /api → backend)
backend/   FastAPI · Pydantic · SQLAlchemy (SQLite default, PostgreSQL in Docker)
  app/services/dilemma      structuring, stakeholders, conflicts, actions (heuristic engine)
  app/services/ethics       6 isolated framework evaluators (registry, pluggable)
  app/services/dharma       KB retrieval → grounded concept rules → citation validator
  app/services/decision     deterministic aggregation, ranking, sensitivity
  app/services/explanation  explanation, trace, comparison
  app/llm                   provider abstraction (Gemini, OpenAI-compatible incl. Ollama), prompts, structured output
knowledge/  dharma_kb.json (versioned, paraphrase-only, cited)
evaluation/ benchmark (22 cases), paraphrases, runner, results, user-study protocol
```

## Running locally

Requirements: Python 3.10+, Node 20+.

```bash
python -m venv backend/.venv
```
```bash
backend/.venv/Scripts/pip install -r backend/requirements.txt
```
(on Linux/macOS use `backend/.venv/bin/...`)

```bash
backend/.venv/Scripts/python -m uvicorn app.main:create_app --factory --app-dir backend --port 8000
```
```bash
npm --prefix frontend install
```
```bash
npm --prefix frontend run dev
```

Open http://localhost:3000. API docs: http://localhost:8000/docs.

### Docker

```bash
docker compose up --build
```
Runs PostgreSQL, the backend (port 8000) and the frontend (port 3000). See [docs/deployment.md](docs/deployment.md).

## Environment variables

Copy `.env.example` to `.env`. Key settings (all prefixed `DHARMANET_`):

| Variable | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER` | `heuristic` | `heuristic` (offline) · `gemini` · `openai_compatible` |
| `LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL` | — | LLM settings (Ollama: base URL `http://localhost:11434/v1`) |
| `DATABASE_URL` | SQLite file in `backend/` | SQLAlchemy URL |
| `API_TOKEN` | empty | if set, `/api` requires a bearer token |
| `RATE_LIMIT_PER_MINUTE` | 60 | per-IP limit |
| `STORE_DILEMMA_TEXT` / `ANONYMIZE_INPUT` | true / false | privacy controls |

Secrets are read only from the environment; `.env` is git-ignored.

## The two engines — read this

With no LLM configured, DharmaNet runs a **transparent heuristic engine**: keyword rules for structuring and
published formulas over interpretable action features. It is reproducible and fully testable, but **it does not
understand language** (e.g. it ignores "the problem might not be real after all"). With an LLM provider, the semantic
stages (extraction, framework judgments, Dharma reading) use per-stage prompts with schema validation, retry, repair,
and per-stage fallback to the heuristic engine (recorded on the run). Aggregation, ranking and sensitivity are always
deterministic code.

## Example

Input: *"I discovered that my company is hiding a serious safety issue in one of its products. Reporting it may protect
customers but could cause hundreds of employees to lose their jobs, and I might lose my job too."*

Heuristic-engine output at default weights: *Escalate internally with a deadline* (6.86 ± 0.72) and *Report to the
regulator* (6.66 ± 0.74) are **within uncertainty — no clear preference**. Internal escalation leads or near-ties on
most dimensions, while virtue clearly favours public disclosure (6.9 vs 6.5). Stability: Highly Sensitive (driven by
score uncertainty). Lowering the threshold for "disagreement" would also surface fairness and care near-ties.

## Evaluation

```bash
backend/.venv/Scripts/python evaluation/run_benchmark.py
```
Produces `evaluation/results.json`, `results.csv`, `report.md`. LLM baselines are marked **NOT YET EVALUATED**
until a provider is configured; the human study is **NOT YET EVALUATED**. See [docs/evaluation.md](docs/evaluation.md).

Tests: `backend/.venv/Scripts/python -m pytest -c backend/pytest.ini --rootdir backend backend` (67 tests).

## Limitations

See [docs/limitations.md](docs/limitations.md). In short: heuristic engine is shallow; scores are not calibrated;
benchmark annotations are author-written; the knowledge base awaits scholarly review; no user study yet.

## Documentation

[architecture](docs/architecture.md) · [research](docs/research.md) · [ethical frameworks](docs/ethical-frameworks.md) ·
[dharma framework](docs/dharma-framework.md) · [API](docs/api.md) · [evaluation](docs/evaluation.md) ·
[deployment](docs/deployment.md) · [limitations](docs/limitations.md)
