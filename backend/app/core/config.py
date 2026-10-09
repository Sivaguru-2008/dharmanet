"""Runtime configuration loaded from environment / .env (never from source code)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DHARMANET_",
        env_file=(str(REPO_ROOT / ".env"), str(BACKEND_ROOT / ".env")),
        extra="ignore",
    )

    # LLM: "heuristic" (offline, deterministic), "gemini", "openai_compatible"
    llm_provider: str = "heuristic"
    llm_model: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_timeout_s: float = 60.0
    llm_max_retries: int = 2
    llm_temperature: float = 0.2

    database_url: str = f"sqlite:///{(BACKEND_ROOT / 'dharmanet.db').as_posix()}"
    knowledge_path: str = str(REPO_ROOT / "knowledge" / "dharma_kb.json")

    # API hardening
    api_token: str = ""  # if set, all /api routes except health/meta require "Authorization: Bearer <token>"
    cors_origins: str = "http://localhost:3005,http://127.0.0.1:3005,http://localhost:3000,http://127.0.0.1:3000"
    rate_limit_per_minute: int = 60
    max_dilemma_chars: int = 8000

    # Privacy
    store_dilemma_text: bool = True
    anonymize_input: bool = False
    log_level: str = "INFO"

    sensitivity_samples: int = 2000
    sensitivity_seed: int = 7


@lru_cache
def get_settings() -> Settings:
    return Settings()
