import logging
import time

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from app.classification.classifier import TableClassifier
from app.core.exceptions import (
    DatabaseConnectionError,
    DiscoveryError,
    TableNotFoundError,
)
from app.core.logging import log_event
from app.discovery.metadata import MetadataDiscovery
from app.profiling.profiler import TableProfiler
from app.sampling.sampler import TableSampler
from app.schemas.analysis import (
    TableAnalysisPlan,
    TableAnalysisStatus,
    TableAnalysisSummary,
    TableAnalysisTimings,
)

logger = logging.getLogger(__name__)


class TableAnalyzer:
    """
    Executes the analysis pipeline for a single table:
    1. Structural discovery (columns, types, constraints)
    2. Safe bounded TOP N sampling & Polars profiling
    3. Semantic classification & sensitivity rating

    Provides strict failure isolation — an error on one table is captured and sanitized,
    never crashing the wider database analysis.
    """

    def __init__(
        self,
        discovery: MetadataDiscovery | None = None,
        sampler: TableSampler | None = None,
        profiler: TableProfiler | None = None,
        classifier: TableClassifier | None = None,
    ):
        self.discovery = discovery or MetadataDiscovery()
        self.sampler = sampler or TableSampler(discovery=self.discovery)
        self.profiler = profiler or TableProfiler(sampler=self.sampler, discovery=self.discovery)
        self.classifier = classifier or TableClassifier(discovery=self.discovery)

    def analyze_table(self, plan: TableAnalysisPlan) -> TableAnalysisSummary:
        """Analyzes a single table with timing metrics and complete failure isolation."""
        t_start = time.perf_counter()
        schema = plan.schema_name
        table = plan.table

        # 1. Check if table should be skipped (e.g. empty table)
        if not plan.should_analyze:
            duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
            log_event(
                "analysis.table.skipped",
                schema=schema,
                table=table,
                skip_reason=plan.skip_reason,
                estimated_rows=plan.estimated_rows,
            )
            return TableAnalysisSummary(
                schema_name=schema,
                table=table,
                estimated_rows=plan.estimated_rows,
                status=TableAnalysisStatus.SKIPPED,
                skip_reason=plan.skip_reason,
                sample_size=0,
                returned_rows=0,
                column_count=plan.column_count,
                profiled_columns=0,
                classified_columns=0,
                duration_ms=duration_ms,
                timings=TableAnalysisTimings(total_duration_ms=duration_ms),
            )

        log_event(
            "analysis.table.started",
            schema=schema,
            table=table,
            sample_size=plan.sample_size,
            estimated_rows=plan.estimated_rows,
        )

        timings = TableAnalysisTimings()

        try:
            # Step 1: Structural Metadata Discovery
            t_struct = time.perf_counter()
            columns_meta = self.discovery.get_columns(schema, table)
            timings.structure_duration_ms = round((time.perf_counter() - t_struct) * 1000, 2)
            column_count = len(columns_meta)

            # Step 2: Sampling & Polars Profiling
            t_prof = time.perf_counter()
            profile_response = self.profiler.profile_table(schema, table, limit=plan.sample_size)
            timings.profiling_duration_ms = round((time.perf_counter() - t_prof) * 1000, 2)

            # Step 3: Semantic Classification
            t_class = time.perf_counter()
            classification_response = self.classifier.classify_table(schema, table)
            timings.classification_duration_ms = round((time.perf_counter() - t_class) * 1000, 2)

            # Calculate total duration
            total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
            timings.total_duration_ms = total_duration_ms

            summary = TableAnalysisSummary(
                schema_name=schema,
                table=table,
                estimated_rows=plan.estimated_rows,
                status=TableAnalysisStatus.COMPLETED,
                sample_size=profile_response.sample_size,
                returned_rows=profile_response.returned_rows,
                column_count=column_count,
                profiled_columns=len(profile_response.columns),
                classified_columns=len(classification_response.columns),
                duration_ms=total_duration_ms,
                timings=timings,
                profile_response=profile_response,
                classification_response=classification_response,
            )

            log_event(
                "analysis.table.completed",
                schema=schema,
                table=table,
                status="COMPLETED",
                returned_rows=summary.returned_rows,
                duration_ms=total_duration_ms,
            )
            return summary

        except (SQLTimeoutError, TimeoutError):
            total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
            timings.total_duration_ms = total_duration_ms
            error_code = "QUERY_TIMEOUT"
            error_msg = f"Table analysis exceeded query timeout on '{schema}.{table}'."
            log_event(
                "analysis.table.failed",
                level=logging.ERROR,
                schema=schema,
                table=table,
                error_code=error_code,
                duration_ms=total_duration_ms,
            )
            return TableAnalysisSummary(
                schema_name=schema,
                table=table,
                estimated_rows=plan.estimated_rows,
                status=TableAnalysisStatus.FAILED,
                column_count=plan.column_count,
                duration_ms=total_duration_ms,
                timings=timings,
                error_code=error_code,
                error_message=error_msg,
            )

        except TableNotFoundError:
            total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
            timings.total_duration_ms = total_duration_ms
            error_code = "TABLE_NOT_FOUND"
            error_msg = f"Table '{schema}.{table}' could not be located in database."
            log_event(
                "analysis.table.failed",
                level=logging.ERROR,
                schema=schema,
                table=table,
                error_code=error_code,
                duration_ms=total_duration_ms,
            )
            return TableAnalysisSummary(
                schema_name=schema,
                table=table,
                estimated_rows=plan.estimated_rows,
                status=TableAnalysisStatus.FAILED,
                column_count=plan.column_count,
                duration_ms=total_duration_ms,
                timings=timings,
                error_code=error_code,
                error_message=error_msg,
            )

        except (DiscoveryError, DatabaseConnectionError, SQLAlchemyError) as e:
            total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
            timings.total_duration_ms = total_duration_ms
            error_code = "DATABASE_ERROR"
            error_msg = f"Database operation failed during analysis of '{schema}.{table}'."
            logger.error(f"Database error analyzing table {schema}.{table}: {e}", exc_info=False)
            log_event(
                "analysis.table.failed",
                level=logging.ERROR,
                schema=schema,
                table=table,
                error_code=error_code,
                duration_ms=total_duration_ms,
            )
            return TableAnalysisSummary(
                schema_name=schema,
                table=table,
                estimated_rows=plan.estimated_rows,
                status=TableAnalysisStatus.FAILED,
                column_count=plan.column_count,
                duration_ms=total_duration_ms,
                timings=timings,
                error_code=error_code,
                error_message=error_msg,
            )

        except Exception as e:
            total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
            timings.total_duration_ms = total_duration_ms
            error_code = "UNEXPECTED_ERROR"
            error_msg = f"Unexpected error during analysis of '{schema}.{table}'."
            logger.error(
                f"Unexpected error analyzing table {schema}.{table}: {e}",
                exc_info=True,
            )
            log_event(
                "analysis.table.failed",
                level=logging.ERROR,
                schema=schema,
                table=table,
                error_code=error_code,
                duration_ms=total_duration_ms,
            )
            return TableAnalysisSummary(
                schema_name=schema,
                table=table,
                estimated_rows=plan.estimated_rows,
                status=TableAnalysisStatus.FAILED,
                column_count=plan.column_count,
                duration_ms=total_duration_ms,
                timings=timings,
                error_code=error_code,
                error_message=error_msg,
            )
