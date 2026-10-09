"""Loads and validates the versioned Dharma knowledge base."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.schemas.dharma import KBEntry, KnowledgeBase


class KnowledgeBaseError(ValueError):
    pass


def load_kb(path: str | Path) -> KnowledgeBase:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    kb = KnowledgeBase.model_validate(data)
    ids = [e.id for e in kb.entries]
    if len(ids) != len(set(ids)):
        raise KnowledgeBaseError("duplicate KB entry ids")
    for e in kb.entries:
        if e.source == "Bhagavad Gita":
            if not (e.chapter and e.verse):
                raise KnowledgeBaseError(f"{e.id}: Gita entries need chapter and verse")
            if not 1 <= int(e.chapter) <= 18:
                raise KnowledgeBaseError(f"{e.id}: Gita has 18 chapters")
        if e.source == "Mahabharata" and not e.chapter:
            raise KnowledgeBaseError(f"{e.id}: Mahabharata entries need a parva")
    return kb


@lru_cache
def get_kb(path: str) -> KnowledgeBase:
    return load_kb(path)


def kb_index(kb: KnowledgeBase) -> dict[str, KBEntry]:
    return {e.id: e for e in kb.entries}
