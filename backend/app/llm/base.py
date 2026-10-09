"""LLM provider abstraction. Swap providers via DHARMANET_LLM_PROVIDER without touching the pipeline."""
from __future__ import annotations

from typing import Protocol

import httpx

from app.core.config import Settings


class LLMError(RuntimeError):
    pass


class LLMProvider(Protocol):
    name: str
    model: str

    def complete(self, system: str, user: str) -> str: ...


class GeminiProvider:
    name = "gemini"

    def __init__(self, s: Settings):
        if not s.llm_api_key:
            raise LLMError("DHARMANET_LLM_API_KEY is required for gemini")
        self.model = s.llm_model or "gemini-2.0-flash"
        self._key, self._timeout, self._temp = s.llm_api_key, s.llm_timeout_s, s.llm_temperature

    def complete(self, system: str, user: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": self._temp, "responseMimeType": "application/json"},
        }
        try:  # key goes in a header, never in the URL
            r = httpx.post(url, json=body, headers={"x-goog-api-key": self._key}, timeout=self._timeout)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError) as e:
            raise LLMError(f"gemini request failed: {type(e).__name__}") from e


class OpenAICompatibleProvider:
    """Works with OpenAI and any OpenAI-compatible server (Ollama, LM Studio, vLLM, OpenRouter...)."""
    name = "openai_compatible"

    def __init__(self, s: Settings):
        if not s.llm_model:
            raise LLMError("DHARMANET_LLM_MODEL is required for openai_compatible")
        self.model = s.llm_model
        self._base = s.llm_base_url.rstrip("/")
        self._key, self._timeout, self._temp = s.llm_api_key, s.llm_timeout_s, s.llm_temperature

    def complete(self, system: str, user: str) -> str:
        headers = {"Authorization": f"Bearer {self._key}"} if self._key else {}
        body = {"model": self.model, "temperature": self._temp,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "response_format": {"type": "json_object"}}
        try:
            r = httpx.post(f"{self._base}/chat/completions", json=body, headers=headers, timeout=self._timeout)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError) as e:
            raise LLMError(f"openai-compatible request failed: {type(e).__name__}") from e


def make_provider(s: Settings) -> LLMProvider | None:
    """Returns None for the offline heuristic engine."""
    p = s.llm_provider.lower()
    if p == "heuristic":
        return None
    if p == "gemini":
        return GeminiProvider(s)
    if p in ("openai", "openai_compatible", "ollama"):
        return OpenAICompatibleProvider(s)
    raise LLMError(f"unknown provider {s.llm_provider!r}")
