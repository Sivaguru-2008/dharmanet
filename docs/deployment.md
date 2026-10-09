# Deployment

## Local (no Docker)

See README → Running locally. Backend defaults to SQLite at `backend/dharmanet.db`. The frontend proxies `/api/*` to
`BACKEND_URL` (default `http://127.0.0.1:8000`), so the browser never calls the backend directly.

## Docker Compose

```bash
docker compose up --build
```

| Service | Image | Port | Notes |
|---|---|---|---|
| postgres | postgres:16-alpine | internal | dev credentials in compose file — change for any shared deployment |
| backend | `docker/backend.Dockerfile` | 8000 | non-root user; reads `.env` if present |
| frontend | `docker/frontend.Dockerfile` | 3000 | Next.js standalone; `BACKEND_URL` is a **build** argument (rewrites resolve at build time) |

## Using an LLM

```bash
DHARMANET_LLM_PROVIDER=gemini
DHARMANET_LLM_MODEL=gemini-2.0-flash
DHARMANET_LLM_API_KEY=...
```
or a local model through Ollama:
```bash
DHARMANET_LLM_PROVIDER=openai_compatible
DHARMANET_LLM_MODEL=llama3.1
DHARMANET_LLM_BASE_URL=http://localhost:11434/v1
```
(From inside Docker use `http://host.docker.internal:11434/v1`.)

## Hardening checklist for anything beyond localhost
* Set `DHARMANET_API_TOKEN`, a real PostgreSQL password, and restrict `DHARMANET_CORS_ORIGINS`.
* Put a TLS-terminating reverse proxy in front; move rate limiting to the proxy or a shared store.
* Decide on `DHARMANET_STORE_DILEMMA_TEXT` / `ANONYMIZE_INPUT` and a retention policy; dilemmas are sensitive.
* Run `docker compose build` and the test suite in CI before release.
