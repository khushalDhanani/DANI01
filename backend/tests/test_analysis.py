import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from app.analysis.database_analyzer import DatabaseAnalyzer
from app.analysis.planner import AnalysisPlanner
from app.analysis.table_analyzer import TableAnalyzer
from app.classification.taxonomy import SensitivityLevel
from app.core.config import Settings
from app.core.exceptions import DiscoveryError, TableNotFoundError
from app.main import app
from app.schemas.analysis import (
    AnalysisStatus,
    DatabaseAnalysisResponse,
    QuickAnalysisRequest,
    TableAnalysisPlan,
    TableAnalysisStatus,
    TableAnalysisSummary,
    TableSkipReason,
)
from app.schemas.classification import (
    ColumnClassification,
    TableClassificationResponse,
)
from app.schemas.database import ColumnInfo, TableInfo, TableListResponse
from app.schemas.profiling import BaseColumnProfile, TableProfileResponse

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. PLANNER TESTS
# ---------------------------------------------------------------------------


def test_planner_empty_table():
    planner = AnalysisPlanner()
    table = TableInfo(
        schema="dbo",
        table="EmptyLogs",
        estimated_rows=0,
        column_count=5,
    )
    plan = planner.determine_table_plan(table)

    assert plan.schema_name == "dbo"
    assert plan.table == "EmptyLogs"
    assert plan.estimated_rows == 0
    assert plan.should_analyze is False
    assert plan.sample_size == 0
    assert plan.skip_reason == TableSkipReason.EMPTY_TABLE.value


def test_planner_tiny_table():
    planner = AnalysisPlanner()
    table = TableInfo(
        schema="dbo",
        table="TinyTable",
        estimated_rows=500,
        column_count=3,
    )
    plan = planner.determine_table_plan(table)

    assert plan.should_analyze is True
    assert plan.sample_size == 1000
    assert plan.skip_reason is None


def test_planner_small_table():
    planner = AnalysisPlanner()
    table = TableInfo(
        schema="dbo",
        table="SmallTable",
        estimated_rows=5000,
        column_count=8,
    )
    plan = planner.determine_table_plan(table)

    assert plan.should_analyze is True
    assert plan.sample_size == 1000


def test_planner_medium_table():
    planner = AnalysisPlanner()
    table = TableInfo(
        schema="dbo",
        table="MediumTable",
        estimated_rows=50000,
        column_count=12,
    )
    plan = planner.determine_table_plan(table)

    assert plan.should_analyze is True
    assert plan.sample_size == 2000


def test_planner_large_table():
    planner = AnalysisPlanner()
    table = TableInfo(
        schema="dbo",
        table="LargeTable",
        estimated_rows=500000,
        column_count=20,
    )
    plan = planner.determine_table_plan(table)

    assert plan.should_analyze is True
    assert plan.sample_size == 3000


def test_planner_very_large_table():
    planner = AnalysisPlanner()
    table = TableInfo(
        schema="dbo",
        table="HugeTable",
        estimated_rows=10000000,
        column_count=40,
    )
    plan = planner.determine_table_plan(table)

    assert plan.should_analyze is True
    assert plan.sample_size == 5000


def test_planner_sample_never_exceeds_max_cap():
    custom_settings = Settings(
        PROFILE_MAX_SAMPLE_SIZE=2500,
        ANALYSIS_SAMPLE_VERY_LARGE=5000,
    )
    planner = AnalysisPlanner(config=custom_settings)
    table = TableInfo(
        schema="dbo",
        table="HugeTable",
        estimated_rows=50000000,
        column_count=10,
    )
    plan = planner.determine_table_plan(table)

    assert plan.sample_size == 2500


def test_planner_database_plan_with_schema_filter():
    planner = AnalysisPlanner()
    tables = [
        TableInfo(
            schema="dbo", table="Users", estimated_rows=1000, column_count=5
        ),
        TableInfo(
            schema="dbo", table="EmptyAudit", estimated_rows=0, column_count=3
        ),
        TableInfo(
            schema="staging", table="StgData", estimated_rows=5000, column_count=10
        ),
    ]

    # Without filter
    all_plan = planner.create_database_plan(tables, database_name="AIRIS_TEST")
    assert all_plan.total_tables == 3
    assert all_plan.planned_tables == 2
    assert all_plan.skipped_tables == 1

    # With schema filter
    dbo_plan = planner.create_database_plan(
        tables, database_name="AIRIS_TEST", schema_filter="dbo"
    )
    assert dbo_plan.total_tables == 2
    assert dbo_plan.planned_tables == 1
    assert dbo_plan.skipped_tables == 1
    assert all(p.schema_name == "dbo" for p in dbo_plan.table_plans)


# ---------------------------------------------------------------------------
# 2. TABLE ANALYZER TESTS
# ---------------------------------------------------------------------------


def test_table_analyzer_successful_table():
    mock_discovery = MagicMock()
    mock_discovery.get_columns.return_value = [
        ColumnInfo(
            ordinal=1,
            name="ID",
            data_type="int",
            nullable=False,
            identity=True,
            computed=False,
            has_default=False,
            primary_key=True,
        ),
        ColumnInfo(
            ordinal=2,
            name="Name",
            data_type="varchar",
            nullable=True,
            identity=False,
            computed=False,
            has_default=False,
        ),
    ]

    mock_profiler = MagicMock()
    mock_profiler.profile_table.return_value = TableProfileResponse(
        schema="dbo",
        table="Users",
        sample_size=1000,
        returned_rows=250,
        columns=[
            BaseColumnProfile(
                name="ID",
                data_type="int",
                null_count=0,
                null_percent=0.0,
                distinct_count=250,
                distinct_percent=100.0,
            ),
            BaseColumnProfile(
                name="Name",
                data_type="varchar",
                null_count=5,
                null_percent=2.0,
                distinct_count=200,
                distinct_percent=80.0,
            ),
        ],
    )

    mock_classifier = MagicMock()
    mock_classifier.classify_table.return_value = TableClassificationResponse(
        schema="dbo",
        table="Users",
        columns=[
            ColumnClassification(
                name="ID",
                sql_type="int",
                semantic_type="identifier",
                sensitivity=SensitivityLevel.PUBLIC.value,
                expose_values=True,
                confidence=1.0,
            ),
            ColumnClassification(
                name="Name",
                sql_type="varchar",
                semantic_type="name",
                sensitivity=SensitivityLevel.PII.value,
                expose_values=False,
                confidence=0.9,
            ),
        ],
    )

    analyzer = TableAnalyzer(
        discovery=mock_discovery,
        profiler=mock_profiler,
        classifier=mock_classifier,
    )

    plan = TableAnalysisPlan(
        schema="dbo",
        table="Users",
        estimated_rows=5000,
        column_count=2,
        should_analyze=True,
        sample_size=1000,
    )

    summary = analyzer.analyze_table(plan)

    assert summary.status == TableAnalysisStatus.COMPLETED
    assert summary.schema_name == "dbo"
    assert summary.table == "Users"
    assert summary.sample_size == 1000
    assert summary.returned_rows == 250
    assert summary.column_count == 2
    assert summary.profiled_columns == 2
    assert summary.classified_columns == 2
    assert summary.error_code is None
    assert summary.duration_ms >= 0
    assert summary.timings is not None


def test_table_analyzer_empty_table_skipped():
    mock_discovery = MagicMock()
    mock_profiler = MagicMock()
    mock_classifier = MagicMock()

    analyzer = TableAnalyzer(
        discovery=mock_discovery,
        profiler=mock_profiler,
        classifier=mock_classifier,
    )

    plan = TableAnalysisPlan(
        schema="dbo",
        table="EmptyTable",
        estimated_rows=0,
        column_count=4,
        should_analyze=False,
        sample_size=0,
        skip_reason="EMPTY_TABLE",
    )

    summary = analyzer.analyze_table(plan)

    assert summary.status == TableAnalysisStatus.SKIPPED
    assert summary.skip_reason == "EMPTY_TABLE"
    assert summary.sample_size == 0
    assert summary.returned_rows == 0
    assert summary.profiled_columns == 0
    assert summary.classified_columns == 0

    # Ensure no database calls were made for profiling/sampling
    mock_profiler.profile_table.assert_not_called()
    mock_classifier.classify_table.assert_not_called()


def test_table_analyzer_timeout_failure_isolated():
    mock_discovery = MagicMock()
    mock_discovery.get_columns.side_effect = SQLTimeoutError("Statement timed out")

    analyzer = TableAnalyzer(discovery=mock_discovery)

    plan = TableAnalysisPlan(
        schema="dbo",
        table="SlowTable",
        estimated_rows=1000000,
        column_count=10,
        should_analyze=True,
        sample_size=3000,
    )

    # Must NOT raise exception; must return FAILED summary with sanitized error
    summary = analyzer.analyze_table(plan)

    assert summary.status == TableAnalysisStatus.FAILED
    assert summary.error_code == "QUERY_TIMEOUT"
    assert "timeout" in summary.error_message.lower()


def test_table_analyzer_table_not_found_isolated():
    mock_discovery = MagicMock()
    mock_discovery.get_columns.side_effect = TableNotFoundError("dbo", "MissingTable")

    analyzer = TableAnalyzer(discovery=mock_discovery)

    plan = TableAnalysisPlan(
        schema="dbo",
        table="MissingTable",
        estimated_rows=100,
        column_count=2,
        should_analyze=True,
        sample_size=100,
    )

    summary = analyzer.analyze_table(plan)

    assert summary.status == TableAnalysisStatus.FAILED
    assert summary.error_code == "TABLE_NOT_FOUND"


def test_table_analyzer_unexpected_error_isolated():
    mock_discovery = MagicMock()
    mock_discovery.get_columns.side_effect = RuntimeError("Unexpected internal crash")

    analyzer = TableAnalyzer(discovery=mock_discovery)

    plan = TableAnalysisPlan(
        schema="dbo",
        table="CrashTable",
        estimated_rows=500,
        column_count=2,
        should_analyze=True,
        sample_size=500,
    )

    summary = analyzer.analyze_table(plan)

    assert summary.status == TableAnalysisStatus.FAILED
    assert summary.error_code == "UNEXPECTED_ERROR"


# ---------------------------------------------------------------------------
# 3. DATABASE ANALYZER TESTS
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_database_analyzer_all_successful():
    mock_discovery = MagicMock()
    mock_discovery.db_name = "AIRIS_TEST"
    mock_discovery.get_tables.return_value = TableListResponse(
        items=[
            TableInfo(schema="dbo", table="Table1", estimated_rows=1000, column_count=5),
            TableInfo(schema="dbo", table="Table2", estimated_rows=2000, column_count=8),
            TableInfo(schema="dbo", table="Empty1", estimated_rows=0, column_count=2),
        ],
        total=3,
        limit=10000,
        offset=0,
    )

    mock_table_analyzer = MagicMock()

    def mock_analyze(plan):
        if not plan.should_analyze:
            return TableAnalysisSummary(
                schema="dbo",
                table=plan.table,
                estimated_rows=0,
                status=TableAnalysisStatus.SKIPPED,
                skip_reason="EMPTY_TABLE",
                column_count=plan.column_count,
            )
        return TableAnalysisSummary(
            schema="dbo",
            table=plan.table,
            estimated_rows=plan.estimated_rows,
            status=TableAnalysisStatus.COMPLETED,
            sample_size=plan.sample_size,
            returned_rows=100,
            column_count=plan.column_count,
            profiled_columns=plan.column_count,
            classified_columns=plan.column_count,
            duration_ms=50.0,
        )

    mock_table_analyzer.analyze_table.side_effect = mock_analyze

    analyzer = DatabaseAnalyzer(
        discovery=mock_discovery,
        table_analyzer=mock_table_analyzer,
    )

    result: DatabaseAnalysisResponse = await analyzer.analyze_database()

    assert result.database == "AIRIS_TEST"
    assert result.status == AnalysisStatus.COMPLETED
    assert result.tables_total == 3
    assert result.tables_analyzed == 2
    assert result.tables_skipped == 1
    assert result.tables_failed == 0
    assert result.columns_discovered == 15
    assert result.columns_profiled == 13
    assert result.columns_classified == 13
    assert len(result.tables) == 3


@pytest.mark.asyncio
async def test_database_analyzer_failure_isolation():
    mock_discovery = MagicMock()
    mock_discovery.db_name = "AIRIS_TEST"
    mock_discovery.get_tables.return_value = TableListResponse(
        items=[
            TableInfo(schema="dbo", table="Good1", estimated_rows=1000, column_count=5),
            TableInfo(schema="dbo", table="FailingTable", estimated_rows=5000, column_count=6),
            TableInfo(schema="dbo", table="Good2", estimated_rows=2000, column_count=4),
        ],
        total=3,
        limit=10000,
        offset=0,
    )

    mock_table_analyzer = MagicMock()

    def mock_analyze(plan):
        if plan.table == "FailingTable":
            return TableAnalysisSummary(
                schema="dbo",
                table=plan.table,
                estimated_rows=plan.estimated_rows,
                status=TableAnalysisStatus.FAILED,
                error_code="QUERY_TIMEOUT",
                error_message="Table analysis timed out",
                column_count=plan.column_count,
            )
        return TableAnalysisSummary(
            schema="dbo",
            table=plan.table,
            estimated_rows=plan.estimated_rows,
            status=TableAnalysisStatus.COMPLETED,
            sample_size=plan.sample_size,
            returned_rows=100,
            column_count=plan.column_count,
            profiled_columns=plan.column_count,
            classified_columns=plan.column_count,
            duration_ms=40.0,
        )

    mock_table_analyzer.analyze_table.side_effect = mock_analyze

    analyzer = DatabaseAnalyzer(
        discovery=mock_discovery,
        table_analyzer=mock_table_analyzer,
    )

    result = await analyzer.analyze_database()

    # Database analysis continues and finishes with COMPLETED_WITH_ERRORS
    assert result.status == AnalysisStatus.COMPLETED_WITH_ERRORS
    assert result.tables_total == 3
    assert result.tables_analyzed == 2
    assert result.tables_failed == 1
    assert result.tables_skipped == 0

    failed_tables = [t for t in result.tables if t.status == TableAnalysisStatus.FAILED]
    assert len(failed_tables) == 1
    assert failed_tables[0].table == "FailingTable"
    assert failed_tables[0].error_code == "QUERY_TIMEOUT"


@pytest.mark.asyncio
async def test_database_analyzer_all_failed():
    mock_discovery = MagicMock()
    mock_discovery.db_name = "AIRIS_TEST"
    mock_discovery.get_tables.return_value = TableListResponse(
        items=[
            TableInfo(schema="dbo", table="Bad1", estimated_rows=1000, column_count=5),
            TableInfo(schema="dbo", table="Bad2", estimated_rows=2000, column_count=8),
        ],
        total=2,
        limit=10000,
        offset=0,
    )

    mock_table_analyzer = MagicMock()
    mock_table_analyzer.analyze_table.return_value = TableAnalysisSummary(
        schema="dbo",
        table="Bad",
        estimated_rows=1000,
        status=TableAnalysisStatus.FAILED,
        error_code="DATABASE_ERROR",
        error_message="Connection lost",
        column_count=5,
    )

    analyzer = DatabaseAnalyzer(
        discovery=mock_discovery,
        table_analyzer=mock_table_analyzer,
    )

    result = await analyzer.analyze_database()
    assert result.status == AnalysisStatus.FAILED
    assert result.tables_analyzed == 0
    assert result.tables_failed == 2


@pytest.mark.asyncio
async def test_database_analyzer_progress_callback():
    mock_discovery = MagicMock()
    mock_discovery.db_name = "AIRIS_TEST"
    mock_discovery.get_tables.return_value = TableListResponse(
        items=[
            TableInfo(schema="dbo", table="T1", estimated_rows=100, column_count=2),
            TableInfo(schema="dbo", table="T2", estimated_rows=200, column_count=3),
            TableInfo(schema="dbo", table="T3", estimated_rows=0, column_count=1),
        ],
        total=3,
        limit=10000,
        offset=0,
    )

    mock_table_analyzer = MagicMock()
    mock_table_analyzer.analyze_table.return_value = TableAnalysisSummary(
        schema="dbo",
        table="T",
        estimated_rows=100,
        status=TableAnalysisStatus.COMPLETED,
        column_count=2,
    )

    progress_updates = []

    def callback(progress):
        progress_updates.append(progress)

    analyzer = DatabaseAnalyzer(
        discovery=mock_discovery,
        table_analyzer=mock_table_analyzer,
    )

    result = await analyzer.analyze_database(progress_callback=callback)

    assert len(progress_updates) == 3
    assert progress_updates[-1].progress_percent == 100.0


# ---------------------------------------------------------------------------
# 4. API ROUTE TESTS
# ---------------------------------------------------------------------------


def test_api_quick_analysis_endpoint():
    mock_response = DatabaseAnalysisResponse(
        database="AIRIS_TEST",
        status=AnalysisStatus.COMPLETED,
        tables_total=2,
        tables_analyzed=2,
        tables_skipped=0,
        tables_failed=0,
        columns_discovered=10,
        columns_profiled=10,
        columns_classified=10,
        started_at="2026-08-14T12:00:00Z",
        completed_at="2026-08-14T12:00:01Z",
        duration_ms=1000.0,
        tables=[
            TableAnalysisSummary(
                schema="dbo",
                table="Users",
                estimated_rows=100,
                status=TableAnalysisStatus.COMPLETED,
                sample_size=100,
                returned_rows=100,
                column_count=5,
                profiled_columns=5,
                classified_columns=5,
                duration_ms=500.0,
            )
        ],
    )

    with patch.object(
        DatabaseAnalyzer, "analyze_database", new_callable=AsyncMock
    ) as mock_analyze:
        mock_analyze.return_value = mock_response

        response = client.post("/api/v1/analysis/quick", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "AIRIS_TEST"
        assert data["status"] == "COMPLETED"
        assert data["tables_total"] == 2
        assert data["tables_analyzed"] == 2
        assert len(data["tables"]) == 1


def test_api_quick_analysis_with_schema_filter():
    mock_response = DatabaseAnalysisResponse(
        database="AIRIS_TEST",
        status=AnalysisStatus.COMPLETED,
        tables_total=1,
        tables_analyzed=1,
        tables_skipped=0,
        tables_failed=0,
        columns_discovered=5,
        columns_profiled=5,
        columns_classified=5,
        started_at="2026-08-14T12:00:00Z",
        completed_at="2026-08-14T12:00:01Z",
        duration_ms=500.0,
        tables=[],
    )

    with patch.object(
        DatabaseAnalyzer, "analyze_database", new_callable=AsyncMock
    ) as mock_analyze:
        mock_analyze.return_value = mock_response

        response = client.post(
            "/api/v1/analysis/quick",
            json={"schema": "dbo"},
        )

        assert response.status_code == 200
        mock_analyze.assert_awaited_once_with(schema="dbo", max_concurrent=None)
