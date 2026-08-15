import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from celery.exceptions import MaxRetriesExceededError

from app.analysis.database_analyzer import DatabaseAnalyzer
from app.analysis.sanitization import ProfileSanitizer
from app.core.exceptions import DatabaseConnectionError
from app.db.postgres import get_db_context
from app.persistence.models.analysis_run import AnalysisRunStatus
from app.persistence.repositories.analysis_runs import AnalysisRunRepository
from app.persistence.repositories.profiles import AnalysisProfileRepository
from app.persistence.repositories.table_results import AnalysisTableResultRepository
from app.schemas.analysis import AnalysisProgress
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def utcnow() -> datetime:
    return datetime.now(UTC)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def run_database_analysis_task(self, run_id: str) -> dict[str, Any]:
    """
    Celery background worker task for executing database-wide quick analysis.
    Coordinates run status lifecycle, invokes existing DatabaseAnalyzer,
    sanitizes profiles against PII leakage, and commits durable results to PostgreSQL.
    """
    logger.info(f"Worker task started for AnalysisRun {run_id}")

    # 1. Check if run exists and set RUNNING
    with get_db_context() as session:
        run_repo = AnalysisRunRepository(session)
        run = run_repo.get_run(run_id)
        if not run:
            logger.error(f"AnalysisRun {run_id} not found in database.")
            return {"error": "RUN_NOT_FOUND", "run_id": run_id}

        if run.status == AnalysisRunStatus.CANCELLED.value:
            logger.info(f"AnalysisRun {run_id} was cancelled before starting.")
            return {"status": "CANCELLED", "run_id": run_id}

        run_repo.update_status(
            run_id,
            status=AnalysisRunStatus.RUNNING,
            started_at=utcnow(),
            celery_task_id=self.request.id,
        )
        schema_filter = run.schema_filter

    # 2. Progress callback for real-time PostgreSQL updates
    def on_progress(progress: AnalysisProgress) -> None:
        try:
            with get_db_context() as progress_session:
                p_repo = AnalysisRunRepository(progress_session)
                p_repo.update_progress(
                    run_id=run_id,
                    tables_total=progress.tables_total,
                    tables_completed=progress.tables_completed,
                    tables_skipped=progress.tables_skipped,
                    tables_failed=progress.tables_failed,
                    progress_percent=progress.progress_percent,
                )
        except Exception as pe:
            logger.warning(f"Failed to persist progress update for {run_id}: {pe}")

    # 3. Execute DatabaseAnalyzer
    try:
        analyzer = DatabaseAnalyzer()
        # Execute async analysis in standard asyncio runner
        analysis_response = asyncio.run(
            analyzer.analyze_database(
                schema=schema_filter,
                progress_callback=on_progress,
            )
        )

        # 4. Persist results, profiles, classifications, and timings transactionally
        with get_db_context() as session:
            run_repo = AnalysisRunRepository(session)
            table_repo = AnalysisTableResultRepository(session)
            profile_repo = AnalysisProfileRepository(session)

            # Check if cancelled during execution
            if run_repo.is_cancelled(run_id):
                run_repo.update_status(
                    run_id,
                    status=AnalysisRunStatus.CANCELLED,
                    completed_at=utcnow(),
                )
                logger.info(f"AnalysisRun {run_id} cancelled cooperatively.")
                return {"status": "CANCELLED", "run_id": run_id}

            for table_summary in analysis_response.tables:
                table_record = table_repo.upsert_table_result(run_id, table_summary)

                # Persist sanitized profiles and classifications if available
                if (
                    hasattr(table_summary, "profile_response")
                    and table_summary.profile_response
                    and hasattr(table_summary, "classification_response")
                    and table_summary.classification_response
                ):
                    sanitized_profiles = ProfileSanitizer.sanitize_column_profiles(
                        table_summary.profile_response,
                        table_summary.classification_response,
                    )
                    profile_repo.save_column_profiles(table_record.id, sanitized_profiles)
                    profile_repo.save_column_classifications(
                        table_record.id,
                        table_summary.classification_response.columns,
                    )

                if table_summary.error_code:
                    run_repo.record_error(
                        run_id=run_id,
                        error_code=table_summary.error_code,
                        error_message=table_summary.error_message or "Table analysis failed",
                        schema_name=table_summary.schema_name,
                        table_name=table_summary.table,
                    )

            # Determine final status
            final_status = (
                AnalysisRunStatus.COMPLETED
                if analysis_response.tables_failed == 0
                else AnalysisRunStatus.COMPLETED_WITH_ERRORS
            )

            run_repo.update_status(
                run_id,
                status=final_status,
                completed_at=utcnow(),
                duration_ms=analysis_response.duration_ms,
            )

            # Final progress update to ensure 100%
            run_repo.update_progress(
                run_id=run_id,
                tables_total=analysis_response.tables_total,
                tables_completed=analysis_response.tables_analyzed,
                tables_skipped=analysis_response.tables_skipped,
                tables_failed=analysis_response.tables_failed,
                progress_percent=100.0,
                columns_discovered=analysis_response.columns_discovered,
                columns_profiled=analysis_response.columns_profiled,
                columns_classified=analysis_response.columns_classified,
            )

            logger.info(
                f"AnalysisRun {run_id} finished successfully with status {final_status.value}"
            )
            return {
                "run_id": run_id,
                "status": final_status.value,
                "tables_analyzed": analysis_response.tables_analyzed,
                "tables_skipped": analysis_response.tables_skipped,
                "tables_failed": analysis_response.tables_failed,
                "duration_ms": analysis_response.duration_ms,
            }

    except DatabaseConnectionError as dce:
        logger.error(f"Transient database connection error in run {run_id}: {dce}")
        try:
            raise self.retry(exc=dce)
        except MaxRetriesExceededError:
            with get_db_context() as session:
                run_repo = AnalysisRunRepository(session)
                run_repo.update_status(
                    run_id,
                    status=AnalysisRunStatus.FAILED,
                    error_code="CONNECTION_ERROR",
                    error_message=f"Database connection error: {dce}",
                    completed_at=utcnow(),
                )
                run_repo.record_error(
                    run_id, "CONNECTION_ERROR", f"Database connection error: {dce}"
                )
            return {"status": "FAILED", "error": str(dce)}

    except Exception as e:
        logger.error(f"Fatal error executing AnalysisRun {run_id}: {e}", exc_info=True)
        with get_db_context() as session:
            run_repo = AnalysisRunRepository(session)
            run_repo.update_status(
                run_id,
                status=AnalysisRunStatus.FAILED,
                error_code="EXECUTION_ERROR",
                error_message=f"Fatal analysis failure: {e!s}",
                completed_at=utcnow(),
            )
            run_repo.record_error(run_id, "EXECUTION_ERROR", f"Fatal analysis failure: {e!s}")
        return {"status": "FAILED", "error": str(e)}
