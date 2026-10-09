"""Retrieval over the Dharma KB.

Default: deterministic in-process lexical retriever (TF-IDF cosine + keyword + tag overlap).
The KB is small and retrieval must be reproducible, so no external vector DB is required.
Implement `Retriever` to plug in an embedding/Qdrant retriever later.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Protocol

from app.schemas.dharma import KnowledgeBase, RetrievedEntry

_TOKEN = re.compile(r"[a-z][a-z\-']+")
_STOP = set("""a an the and or of to in on for with is are was were be been being it its this that these those
as at by from but not no nor so if then than too very can could should would may might must will shall do does
did done have has had i me my we our you your he him his she her they them their what which who whom whose
when where why how all any each few more most other some such only own same just into over under again further
once here there about above below up down out off""".split())


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP and len(t) > 2]


class Retriever(Protocol):
    def retrieve(self, query: str, tags: list[str], k: int) -> list[RetrievedEntry]: ...


class LexicalRetriever:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.docs: dict[str, Counter] = {}
        for e in kb.entries:
            text = " ".join([e.concept, e.paraphrase, e.interpretation, " ".join(e.keywords * 2),
                             " ".join(e.applicability).replace("_", " "), " ".join(e.ethical_dimension)])
            self.docs[e.id] = Counter(tokenize(text))
        n = len(self.docs)
        df = Counter(t for c in self.docs.values() for t in c)
        self.idf = {t: math.log((1 + n) / (1 + d)) + 1 for t, d in df.items()}
        self.vecs = {i: self._vec(c) for i, c in self.docs.items()}

    def _vec(self, counts: Counter) -> dict[str, float]:
        v = {t: (1 + math.log(c)) * self.idf.get(t, 1.0) for t, c in counts.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def retrieve(self, query: str, tags: list[str], k: int = 10) -> list[RetrievedEntry]:
        q = self._vec(Counter(tokenize(query)))
        ql = query.lower()
        tagset = set(tags)
        results = []
        for e in self.kb.entries:
            dv = self.vecs[e.id]
            cos = sum(w * dv.get(t, 0.0) for t, w in q.items())
            kw = [kw for kw in e.keywords if kw.lower() in ql]
            tag_hits = sorted(tagset & set(e.applicability))
            score = 0.5 * cos + 0.12 * min(len(kw), 3) + 0.15 * min(len(tag_hits), 3)
            if score <= 0.05:
                continue
            results.append(RetrievedEntry(
                entry_id=e.id, concept=e.concept, citation=e.citation,
                relevance=round(min(1.0, score), 3),
                matched_on=[f"keyword:{x}" for x in kw[:3]] + [f"tag:{x}" for x in tag_hits[:3]],
            ))
        results.sort(key=lambda r: (-r.relevance, r.entry_id))
        return results[:k]
