from typing import Any

from sqlalchemy import JSON, BigInteger, Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base


class AnalysisColumnProfileModel(Base):
    __tablename__ = "analysis_column_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_result_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("analysis_table_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    column_name: Mapped[str] = mapped_column(String(128), nullable=False)
    data_type: Mapped[str] = mapped_column(String(64), nullable=False)
    profile_type: Mapped[str] = mapped_column(String(32), default="generic", nullable=False)

    null_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    null_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    distinct_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    distinct_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Privacy-sanitized top_values (redacted/empty if expose_values is False)
    top_values: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    # Type-specific stats dictionary (numeric mean/min/max, text length, boolean counts, etc.)
    stats: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    table_result = relationship("AnalysisTableResultModel", back_populates="column_profiles")


class AnalysisColumnClassificationModel(Base):
    __tablename__ = "analysis_column_classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_result_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("analysis_table_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    column_name: Mapped[str] = mapped_column(String(128), nullable=False)
    sql_type: Mapped[str] = mapped_column(String(64), nullable=False)
    semantic_type: Mapped[str] = mapped_column(String(64), nullable=False)
    sensitivity: Mapped[str] = mapped_column(String(32), nullable=False)
    expose_values: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    signals: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    table_result = relationship("AnalysisTableResultModel", back_populates="column_classifications")
