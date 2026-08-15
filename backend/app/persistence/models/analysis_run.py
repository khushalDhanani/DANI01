from datetime import datetime, timezone
from enum import Enum
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisRunStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"


class AnalysisRunModel(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    database_name: Mapped[str] = mapped_column(String(128), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(64), default="QUICK", nullable=False)
    schema_filter: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), default=AnalysisRunStatus.QUEUED.value, nullable=False, index=True
    )

    tables_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tables_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tables_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tables_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    columns_discovered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    columns_profiled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    columns_classified: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    progress_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)

    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    table_results = relationship(
        "AnalysisTableResultModel",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    errors = relationship(
        "AnalysisErrorModel",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class AnalysisErrorModel(Base):
    __tablename__ = "analysis_errors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schema_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    table_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error_code: Mapped[str] = mapped_column(String(64), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    run = relationship("AnalysisRunModel", back_populates="errors")
