"""SQLAlchemy ORM models. SQLite by default, PostgreSQL via DHARMANET_DATABASE_URL."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120), default="anonymous")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Dilemma(Base):
    __tablename__ = "dilemmas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str | None] = mapped_column(Text, nullable=True)  # None when storage of text is disabled
    text_hash: Mapped[str] = mapped_column(String(32), index=True)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    dilemma_id: Mapped[int] = mapped_column(ForeignKey("dilemmas.id"))
    parent_run_id: Mapped[str | None] = mapped_column(String(24), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="complete")
    provider: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    analysis_version: Mapped[str] = mapped_column(String(20))
    framework_version: Mapped[str] = mapped_column(String(20))
    prompt_version: Mapped[str] = mapped_column(String(20))
    kb_version: Mapped[str] = mapped_column(String(20))
    scoring_version: Mapped[str] = mapped_column(String(20))
    seed: Mapped[int] = mapped_column(Integer)
    weights: Mapped[dict] = mapped_column(JSON)
    input: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict] = mapped_column(JSON)
    fallbacks: Mapped[list] = mapped_column(JSON, default=list)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class StakeholderRow(Base):
    __tablename__ = "stakeholders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    sid: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(40))
    user_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    data: Mapped[dict] = mapped_column(JSON)


class ActionRow(Base):
    __tablename__ = "actions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    aid: Mapped[str] = mapped_column(String(20))
    label: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(40))
    user_added: Mapped[bool] = mapped_column(Boolean, default=False)
    data: Mapped[dict] = mapped_column(JSON)


class EthicalEvaluationRow(Base):
    __tablename__ = "ethical_evaluations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    framework_id: Mapped[str] = mapped_column(String(40))
    framework_version: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(30))
    action_aid: Mapped[str] = mapped_column(String(20))
    score: Mapped[float] = mapped_column(Float)
    uncertainty: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    data: Mapped[dict] = mapped_column(JSON)


class DharmaEvaluationRow(Base):
    __tablename__ = "dharma_evaluations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    action_aid: Mapped[str] = mapped_column(String(20))
    score: Mapped[float] = mapped_column(Float)
    uncertainty: Mapped[float] = mapped_column(Float)
    data: Mapped[dict] = mapped_column(JSON)


class DecisionMatrixRow(Base):
    __tablename__ = "decision_matrices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    weights: Mapped[dict] = mapped_column(JSON)
    matrix: Mapped[dict] = mapped_column(JSON)
    sensitivity: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ExplanationRow(Base):
    __tablename__ = "explanations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    data: Mapped[dict] = mapped_column(JSON)


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(20))  # "decision" | "feedback"
    decision: Mapped[str | None] = mapped_column(String(20), nullable=True)
    chosen_action: Mapped[str | None] = mapped_column(String(20), nullable=True)
    useful: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ratings: Mapped[dict] = mapped_column(JSON, default=dict)
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_id: Mapped[str] = mapped_column(String(60), index=True)
    kb_version: Mapped[str] = mapped_column(String(20))
    concept: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(40))
    chapter: Mapped[str | None] = mapped_column(String(60), nullable=True)
    verse: Mapped[str | None] = mapped_column(String(20), nullable=True)
    data: Mapped[dict] = mapped_column(JSON)


def make_session_factory(url: str):
    kwargs = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {"pool_pre_ping": True}
    engine = create_engine(url, **kwargs)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
