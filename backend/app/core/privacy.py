"""Privacy helpers: logging setup that never records dilemma text, and optional anonymisation."""
from __future__ import annotations

import hashlib
import logging
import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
_URL = re.compile(r"https?://\S+")


def anonymize(text: str) -> str:
    """Redact direct identifiers (emails, phone numbers, URLs). Names are not detected reliably
    and are therefore NOT redacted — this is documented in docs/limitations.md."""
    text = _EMAIL.sub("[EMAIL]", text)
    text = _URL.sub("[URL]", text)
    return _PHONE.sub("[PHONE]", text)


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
