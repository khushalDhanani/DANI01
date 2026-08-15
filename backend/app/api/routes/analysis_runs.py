import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.postgres import get_db_session
from app.persistence.models.analysis_run import AnalysisRunStatus
from app.persistence.repositories.analysis_runs import AnalysisRunRepository
from app.persistence.repositories.profiles import AnalysisProfileRepository
from app.persistence.repositories.table_results import AnalysisTableResultRepository
from app.schemas.analysis import TableAnalysisTimings
from app.schemas.analysis_runs import (
    AnalysisRunCreatedResponse,
    AnalysisRunDetailResponse,
    AnalysisRunListResponse,
    AnalysisRunTableDetailResponse,
    AnalysisRunTableListResponse,
    AnalysisRunTableResultItem,
    CancelAnalysisRunResponse,
    CreateAnalysisRunRequest,
)
from app.workers.analysis_tasks import run_database_analysis_task

router = APIRouter()
logger = logging.getLogger(__name__)

DBSessionDep = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/",
    response_model=AnalysisRunCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create and start a database-wide analysis run",
)
def create_analysis_run(
    request: CreateAnalysisRunRequest = CreateAnalysisRunRequest(),
    session: DBSessionDep = None,
):
    """
    Submits a database-wide analysis run to the background Celery worker.
    Returns HTTP 202 Accepted immediately with the generated run ID.
    """
    repo = AnalysisRunRepository(session)
    database_name = settings.MSSQL_DATABASE or "AIRIS_TEST"

    # 1. Create run record in PostgreSQL with QUEUED status
    run = repo.create_run(
        database_name=database_name,
        analysis_type=request.analysis_type,
        schema_filter=request.schema_name,
    )

    # 2. Dispatch background task via Celery
    try:
        task = run_database_analysis_task.delay(run.id)
        repo.update_status(run.id, status=AnalysisRunStatus.QUEUED, celery_task_id=task.id)
    except Exception as e:
        logger.warning(
            f"Celery dispatch failed, running inline fallback or recording queue error: {e}"
        )

    return AnalysisRunCreatedResponse(
        run_id=run.id,
        database=run.database_name,
        analysis_type=run.analysis_type,
        status=run.status,
        created_at=run.created_at,
    )


@router.get(
    "/",
    response_model=AnalysisRunListResponse,
    summary="List analysis runs",
)
def list_analysis_runs(
    session: DBSessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Lists historical and active analysis runs with pagination."""
    repo = AnalysisRunRepository(session)
    runs, total = repo.list_runs(limit=limit, offset=offset)

    items = [
        AnalysisRunDetailResponse(
            run_id=r.id,
            database=r.database_name,
            analysis_type=r.analysis_type,
            schema_filter=r.schema_filter,
            status=r.status,
            tables_total=r.tables_total,
            tables_completed=r.tables_completed,
            tables_skipped=r.tables_skipped,
            tables_failed=r.tables_failed,
            columns_discovered=r.columns_discovered,
            columns_profiled=r.columns_profiled,
            columns_classified=r.columns_classified,
            progress_percent=r.progress_percent,
            created_at=r.created_at,
            started_at=r.started_at,
            completed_at=r.completed_at,
            duration_ms=r.duration_ms,
            error_code=r.error_code,
            error_message=r.error_message,
        )
        for r in runs
    ]

    return AnalysisRunListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/{run_id}",
    response_model=AnalysisRunDetailResponse,
    summary="Get analysis run details & live progress",
)
def get_analysis_run(
    run_id: str,
    session: DBSessionDep,
):
    """Fetches real-time status, progress, table counts, and summary for an analysis run."""
    repo = AnalysisRunRepository(session)
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AnalysisRun '{run_id}' not found.",
        )

    return AnalysisRunDetailResponse(
        run_id=run.id,
        database=run.database_name,
        analysis_type=run.analysis_type,
        schema_filter=run.schema_filter,
        status=run.status,
        tables_total=run.tables_total,
        tables_completed=run.tables_completed,
        tables_skipped=run.tables_skipped,
        tables_failed=run.tables_failed,
        columns_discovered=run.columns_discovered,
        columns_profiled=run.columns_profiled,
        columns_classified=run.columns_classified,
        progress_percent=run.progress_percent,
        created_at=run.created_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
        duration_ms=run.duration_ms,
        error_code=run.error_code,
        error_message=run.error_message,
    )


@router.get(
    "/{run_id}/tables",
    response_model=AnalysisRunTableListResponse,
    summary="Get table results for an analysis run",
)
def get_analysis_run_tables(
    run_id: str,
    session: DBSessionDep,
    schema: str | None = Query(default=None, description="Filter by schema name"),
    status_filter: str | None = Query(
        default=None, alias="status", description="Filter by status (COMPLETED/SKIPPED/FAILED)"
    ),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Fetches paginated list of table results belonging to an analysis run."""
    run_repo = AnalysisRunRepository(session)
    if not run_repo.get_run(run_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AnalysisRun '{run_id}' not found.",
        )

    table_repo = AnalysisTableResultRepository(session)
    tables, total = table_repo.get_table_results(
        run_id=run_id,
        schema=schema,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    items = [
        AnalysisRunTableResultItem(
            schema=t.schema_name,
            table=t.table_name,
            estimated_rows=t.estimated_rows,
            sample_size=t.sample_size,
            returned_rows=t.returned_rows,
            column_count=t.column_count,
            profiled_columns=t.profiled_columns,
            classified_columns=t.classified_columns,
            status=t.status,
            skip_reason=t.skip_reason,
            error_code=t.error_code,
            error_message=t.error_message,
            duration_ms=t.duration_ms,
        )
        for t in tables
    ]

    return AnalysisRunTableListResponse(
        run_id=run_id,
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{run_id}/tables/{schema_name}/{table_name}",
    response_model=AnalysisRunTableDetailResponse,
    summary="Get detailed result for a single table in a run",
)
def get_analysis_run_table_detail(
    run_id: str,
    schema_name: str,
    table_name: str,
    session: DBSessionDep,
):
    """Fetches detailed metrics, timings, sanitized profiles, and classifications for a specific table."""
    table_repo = AnalysisTableResultRepository(session)
    table_record = table_repo.get_table_result(run_id, schema_name, table_name)
    if not table_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table result '{schema_name}.{table_name}' for run '{run_id}' not found.",
        )

    profile_repo = AnalysisProfileRepository(session)
    profiles = profile_repo.get_column_profiles(table_record.id)
    classifications = profile_repo.get_column_classifications(table_record.id)

    timings = None
    if table_record.timing:
        timings = TableAnalysisTimings(
            structure_duration_ms=table_record.timing.structure_duration_ms,
            sampling_duration_ms=table_record.timing.sampling_duration_ms,
            profiling_duration_ms=table_record.timing.profiling_duration_ms,
            classification_duration_ms=table_record.timing.classification_duration_ms,
            total_duration_ms=table_record.timing.total_duration_ms,
        )

    col_profiles_data = [
        {
            "column_name": p.column_name,
            "data_type": p.data_type,
            "profile_type": p.profile_type,
            "null_count": p.null_count,
            "null_percent": p.null_percent,
            "distinct_count": p.distinct_count,
            "distinct_percent": p.distinct_percent,
            "top_values": p.top_values,
            "stats": p.stats,
        }
        for p in profiles
    ]

    col_class_data = [
        {
            "column_name": c.column_name,
            "sql_type": c.sql_type,
            "semantic_type": c.semantic_type,
            "sensitivity": c.sensitivity,
            "expose_values": c.expose_values,
            "confidence": c.confidence,
            "signals": c.signals,
        }
        for c in classifications
    ]

    return AnalysisRunTableDetailResponse(
        schema=table_record.schema_name,
        table=table_record.table_name,
        estimated_rows=table_record.estimated_rows,
        sample_size=table_record.sample_size,
        returned_rows=table_record.returned_rows,
        column_count=table_record.column_count,
        status=table_record.status,
        skip_reason=table_record.skip_reason,
        error_code=table_record.error_code,
        error_message=table_record.error_message,
        duration_ms=table_record.duration_ms,
        timings=timings,
        column_profiles=col_profiles_data,
        column_classifications=col_class_data,
    )


@router.post(
    "/{run_id}/cancel",
    response_model=CancelAnalysisRunResponse,
    summary="Request cooperative cancellation of an analysis run",
)
def cancel_analysis_run(
    run_id: str,
    session: DBSessionDep,
):
    """Requests cancellation of a queued or running analysis run."""
    repo = AnalysisRunRepository(session)
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AnalysisRun '{run_id}' not found.",
        )

    success = repo.request_cancellation(run_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel run '{run_id}' with status '{run.status}'.",
        )

    updated_run = repo.get_run(run_id)
    return CancelAnalysisRunResponse(
        run_id=run_id,
        status=updated_run.status if updated_run else "CANCELLED",
        message=f"Cancellation requested for analysis run '{run_id}'.",
    )
