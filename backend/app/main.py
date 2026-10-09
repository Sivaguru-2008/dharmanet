"""DharmaNet FastAPI application."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.deps import AppState, RateLimiter
from app.api.routes import public, router
from app.core.config import Settings, get_settings
from app.core.privacy import setup_logging
from app.core.versions import SYSTEM_VERSION
from app.llm.base import make_provider
from app.models.orm import make_session_factory
from app.models.repository import Repository
from app.rag.knowledge import load_kb
from app.services.pipeline import AnalysisPipeline


def create_app(settings: Settings | None = None, provider=None) -> FastAPI:
    s = settings or get_settings()
    setup_logging(s.log_level)
    kb = load_kb(s.knowledge_path)
    prov = provider if provider is not None else make_provider(s)
    repo = Repository(make_session_factory(s.database_url), store_text=s.store_dilemma_text)
    repo.sync_knowledge(kb)

    app = FastAPI(title="DharmaNet API", version=SYSTEM_VERSION,
                  description="Explainable multi-framework ethical decision support. Decision support, not a final moral judgment.")
    app.state.dharmanet = AppState(settings=s, kb=kb, pipeline=AnalysisPipeline(s, kb, prov), repo=repo)
    limiter = RateLimiter(s.rate_limit_per_minute)

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        if request.method != "OPTIONS" and request.url.path.startswith("/api/") and request.url.path != "/api/health":
            key = request.client.host if request.client else "unknown"
            if not limiter.check(key):
                return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        return await call_next(request)

    app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in s.cors_origins.split(",") if o.strip()],
                       allow_methods=["*"], allow_headers=["*"])
    app.include_router(public)
    app.include_router(router)
    return app
# Run with: uvicorn app.main:create_app --factory
