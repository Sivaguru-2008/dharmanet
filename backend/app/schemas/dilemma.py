"""Structured representation of an ethical dilemma."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

StakeholderRole = Literal["primary", "secondary", "vulnerable", "decision_maker", "direct", "indirect"]
ActionKind = Literal[
    "direct", "escalate_internal", "escalate_external", "gather_info",
    "compromise", "delay", "status_quo", "custom",
]
ConflictType = Literal[
    "duty_vs_consequence", "individual_vs_collective", "truth_vs_loyalty", "justice_vs_mercy",
    "short_vs_long_term", "self_interest_vs_social_responsibility", "legal_vs_moral",
    "organizational_loyalty_vs_public_safety", "autonomy_vs_beneficence", "privacy_vs_safety",
    "other",
]

FEATURE_NAMES: tuple[str, ...] = (
    "prevents_harm",          # degree the action prevents the main threatened harm
    "causes_harm",            # collateral harm the action itself causes
    "honesty",                # transparency / truthfulness
    "role_duty",              # alignment with the decision-maker's role obligations
    "due_process",            # procedural fairness, proper channels, rights of the accused
    "protects_vulnerable",    # protection of the most vulnerable stakeholders
    "preserves_relationships",
    "self_interest",          # how much the action serves the decision-maker personally
    "reversibility",          # can the action be undone / corrected later
    "information_gain",       # does the action reduce uncertainty before irreversible steps
    "timeliness",             # acts before harm materialises
    "courage",                # personal risk accepted for principle
)


class ActionFeatures(BaseModel):
    """Interpretable 0-1 attributes of an action, estimated by the heuristic engine or an LLM."""
    prevents_harm: float = Field(0.5, ge=0, le=1)
    causes_harm: float = Field(0.5, ge=0, le=1)
    honesty: float = Field(0.5, ge=0, le=1)
    role_duty: float = Field(0.5, ge=0, le=1)
    due_process: float = Field(0.5, ge=0, le=1)
    protects_vulnerable: float = Field(0.5, ge=0, le=1)
    preserves_relationships: float = Field(0.5, ge=0, le=1)
    self_interest: float = Field(0.5, ge=0, le=1)
    reversibility: float = Field(0.5, ge=0, le=1)
    information_gain: float = Field(0.5, ge=0, le=1)
    timeliness: float = Field(0.5, ge=0, le=1)
    courage: float = Field(0.5, ge=0, le=1)


class Stakeholder(BaseModel):
    id: str
    name: str = Field(min_length=1, max_length=120)
    category: str = "other"
    roles: list[StakeholderRole] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    rights: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    vulnerabilities: list[str] = Field(default_factory=list)
    potential_benefits: list[str] = Field(default_factory=list)
    potential_harms: list[str] = Field(default_factory=list)
    salience: float = Field(0.5, ge=0, le=1)
    user_edited: bool = False

    @property
    def is_vulnerable(self) -> bool:
        return "vulnerable" in self.roles


class Action(BaseModel):
    id: str
    label: str = Field(min_length=1, max_length=160)
    description: str = ""
    kind: ActionKind = "custom"
    features: ActionFeatures = Field(default_factory=ActionFeatures)
    user_added: bool = False


class Conflict(BaseModel):
    id: str
    type: ConflictType = "other"
    title: str
    description: str = ""
    between: list[str] = Field(default_factory=list)
    intensity: float = Field(0.5, ge=0, le=1)


class ContextCues(BaseModel):
    """Interpretable context signals (0-1) that modulate framework scoring."""
    severity: float = Field(0.5, ge=0, le=1)
    vulnerability: float = Field(0.4, ge=0, le=1)
    relational_closeness: float = Field(0.3, ge=0, le=1)
    uncertainty: float = Field(0.4, ge=0, le=1)
    legal_dimension: float = Field(0.2, ge=0, le=1)
    urgency: float = Field(0.4, ge=0, le=1)
    scale: float = Field(0.4, ge=0, le=1)  # how many people are affected
    evidence: list[str] = Field(default_factory=list)


class DilemmaContext(BaseModel):
    role: str = Field("", max_length=200)
    domain: str = Field("", max_length=80)
    cultural_context: str = Field("", max_length=200)
    time_pressure: str = Field("", max_length=80)
    additional: str = Field("", max_length=2000)


class StructuredDilemma(BaseModel):
    dilemma_text: str
    summary: str
    domain: str = "general"
    decision_maker: str = "You (the decision-maker)"
    context: DilemmaContext = Field(default_factory=DilemmaContext)
    stakeholders: list[Stakeholder] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    ethical_dimensions: list[str] = Field(default_factory=list)
    cues: ContextCues = Field(default_factory=ContextCues)

    @field_validator("actions")
    @classmethod
    def unique_action_ids(cls, v: list[Action]) -> list[Action]:
        ids = [a.id for a in v]
        if len(ids) != len(set(ids)):
            raise ValueError("action ids must be unique")
        return v

    @field_validator("stakeholders")
    @classmethod
    def unique_stakeholder_ids(cls, v: list[Stakeholder]) -> list[Stakeholder]:
        ids = [s.id for s in v]
        if len(ids) != len(set(ids)):
            raise ValueError("stakeholder ids must be unique")
        return v
