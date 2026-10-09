"""Decision matrix, weights, sensitivity, explanation and comparison schemas."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.evaluation import DIMENSIONS

DEFAULT_WEIGHTS: dict[str, float] = {
    "consequences": 0.20,
    "duty": 0.20,
    "fairness": 0.15,
    "virtue": 0.10,
    "care": 0.10,
    "stakeholder_impact": 0.15,
    "dharma": 0.10,
}


class Weights(BaseModel):
    values: dict[str, float] = Field(default_factory=lambda: dict(DEFAULT_WEIGHTS))

    @field_validator("values")
    @classmethod
    def check(cls, v: dict[str, float]) -> dict[str, float]:
        unknown = set(v) - set(DIMENSIONS)
        if unknown:
            raise ValueError(f"unknown dimensions: {sorted(unknown)}")
        if any(x < 0 for x in v.values()):
            raise ValueError("weights must be non-negative")
        if sum(v.values()) <= 0:
            raise ValueError("at least one weight must be positive")
        return v


class MatrixCell(BaseModel):
    score: float
    uncertainty: float
    confidence: float


class WeightedScore(BaseModel):
    action_id: str
    score: float
    uncertainty: float
    confidence: float
    rank: int


class Recommendation(BaseModel):
    action_id: str
    runner_up_id: str | None
    margin: float
    clear_preference: bool
    statement: str


class DecisionMatrix(BaseModel):
    dimensions: list[str]
    actions: list[str]
    cells: dict[str, dict[str, MatrixCell]]  # action_id -> dimension -> cell
    weights: dict[str, float]  # normalised
    weighted: list[WeightedScore]  # user-weighted, sorted by rank
    equal_weighted: list[WeightedScore]
    recommendation: Recommendation
    equal_weight_recommendation: Recommendation


class FlipThreshold(BaseModel):
    dimension: str
    current_weight: float
    stays_top_from: float
    stays_top_to: float
    below_leader: str | None  # who leads if weight drops below range
    above_leader: str | None  # who leads if weight rises above range
    margin_to_flip: float  # distance from current weight to nearest flip (1.0 = never flips)


class Sensitivity(BaseModel):
    leader: str
    flip_thresholds: list[FlipThreshold]
    weight_stability: float  # share of perturbed-weight samples where leader stays top
    score_stability: float   # share of score-noise samples where leader stays top
    win_share_weights: dict[str, float]
    win_share_scores: dict[str, float]
    label: Literal["Stable", "Moderately Sensitive", "Highly Sensitive"]
    samples: int
    seed: int
    method_note: str


class TraceStep(BaseModel):
    step: int
    stage: str
    summary: str


class Explanation(BaseModel):
    why: str
    principles: list[str]
    key_stakeholders: list[str]
    assumptions: list[str]
    what_could_change: list[str]
    disagreements: list[str]
    trace: list[TraceStep]
    note: str = (
        "This is a structured explanation trace assembled from recorded pipeline outputs; "
        "it is not a model's private chain-of-thought."
    )


class ActionComparison(BaseModel):
    action_id: str
    label: str
    strengths: list[str]
    weaknesses: list[str]
    stakeholders_helped: list[str]
    stakeholders_harmed: list[str]
    short_term: str
    long_term: str
    risks: list[str]
    uncertainty: str
    framework_disagreement: str
    dharma_view: str
    best_dimensions: list[str]
    worst_dimensions: list[str]
