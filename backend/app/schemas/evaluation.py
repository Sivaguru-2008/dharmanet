"""Per-framework, per-action evaluation outputs."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

DIMENSIONS: tuple[str, ...] = (
    "consequences", "duty", "fairness", "virtue", "care", "stakeholder_impact", "dharma",
)

DIMENSION_LABELS: dict[str, str] = {
    "consequences": "Consequences",
    "duty": "Duty",
    "fairness": "Fairness / Justice",
    "virtue": "Virtue",
    "care": "Care",
    "stakeholder_impact": "Stakeholder Impact",
    "dharma": "Dharma-inspired",
}


class DimensionScore(BaseModel):
    dimension: str
    action_id: str
    score: float = Field(ge=0, le=10)
    uncertainty: float = Field(ge=0, le=5, description="± half-width on the 0-10 scale")
    confidence: float = Field(ge=0, le=1)
    confidence_type: Literal["model-estimated"] = "model-estimated"
    rationale: str
    principle: str = ""
    assumptions: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    potential_disagreement: str = ""
    flags: list[str] = Field(default_factory=list)  # e.g. "duty_violation"
    citations: list[str] = Field(default_factory=list)  # KB entry ids (dharma only)


class StakeholderImpact(BaseModel):
    stakeholder_id: str
    action_id: str
    impact: float = Field(ge=-1, le=1)  # -1 strongly harmed .. +1 strongly helped
    note: str = ""


class FrameworkEvaluation(BaseModel):
    framework_id: str
    framework_name: str
    framework_version: str
    source: Literal["heuristic", "llm", "heuristic_fallback"] = "heuristic"
    summary: str = ""
    scores: list[DimensionScore]
    stakeholder_impacts: list[StakeholderImpact] = Field(default_factory=list)
