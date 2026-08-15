import logging

from app.core.config import Settings
from app.core.config import settings as global_settings
from app.schemas.analysis import AnalysisPlan, TableAnalysisPlan, TableSkipReason
from app.schemas.database import TableInfo

logger = logging.getLogger(__name__)


class AnalysisPlanner:
    """
    Responsible for formulating an analysis plan per table and database-wide.
    Determines sample sizes based on estimated row counts and configured thresholds.
    Ensures empty tables are safely skipped without SQL sampling or Polars execution.
    """

    def __init__(self, config: Settings | None = None):
        self.settings = config or global_settings

    def determine_table_plan(self, table: TableInfo) -> TableAnalysisPlan:
        """Determines the analysis plan and sampling size for a single table."""
        estimated_rows = table.estimated_rows

        if estimated_rows <= 0:
            return TableAnalysisPlan(
                schema_name=table.schema_name,
                table=table.table,
                estimated_rows=0,
                column_count=table.column_count,
                should_analyze=False,
                sample_size=0,
                priority=1,
                skip_reason=TableSkipReason.EMPTY_TABLE.value,
            )

        # Determine sample size by row count tiers
        if estimated_rows <= self.settings.ANALYSIS_TINY_TABLE_MAX_ROWS:
            target_sample = self.settings.ANALYSIS_SAMPLE_TINY
        elif estimated_rows <= self.settings.ANALYSIS_SMALL_TABLE_MAX_ROWS:
            target_sample = self.settings.ANALYSIS_SAMPLE_SMALL
        elif estimated_rows <= self.settings.ANALYSIS_MEDIUM_TABLE_MAX_ROWS:
            target_sample = self.settings.ANALYSIS_SAMPLE_MEDIUM
        elif estimated_rows <= self.settings.ANALYSIS_LARGE_TABLE_MAX_ROWS:
            target_sample = self.settings.ANALYSIS_SAMPLE_LARGE
        else:
            target_sample = self.settings.ANALYSIS_SAMPLE_VERY_LARGE

        # Ensure sample does not exceed global profile limit or table's estimated rows if tiny
        clamped_sample = min(target_sample, self.settings.PROFILE_MAX_SAMPLE_SIZE)

        return TableAnalysisPlan(
            schema_name=table.schema_name,
            table=table.table,
            estimated_rows=estimated_rows,
            column_count=table.column_count,
            should_analyze=True,
            sample_size=clamped_sample,
            priority=1,
            skip_reason=None,
        )

    def create_database_plan(
        self,
        tables: list[TableInfo],
        database_name: str | None = None,
        schema_filter: str | None = None,
    ) -> AnalysisPlan:
        """Formulates database-wide execution plan across discovered tables."""
        db_name = database_name or self.settings.MSSQL_DATABASE

        # Optional schema filtering
        if schema_filter:
            target_tables = [t for t in tables if t.schema_name.lower() == schema_filter.lower()]
        else:
            target_tables = tables

        table_plans: list[TableAnalysisPlan] = []
        planned_count = 0
        skipped_count = 0

        for table in target_tables:
            plan = self.determine_table_plan(table)
            table_plans.append(plan)
            if plan.should_analyze:
                planned_count += 1
            else:
                skipped_count += 1

        return AnalysisPlan(
            database=db_name,
            total_tables=len(table_plans),
            planned_tables=planned_count,
            skipped_tables=skipped_count,
            table_plans=table_plans,
        )
