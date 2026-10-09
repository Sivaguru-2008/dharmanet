"""Shared app state, auth and rate limiting."""
from __future__ import annotations

import hmac
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request

from app.core.config import Settings
from app.models.repository import Repository
from app.schemas.dharma import KnowledgeBase
from app.services.pipeline import AnalysisPipeline


@dataclass
class AppState:
    settings: Settings
    kb: KnowledgeBase
    pipeline: AnalysisPipeline
    repo: Repository


def get_state(request: Request) -> AppState:
    return request.app.state.dharmanet


class RateLimiter:
    """Sliding-window limiter per client IP (in-memory; use a shared store such as Redis when scaling out)."""

    def __init__(self, per_minute: int):
        self.per_minute = per_minute
        self.hits: dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def check(self, key: str) -> bool:
        now = time.monotonic()
        with self.lock:
            q = self.hits[key]
            while q and now - q[0] > 60:
                q.popleft()
            if len(q) >= self.per_minute:
                return False
            q.append(now)
            return True


def require_auth(request: Request, state: AppState = Depends(get_state)) -> None:
    token = state.settings.api_token
    if not token:
        return
    header = request.headers.get("authorization", "")
    if not hmac.compare_digest(header, f"Bearer {token}"):
        raise HTTPException(status_code=401, detail="invalid or missing bearer token")
