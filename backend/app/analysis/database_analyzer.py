import asyncio
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime

from app.analysis.planner import AnalysisPlanner
from app.analysis.table_analyzer import TableAnalyzer
from app.core.config import Settings
from app.core.config import settings as global_settings
from app.core.logging import log_event
from app.discovery.metadata import MetadataDiscovery
from app.schemas.analysis import (
    AnalysisProgress,
    AnalysisStatus,
    DatabaseAnalysisResponse,
    TableAnalysisPlan,
    TableAnalysisStatus,
    TableAnalysisSummary,
)

logger = logging.getLogger(__name__)


class DatabaseAnalyzer:
    """
    Database-wide analysis orchestrator.
    Coordinates table discovery, planning, bounded worker concurrency,
    isolated execution of V1-V5 services per table, and database-level summary reporting.
    """

    def __init__(
        self,
        discovery: MetadataDiscovery | None = None,
        planner: AnalysisPlanner | None = None,
        table_analyzer: TableAnalyzer | None = None,
        config: Settings | None = None,
    ):
        self.settings = config or global_settings
        self.discovery = discovery or MetadataDiscovery()
        self.planner = planner or AnalysisPlanner(config=self.settings)
        self.table_analyzer = table_analyzer or TableAnalyzer(discovery=self.discovery)

    async def analyze_database(
        self,
        schema: str | None = None,
        max_concurrent: int | None = None,
        progress_callback: Callable[[AnalysisProgress], None] | None = None,
    ) -> DatabaseAnalysisResponse:
        """
        Executes database-wide quick analysis orchestration.
        Safe, read-only, failure-isolated, and bounded in concurrency.
        """
        started_at = datetime.now(UTC)
        t_start = time.perf_counter()

        # 1. Discover all tables (fetch up to 10,000 to cover all DB tables without truncation)
        tables_response = self.discovery.get_tables(schema=schema, limit=10000)

        # 2. Formulate database analysis plan
        plan = self.planner.create_database_plan(
            tables=tables_response.items,
            database_name=self.discovery.db_name,
            schema_filter=schema,
        )

        total_tables = plan.total_tables

        # 3. Determine concurrency limit safely within connection pool bounds
        requested_concurrency = max_concurrent or self.settings.ANALYSIS_MAX_CONCURRENT_TABLES
        pool_safe_limit = max(1, self.settings.MSSQL_POOL_SIZE - 1)
        concurrency = min(requested_concurrency, pool_safe_limit)

        log_event(
            "analysis.database.started",
            database=plan.database,
            tables_total=total_tables,
            planned_tables=plan.planned_tables,
            skipped_tables=plan.skipped_tables,
            concurrency=concurrency,
        )

        # 4. Concurrency management with asyncio Semaphore
        semaphore = asyncio.Semaphore(concurrency)
        completed_count = 0
        failed_count = 0
        skipped_count = 0

        async def _run_table_plan(table_plan: TableAnalysisPlan) -> TableAnalysisSummary:
            nonlocal completed_count, failed_count, skipped_count
            async with semaphore:
                # Execute blocking DB/Polars profiling in threadpool
                result: TableAnalysisSummary = await asyncio.to_thread(
                    self.table_analyzer.analyze_table, table_plan
                )

                if result.status == TableAnalysisStatus.COMPLETED:
                    completed_count += 1
                elif result.status == TableAnalysisStatus.FAILED:
                    failed_count += 1
                elif result.status == TableAnalysisStatus.SKIPPED:
                    skipped_count += 1

                if progress_callback:
                    processed = completed_count + failed_count + skipped_count
                    pct = round((processed / total_tables * 100), 2) if total_tables > 0 else 100.0
                    progress = AnalysisProgress(
                        tables_total=total_tables,
                        tables_completed=completed_count,
                        tables_failed=failed_count,
                        tables_skipped=skipped_count,
                        progress_percent=pct,
                    )
                    try:
                        progress_callback(progress)
                    except Exception as pe:
                        logger.warning(f"Error in progress callback: {pe}")

                return result

        # 5. Launch all table analyses concurrently respecting bounded semaphore
        if plan.table_plans:
            table_results = await asyncio.gather(*[_run_table_plan(tp) for tp in plan.table_plans])
        else:
            table_results = []

        # 6. Database summary calculations
        completed_at = datetime.now(UTC)
        duration_ms = round((time.perf_counter() - t_start) * 1000, 2)

        tables_analyzed = sum(1 for r in table_results if r.status == TableAnalysisStatus.COMPLETED)
        tables_skipped = sum(1 for r in table_results if r.status == TableAnalysisStatus.SKIPPED)
        tables_failed = sum(1 for r in table_results if r.status == TableAnalysisStatus.FAILED)

        columns_discovered = sum(r.column_count for r in table_results)
        columns_profiled = sum(r.profiled_columns for r in table_results)
        columns_classified = sum(r.classified_columns for r in table_results)

        # Status determination
        if tables_failed == 0:
            status = AnalysisStatus.COMPLETED
        elif tables_analyzed > 0:
            status = AnalysisStatus.COMPLETED_WITH_ERRORS
        elif total_tables > tables_skipped:
            status = AnalysisStatus.FAILED
        else:
            status = AnalysisStatus.COMPLETED

        response = DatabaseAnalysisResponse(
            database=plan.database,
            status=status,
            tables_total=total_tables,
            tables_analyzed=tables_analyzed,
            tables_skipped=tables_skipped,
            tables_failed=tables_failed,
            columns_discovered=columns_discovered,
            columns_profiled=columns_profiled,
            columns_classified=columns_classified,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            tables=table_results,
        )

        log_event(
            "analysis.database.completed",
            database=plan.database,
            status=status.value,
            duration_ms=duration_ms,
            tables_analyzed=tables_analyzed,
            tables_skipped=tables_skipped,
            tables_failed=tables_failed,
            columns_profiled=columns_profiled,
            columns_classified=columns_classified,
        )

        return response
