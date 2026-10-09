import json
from pathlib import Path

import pytest

from app.core.config import REPO_ROOT, Settings
from app.rag.knowledge import load_kb
from app.services.pipeline import AnalysisPipeline

BENCHMARK = json.loads((REPO_ROOT / "evaluation" / "benchmark" / "dilemmas.json").read_text(encoding="utf-8"))["cases"]
WHISTLE = ("I discovered that my company is hiding a serious safety issue in one of its products. Reporting it may "
           "protect customers but could cause hundreds of employees to lose their jobs, and I might lose my job too.")


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(_env_file=None, database_url=f"sqlite:///{(tmp_path / 't.db').as_posix()}",
                    sensitivity_samples=400, rate_limit_per_minute=1000)


@pytest.fixture
def kb(settings):
    return load_kb(settings.knowledge_path)


@pytest.fixture
def pipeline(settings, kb):
    return AnalysisPipeline(settings, kb)


class FakeProvider:
    """Scripted LLM for tests: returns queued responses, or calls a function of the prompt."""
    name, model = "fake", "fake-1"

    def __init__(self, responder):
        self.responder = responder
        self.calls: list[str] = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append(user)
        return self.responder(user)
