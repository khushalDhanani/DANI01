import logging
import time
from typing import Any

from app.db.mssql import execute_readonly_query
from app.discovery.metadata import MetadataDiscovery
from app.modules.definitions.person import PersonModuleDefinition
from app.modules.person.queries import (
    build_child_table_counts_query,
    build_person_metrics_query,
)
from app.modules.person.schemas import (
    PersonMetricsSummary,
    PersonModuleMetricsResponse,
)

logger = logging.getLogger(__name__)


def safe_percent(numerator: int | None, denominator: int | None) -> float | None:
    """Safely calculates percentage with division-by-zero protection."""
    if numerator is None or denominator is None or denominator <= 0:
        return 0.0 if numerator is not None and denominator == 0 else None
    return round((numerator / denominator) * 100, 2)


class PersonMetricsService:
    """
    Computes domain aggregate metrics for the PERSON module using set-based MSSQL queries.
    """

    def __init__(self, discovery: MetadataDiscovery | None = None) -> None:
        self.discovery = discovery or MetadataDiscovery()

    async def calculate_metrics(self) -> PersonModuleMetricsResponse:
        start_time = time.perf_counter()
        warnings: list[str] = []

        definition = PersonModuleDefinition
        root_schema = definition.root_schema
        root_table = definition.root_table
        full_root_table = f"{root_schema}.{root_table}"

        # 1. Verify Root Table
        try:
            root_struct = self.discovery.get_table_structure(root_schema, root_table)
            root_cols = {c.name.lower() for c in root_struct.columns}
            has_active_col = "personisactive" in root_cols
            has_deleted_col = "personisdeleted" in root_cols
            has_temp_col = "personistemp" in root_cols
            has_blacklist_col = "personisblacklist" in root_cols
        except Exception as e:
            return PersonModuleMetricsResponse(
                module="PERSON",
                status="FAILED",
                root_entity=full_root_table,
                metrics=PersonMetricsSummary(total_persons=0),
                warnings=[f"Root entity '{full_root_table}' could not be accessed: {e}"],
                duration_ms=0.0,
            )

        # 2. Check Optional Child Tables
        tables_map = {t.table_name.lower(): t for t in definition.tables}

        def resolve_child_table(table_name: str) -> str | None:
            t_def = tables_map.get(table_name.lower())
            if not t_def:
                return None
            try:
                self.discovery.get_table_structure(t_def.schema_name, t_def.table_name)
                return f"{t_def.schema_name}.{t_def.table_name}"
            except Exception:
                warnings.append(f"Optional table '{t_def.schema_name}.{t_def.table_name}' is missing; corresponding metrics will be unavailable.")
                return None

        address_tbl = resolve_child_table("DLPersonAddressDet")
        contact_tbl = resolve_child_table("DLPersonPhoneEmailURLDet")

        # 3. Build & Execute Person Aggregate Query
        agg_sql = build_person_metrics_query(
            root_table=full_root_table,
            root_key=definition.root_key,
            has_active_col=has_active_col,
            has_deleted_col=has_deleted_col,
            has_temp_col=has_temp_col,
            has_blacklist_col=has_blacklist_col,
        )

        try:
            agg_results = execute_readonly_query(agg_sql)
            row: dict[str, Any] = agg_results[0] if agg_results else {}
        except Exception as e:
            logger.error(f"Error executing person aggregate query: {e}")
            return PersonModuleMetricsResponse(
                module="PERSON",
                status="FAILED",
                root_entity=full_root_table,
                metrics=PersonMetricsSummary(total_persons=0),
                warnings=[f"Database query failed: {e}"],
                duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
            )

        child_counts: dict[str, Any] = {}

        # 5. Process Metrics & Percentages
        total_persons = int(row.get("total_persons") or 0)
        active_persons = row.get("active_persons")
        inactive_persons = row.get("inactive_persons")
        deleted_persons = row.get("deleted_persons")
        temp_persons = row.get("temp_persons")
        blacklist_persons = row.get("blacklist_persons")

        active_cnt = int(active_persons) if active_persons is not None else None
        inactive_cnt = int(inactive_persons) if inactive_persons is not None else None
        deleted_cnt = int(deleted_persons) if deleted_persons is not None else None
        temp_cnt = int(temp_persons) if temp_persons is not None else None
        blacklist_cnt = int(blacklist_persons) if blacklist_persons is not None else None


        summary = PersonMetricsSummary(
            total_persons=total_persons,
            active_persons=active_cnt,
            inactive_persons=inactive_cnt,
            active_percent=safe_percent(active_cnt, total_persons),
            inactive_percent=safe_percent(inactive_cnt, total_persons),
            deleted_persons=deleted_cnt,
            deleted_percent=safe_percent(deleted_cnt, total_persons),
            temp_persons=temp_cnt,
            temp_percent=safe_percent(temp_cnt, total_persons),
            blacklist_persons=blacklist_cnt,
            blacklist_percent=safe_percent(blacklist_cnt, total_persons),

            # Business Mappings: PersonIsVisitor_Contact (1=Visitor, 2=Contact)
            visitor_count=int(row.get("visitor_count") or 0),
            visitor_percent=safe_percent(int(row.get("visitor_count") or 0), total_persons),
            contact_entity_count=int(row.get("contact_entity_count") or 0),
            contact_entity_percent=safe_percent(int(row.get("contact_entity_count") or 0), total_persons),

            # Business Mappings: PersonIsShareContact (0=Private, 1=Public)
            public_count=int(row.get("public_count") or 0),
            public_percent=safe_percent(int(row.get("public_count") or 0), total_persons),
            private_count=int(row.get("private_count") or 0),
            private_percent=safe_percent(int(row.get("private_count") or 0), total_persons),


        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        status = "DEGRADED" if warnings else "COMPLETED"

        return PersonModuleMetricsResponse(
            module="PERSON",
            status=status,
            root_entity=full_root_table,
            metrics=summary,
            warnings=warnings,
            duration_ms=round(duration_ms, 2),
        )
