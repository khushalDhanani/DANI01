import logging
from collections.abc import Sequence

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.persistence.models.table_result import (
    AnalysisTableResultModel,
    AnalysisTableTimingModel,
)
from app.schemas.analysis import TableAnalysisSummary

logger = logging.getLogger(__name__)


class AnalysisTableResultRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_table_result(
        self,
        run_id: str,
        summary: TableAnalysisSummary,
    ) -> AnalysisTableResultModel:
        """
        Idempotently inserts or updates a table result and its timings.
        Guarantees that retry executions do not create duplicate records.
        """
        stmt = select(AnalysisTableResultModel).where(
            AnalysisTableResultModel.run_id == run_id,
            AnalysisTableResultModel.schema_name == summary.schema_name,
            AnalysisTableResultModel.table_name == summary.table,
        )
        record = self.session.execute(stmt).scalar_one_or_none()

        if not record:
            record = AnalysisTableResultModel(
                run_id=run_id,
                schema_name=summary.schema_name,
                table_name=summary.table,
            )
            self.session.add(record)

        record.estimated_rows = summary.estimated_rows
        record.sample_size = summary.sample_size
        record.returned_rows = summary.returned_rows
        record.column_count = summary.column_count
        record.profiled_columns = summary.profiled_columns
        record.classified_columns = summary.classified_columns
        record.status = summary.status.value if hasattr(summary.status, "value") else summary.status
        record.skip_reason = summary.skip_reason
        record.error_code = summary.error_code
        record.error_message = summary.error_message
        record.duration_ms = summary.duration_ms

        self.session.flush()

        # Save timings if provided
        if summary.timings:
            timing_stmt = select(AnalysisTableTimingModel).where(
                AnalysisTableTimingModel.table_result_id == record.id
            )
            timing_record = self.session.execute(timing_stmt).scalar_one_or_none()

            if not timing_record:
                timing_record = AnalysisTableTimingModel(table_result_id=record.id)
                self.session.add(timing_record)

            timing_record.structure_duration_ms = summary.timings.structure_duration_ms
            timing_record.sampling_duration_ms = summary.timings.sampling_duration_ms
            timing_record.profiling_duration_ms = summary.timings.profiling_duration_ms
            timing_record.classification_duration_ms = summary.timings.classification_duration_ms
            timing_record.total_duration_ms = summary.timings.total_duration_ms
            self.session.flush()

        return record

    def get_table_results(
        self,
        run_id: str,
        schema: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[AnalysisTableResultModel], int]:
        """Returns paginated list of table results for an analysis run."""
        base_filter = [AnalysisTableResultModel.run_id == run_id]
        if schema:
            base_filter.append(AnalysisTableResultModel.schema_name == schema)
        if status:
            base_filter.append(AnalysisTableResultModel.status == status)

        count_stmt = select(func.count(AnalysisTableResultModel.id)).where(*base_filter)
        total = self.session.execute(count_stmt).scalar_one()

        list_stmt = (
            select(AnalysisTableResultModel)
            .where(*base_filter)
            .order_by(
                desc(AnalysisTableResultModel.duration_ms),
                AnalysisTableResultModel.schema_name,
                AnalysisTableResultModel.table_name,
            )
            .limit(limit)
            .offset(offset)
        )
        items = self.session.execute(list_stmt).scalars().all()
        return items, total

    def get_table_result(
        self,
        run_id: str,
        schema_name: str,
        table_name: str,
    ) -> AnalysisTableResultModel | None:
        """Fetches a specific table result within a run."""
        stmt = select(AnalysisTableResultModel).where(
            AnalysisTableResultModel.run_id == run_id,
            AnalysisTableResultModel.schema_name == schema_name,
            AnalysisTableResultModel.table_name == table_name,
        )
        return self.session.execute(stmt).scalar_one_or_none()
