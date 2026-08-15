import logging
from typing import Any, Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.persistence.models.column_profile import (
    AnalysisColumnClassificationModel,
    AnalysisColumnProfileModel,
)
from app.schemas.classification import ColumnClassification

logger = logging.getLogger(__name__)


class AnalysisProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_column_profiles(
        self,
        table_result_id: int,
        profiles: list[dict[str, Any]],
    ) -> None:
        """
        Saves sanitized column profiles for a table result.
        Replaces previous records if re-run (idempotency).
        """
        # Delete any existing profiles for this table result
        self.session.execute(
            delete(AnalysisColumnProfileModel).where(
                AnalysisColumnProfileModel.table_result_id == table_result_id
            )
        )

        for p in profiles:
            record = AnalysisColumnProfileModel(
                table_result_id=table_result_id,
                column_name=p["column_name"],
                data_type=p["data_type"],
                profile_type=p.get("profile_type", "generic"),
                null_count=p.get("null_count", 0),
                null_percent=p.get("null_percent", 0.0),
                distinct_count=p.get("distinct_count", 0),
                distinct_percent=p.get("distinct_percent", 0.0),
                top_values=p.get("top_values"),
                stats=p.get("stats"),
            )
            self.session.add(record)

        self.session.flush()

    def save_column_classifications(
        self,
        table_result_id: int,
        classifications: list[ColumnClassification],
    ) -> None:
        """
        Saves semantic classifications for a table result.
        Replaces previous records if re-run (idempotency).
        """
        # Delete any existing classifications for this table result
        self.session.execute(
            delete(AnalysisColumnClassificationModel).where(
                AnalysisColumnClassificationModel.table_result_id == table_result_id
            )
        )

        for c in classifications:
            record = AnalysisColumnClassificationModel(
                table_result_id=table_result_id,
                column_name=c.name,
                sql_type=c.sql_type,
                semantic_type=c.semantic_type,
                sensitivity=c.sensitivity,
                expose_values=c.expose_values,
                confidence=c.confidence,
                signals=c.signals,
            )
            self.session.add(record)

        self.session.flush()

    def get_column_profiles(
        self,
        table_result_id: int,
    ) -> Sequence[AnalysisColumnProfileModel]:
        """Fetches all column profiles for a table result."""
        stmt = (
            select(AnalysisColumnProfileModel)
            .where(AnalysisColumnProfileModel.table_result_id == table_result_id)
            .order_by(AnalysisColumnProfileModel.id)
        )
        return self.session.execute(stmt).scalars().all()

    def get_column_classifications(
        self,
        table_result_id: int,
    ) -> Sequence[AnalysisColumnClassificationModel]:
        """Fetches all column classifications for a table result."""
        stmt = (
            select(AnalysisColumnClassificationModel)
            .where(AnalysisColumnClassificationModel.table_result_id == table_result_id)
            .order_by(AnalysisColumnClassificationModel.id)
        )
        return self.session.execute(stmt).scalars().all()
