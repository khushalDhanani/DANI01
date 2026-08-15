from datetime import datetime, timezone
import logging
from typing import Sequence

from sqlalchemy import desc, func, select, update
from sqlalchemy.orm import Session

from app.persistence.models.analysis_run import (
    AnalysisErrorModel,
    AnalysisRunModel,
    AnalysisRunStatus,
)

logger = logging.getLogger(__name__)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisRunRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_run(
        self,
        database_name: str,
        analysis_type: str = "QUICK",
        schema_filter: str | None = None,
        run_id: str | None = None,
    ) -> AnalysisRunModel:
        """Creates a new AnalysisRun record with QUEUED status."""
        run = AnalysisRunModel(
            database_name=database_name,
            analysis_type=analysis_type,
            schema_filter=schema_filter,
            status=AnalysisRunStatus.QUEUED.value,
        )
        if run_id:
            run.id = run_id

        self.session.add(run)
        self.session.flush()
        return run

    def get_run(self, run_id: str) -> AnalysisRunModel | None:
        """Fetches an AnalysisRun by ID."""
        stmt = select(AnalysisRunModel).where(AnalysisRunModel.id == run_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def update_status(
        self,
        run_id: str,
        status: AnalysisRunStatus | str,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        duration_ms: float | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        celery_task_id: str | None = None,
    ) -> AnalysisRunModel | None:
        """Updates the status and metadata of an analysis run."""
        run = self.get_run(run_id)
        if not run:
            return None

        status_str = status.value if isinstance(status, AnalysisRunStatus) else status
        run.status = status_str

        if started_at is not None:
            run.started_at = started_at
        if completed_at is not None:
            run.completed_at = completed_at
        if duration_ms is not None:
            run.duration_ms = duration_ms
        if error_code is not None:
            run.error_code = error_code
        if error_message is not None:
            run.error_message = error_message
        if celery_task_id is not None:
            run.celery_task_id = celery_task_id

        self.session.flush()
        return run

    def update_progress(
        self,
        run_id: str,
        tables_total: int,
        tables_completed: int,
        tables_skipped: int,
        tables_failed: int,
        progress_percent: float,
        columns_discovered: int = 0,
        columns_profiled: int = 0,
        columns_classified: int = 0,
    ) -> None:
        """Updates live progress metrics for an analysis run."""
        stmt = (
            update(AnalysisRunModel)
            .where(AnalysisRunModel.id == run_id)
            .values(
                tables_total=tables_total,
                tables_completed=tables_completed,
                tables_skipped=tables_skipped,
                tables_failed=tables_failed,
                progress_percent=min(100.0, max(0.0, round(progress_percent, 2))),
                columns_discovered=columns_discovered,
                columns_profiled=columns_profiled,
                columns_classified=columns_classified,
            )
        )
        self.session.execute(stmt)
        self.session.flush()

    def request_cancellation(self, run_id: str) -> bool:
        """Requests cooperative cancellation of a queued or running analysis run."""
        run = self.get_run(run_id)
        if not run:
            return False

        if run.status in (AnalysisRunStatus.COMPLETED.value, AnalysisRunStatus.COMPLETED_WITH_ERRORS.value, AnalysisRunStatus.FAILED.value, AnalysisRunStatus.CANCELLED.value):
            return False

        if run.status == AnalysisRunStatus.QUEUED.value:
            run.status = AnalysisRunStatus.CANCELLED.value
            run.completed_at = utcnow()
        else:
            run.status = AnalysisRunStatus.CANCELLING.value

        self.session.flush()
        return True

    def is_cancelled(self, run_id: str) -> bool:
        """Checks if an analysis run is marked for cancellation or cancelled."""
        stmt = select(AnalysisRunModel.status).where(AnalysisRunModel.id == run_id)
        status = self.session.execute(stmt).scalar_one_or_none()
        return status in (AnalysisRunStatus.CANCELLING.value, AnalysisRunStatus.CANCELLED.value)

    def list_runs(self, limit: int = 20, offset: int = 0) -> tuple[Sequence[AnalysisRunModel], int]:
        """Returns paginated list of analysis runs and total count."""
        count_stmt = select(func.count(AnalysisRunModel.id))
        total = self.session.execute(count_stmt).scalar_one()

        list_stmt = (
            select(AnalysisRunModel)
            .order_by(desc(AnalysisRunModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        items = self.session.execute(list_stmt).scalars().all()
        return items, total

    def record_error(
        self,
        run_id: str,
        error_code: str,
        error_message: str,
        schema_name: str | None = None,
        table_name: str | None = None,
    ) -> AnalysisErrorModel:
        """Records a sanitized error event for an analysis run."""
        err = AnalysisErrorModel(
            run_id=run_id,
            schema_name=schema_name,
            table_name=table_name,
            error_code=error_code,
            error_message=error_message,
        )
        self.session.add(err)
        self.session.flush()
        return err
