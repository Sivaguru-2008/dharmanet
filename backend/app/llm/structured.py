"""Schema-validated LLM calls: extract JSON → Pydantic validate → retry → repair → fail safely.
Arbitrary LLM text is never trusted without validation."""
from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.llm.base import LLMError, LLMProvider

T = TypeVar("T", bound=BaseModel)

SYSTEM = ("You are a component of DharmaNet, an ethical decision-support system. You never claim moral or "
          "religious authority, never invent citations or scripture, and never present a judgment as objectively "
          "correct. Respond ONLY with a single JSON object matching the requested schema.")


class StructuredOutputError(RuntimeError):
    pass


def extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object found")
    depth, in_str, esc = 0, False, False
    for i, ch in enumerate(text[start:], start):
        if in_str:
            esc = (ch == "\\") and not esc
            if ch == '"' and not esc:
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("unbalanced JSON object")


def generate_structured(provider: LLMProvider, prompt: str, schema: type[T], max_retries: int = 2) -> T:
    last_err, last_out = "", ""
    for attempt in range(max_retries + 1):
        if attempt == 0 or not last_out:
            user = prompt
        else:  # repair: show the model its own output and the validation error
            user = (f"{prompt}\n\nYour previous output was invalid.\nError: {last_err[:1500]}\n"
                    f"Previous output (truncated):\n{last_out[:3000]}\n\nReturn a corrected JSON object only.")
        try:
            last_out = provider.complete(SYSTEM, user)
            return schema.model_validate(extract_json(last_out))
        except LLMError as e:
            last_err, last_out = str(e), ""
        except (ValueError, ValidationError) as e:
            last_err = str(e)
    raise StructuredOutputError(f"{schema.__name__}: failed after {max_retries + 1} attempts: {last_err[:300]}")
