from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.classification.taxonomy import SensitivityLevel
from app.db.postgres import Base
from app.persistence.models.analysis_run import AnalysisRunModel, AnalysisRunStatus
from app.schemas.analysis import (
    AnalysisStatus,
    DatabaseAnalysisResponse,
    TableAnalysisStatus,
    TableAnalysisSummary,
    TableAnalysisTimings,
)
from app.schemas.classification import (
    ColumnClassification,
    TableClassificationResponse,
)
from app.schemas.profiling import BaseColumnProfile, TableProfileResponse, ValueFrequency
from app.workers.analysis_tasks import run_database_analysis_task

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=test_engine)
TestingSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def override_db_context(monkeypatch):
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    from contextlib import contextmanager

    @contextmanager
    def mock_get_db_context():
        session = TestingSession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    monkeypatch.setattr("app.workers.analysis_tasks.get_db_context", mock_get_db_context)


def test_worker_task_successful_execution():
    # 1. Create a queued run in DB
    session = TestingSession()
    run = AnalysisRunModel(
        id="worker-success-run",
        database_name="AIRIS_TEST",
        analysis_type="QUICK",
        status=AnalysisRunStatus.QUEUED.value,
    )
    session.add(run)
    session.commit()
    session.close()

    # 2. Mock DatabaseAnalyzer response
    mock_profile = TableProfileResponse(
        schema="dbo",
        table="Users",
        sample_size=1000,
        returned_rows=100,
        columns=[
            BaseColumnProfile(
                name="Email",
                data_type="varchar",
                null_count=0,
                null_percent=0.0,
                distinct_count=100,
                distinct_percent=100.0,
                top_values=[ValueFrequency(value="user@example.com", count=1, percent=1.0)],
            )
        ],
    )

    mock_classification = TableClassificationResponse(
        schema="dbo",
        table="Users",
        columns=[
            ColumnClassification(
                name="Email",
                sql_type="varchar",
                semantic_type="EMAIL",
                sensitivity=SensitivityLevel.PII.value,
                expose_values=False,
                confidence=1.0,
            )
        ],
    )

    mock_summary = TableAnalysisSummary(
        schema="dbo",
        table="Users",
        estimated_rows=1000,
        status=TableAnalysisStatus.COMPLETED,
        sample_size=1000,
        returned_rows=100,
        column_count=1,
        profiled_columns=1,
        classified_columns=1,
        duration_ms=150.0,
        timings=TableAnalysisTimings(total_duration_ms=150.0),
        profile_response=mock_profile,
        classification_response=mock_classification,
    )

    mock_db_response = DatabaseAnalysisResponse(
        database="AIRIS_TEST",
        status=AnalysisStatus.COMPLETED,
        tables_total=1,
        tables_analyzed=1,
        tables_skipped=0,
        tables_failed=0,
        columns_discovered=1,
        columns_profiled=1,
        columns_classified=1,
        started_at="2026-08-14T12:00:00Z",
        completed_at="2026-08-14T12:00:01Z",
        duration_ms=150.0,
        tables=[mock_summary],
    )

    with patch(
        "app.workers.analysis_tasks.DatabaseAnalyzer.analyze_database", new_callable=AsyncMock
    ) as mock_analyze:
        mock_analyze.return_value = mock_db_response

        # Execute Celery task via .apply()
        result = run_database_analysis_task.apply(args=["worker-success-run"]).get()

        assert result["status"] == "COMPLETED"
        assert result["tables_analyzed"] == 1
        assert result["tables_failed"] == 0

        # Verify DB state
        session = TestingSession()
        run_record = session.get(AnalysisRunModel, "worker-success-run")
        assert run_record.status == AnalysisRunStatus.COMPLETED.value
        assert run_record.progress_percent == 100.0
        assert len(run_record.table_results) == 1

        table_record = run_record.table_results[0]
        assert table_record.table_name == "Users"
        assert len(table_record.column_profiles) == 1
        # Check that top_values was sanitized (redacted) because EMAIL is PII
        assert table_record.column_profiles[0].top_values == []
        session.close()


def test_worker_task_failure_isolation():
    session = TestingSession()
    run = AnalysisRunModel(
        id="worker-fail-run",
        database_name="AIRIS_TEST",
        analysis_type="QUICK",
        status=AnalysisRunStatus.QUEUED.value,
    )
    session.add(run)
    session.commit()
    session.close()

    mock_db_response = DatabaseAnalysisResponse(
        database="AIRIS_TEST",
        status=AnalysisStatus.COMPLETED_WITH_ERRORS,
        tables_total=2,
        tables_analyzed=1,
        tables_skipped=0,
        tables_failed=1,
        columns_discovered=5,
        columns_profiled=3,
        columns_classified=3,
        started_at="2026-08-14T12:00:00Z",
        completed_at="2026-08-14T12:00:01Z",
        duration_ms=200.0,
        tables=[
            TableAnalysisSummary(
                schema="dbo",
                table="GoodTable",
                estimated_rows=100,
                status=TableAnalysisStatus.COMPLETED,
                column_count=3,
                profiled_columns=3,
                classified_columns=3,
            ),
            TableAnalysisSummary(
                schema="dbo",
                table="BadTable",
                estimated_rows=500,
                status=TableAnalysisStatus.FAILED,
                error_code="QUERY_TIMEOUT",
                error_message="Query timed out",
                column_count=2,
            ),
        ],
    )

    with patch(
        "app.workers.analysis_tasks.DatabaseAnalyzer.analyze_database", new_callable=AsyncMock
    ) as mock_analyze:
        mock_analyze.return_value = mock_db_response

        result = run_database_analysis_task.apply(args=["worker-fail-run"]).get()

        assert result["status"] == "COMPLETED_WITH_ERRORS"
        assert result["tables_failed"] == 1

        session = TestingSession()
        run_record = session.get(AnalysisRunModel, "worker-fail-run")
        assert run_record.status == AnalysisRunStatus.COMPLETED_WITH_ERRORS.value
        assert len(run_record.errors) == 1
        assert run_record.errors[0].error_code == "QUERY_TIMEOUT"
        session.close()


def test_worker_task_cooperative_cancellation():
    session = TestingSession()
    run = AnalysisRunModel(
        id="worker-cancel-run",
        database_name="AIRIS_TEST",
        analysis_type="QUICK",
        status=AnalysisRunStatus.CANCELLED.value,
    )
    session.add(run)
    session.commit()
    session.close()

    result = run_database_analysis_task.apply(args=["worker-cancel-run"]).get()

    assert result["status"] == "CANCELLED"
