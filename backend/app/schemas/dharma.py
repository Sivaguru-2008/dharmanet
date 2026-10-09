"""Dharma knowledge-base records and Dharma-inspired evaluation outputs."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class KBEntry(BaseModel):
    id: str
    concept: str
    sanskrit_term: str = ""
    source: Literal["Bhagavad Gita", "Mahabharata"]
    chapter: str | None = None  # Gita chapter number, or Mahabharata parva name
    verse: str | None = None    # None when only a parva-level citation is defensible
    citation: str
    text_type: Literal["paraphrase"] = "paraphrase"
    paraphrase: str
    interpretation: str
    alternative_interpretations: list[str] = Field(default_factory=list)
    ethical_dimension: list[str] = Field(default_factory=list)
    applicability: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    verification_status: str = "needs_scholarly_review"


class KnowledgeBase(BaseModel):
    version: str
    description: str
    attribution_note: str
    entries: list[KBEntry]


class RetrievedEntry(BaseModel):
    entry_id: str
    concept: str
    citation: str
    relevance: float
    matched_on: list[str] = Field(default_factory=list)


class ConceptContribution(BaseModel):
    concept: str
    entry_ids: list[str] = Field(min_length=1)  # every Dharma claim must cite the KB
    effect: float  # signed contribution on 0-10 scale relative to neutral 5
    note: str


class DharmaActionReading(BaseModel):
    action_id: str
    score: float = Field(ge=0, le=10)
    uncertainty: float = Field(ge=0, le=5)
    confidence: float = Field(ge=0, le=1)
    interpretation: str
    contributions: list[ConceptContribution]
    limitations: list[str] = Field(default_factory=list)


class DharmaEvaluation(BaseModel):
    source: Literal["heuristic", "llm", "heuristic_fallback"] = "heuristic"
    kb_version: str
    retrieved: list[RetrievedEntry]
    readings: list[DharmaActionReading]
    overview: str
    dropped_claims: int = 0  # claims removed by the citation validator
    disclaimer: str = (
        "Inspired by selected philosophical concepts and textual interpretations from the "
        "Bhagavad Gita and Mahabharata. Not a definitive interpretation of Hindu philosophy "
        "and not religious authority."
    )
