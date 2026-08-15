from sqlalchemy import (
    BigInteger,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base


class AnalysisTableResultModel(Base):
    __tablename__ = "analysis_table_results"
    __table_args__ = (
        UniqueConstraint("run_id", "schema_name", "table_name", name="uq_run_schema_table"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schema_name: Mapped[str] = mapped_column(String(128), nullable=False)
    table_name: Mapped[str] = mapped_column(String(128), nullable=False)

    estimated_rows: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    returned_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    column_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    profiled_columns: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    classified_columns: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    skip_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    run = relationship("AnalysisRunModel", back_populates="table_results")
    timing = relationship(
        "AnalysisTableTimingModel",
        back_populates="table_result",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    column_profiles = relationship(
        "AnalysisColumnProfileModel",
        back_populates="table_result",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    column_classifications = relationship(
        "AnalysisColumnClassificationModel",
        back_populates="table_result",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class AnalysisTableTimingModel(Base):
    __tablename__ = "analysis_table_timings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_result_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("analysis_table_results.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    structure_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sampling_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    profiling_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    classification_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    table_result = relationship("AnalysisTableResultModel", back_populates="timing")
