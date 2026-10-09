"""API request/response models for analyses."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.decision import (
    ActionComparison, DecisionMatrix, Explanation, Sensitivity, Weights,
)
from app.schemas.dharma import DharmaEvaluation
from app.schemas.dilemma import Action, DilemmaContext, Stakeholder, StructuredDilemma
from app.schemas.evaluation import FrameworkEvaluation


class AnalysisRequest(BaseModel):
    dilemma: str = Field(min_length=20, max_length=8000)
    context: DilemmaContext = Field(default_factory=DilemmaContext)
    weights: Weights | None = None
    include_dharma: bool = True


class RescoreRequest(BaseModel):
    weights: Weights


class RevisionRequest(BaseModel):
    """Human corrections. Anything omitted is kept from the parent run."""
    stakeholders: list[Stakeholder] | None = None
    actions: list[Action] | None = None
    assumptions: list[str] | None = None
    additional_context: str | None = Field(None, max_length=2000)
    weights: Weights | None = None


class DecisionRequest(BaseModel):
    choice: Literal["accept", "alternative", "modify", "reject"]
    action_id: str | None = None
    note: str = Field("", max_length=2000)


class FeedbackRequest(BaseModel):
    useful: bool | None = None
    ratings: dict[str, int] = Field(default_factory=dict)  # Likert 1-5 keyed by item
    comment: str = Field("", max_length=2000)


class ProviderInfo(BaseModel):
    provider: str
    model: str
    is_llm: bool
    note: str


class AnalysisResult(BaseModel):
    id: str
    parent_id: str | None = None
    created_at: datetime
    versions: dict[str, str]
    provider: ProviderInfo
    structured: StructuredDilemma
    evaluations: list[FrameworkEvaluation]
    dharma: DharmaEvaluation | None
    matrix: DecisionMatrix
    sensitivity: Sensitivity
    explanation: Explanation
    comparison: list[ActionComparison]
    fallbacks: list[str] = Field(default_factory=list)
    include_dharma: bool = True
    seed: int
    disclaimer: str
    decision: dict | None = None


class AnalysisSummary(BaseModel):
    id: str
    parent_id: str | None
    created_at: datetime
    summary: str
    domain: str
    recommended_label: str
    stability: str
    provider: str
    decision: str | None = None
