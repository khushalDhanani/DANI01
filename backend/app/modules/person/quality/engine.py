import logging
import time
from typing import Any

from app.discovery.metadata import MetadataDiscovery
from app.modules.definitions.person import PersonModuleDefinition
from app.modules.person.quality.models import (
    PersonQualityResponse,
    QualityFinding,
    QualityFindingStatus,
    QualitySeverity,
    QualitySeveritySummary,
)
from app.modules.person.quality.registry import (
    PersonQualityRuleRegistry,
    person_quality_rule_registry,
)

logger = logging.getLogger(__name__)


class PersonQualityEngine:
    """
    Quality evaluation orchestrator for the PERSON module.
    Evaluates business rules against MSSQL, isolates errors, and generates summary findings.
    """

    def __init__(
        self,
        discovery: MetadataDiscovery | None = None,
        registry: PersonQualityRuleRegistry | None = None,
    ) -> None:
        self.discovery = discovery or MetadataDiscovery()
        self.registry = registry or person_quality_rule_registry

    async def evaluate_quality(self) -> PersonQualityResponse:
        start_time = time.perf_counter()
        definition = PersonModuleDefinition

        # 1. Resolve Available Tables and Columns
        tables_map: dict[str, dict[str, Any]] = {}
        for t_def in definition.tables:
            try:
                struct = self.discovery.get_table_structure(t_def.schema_name, t_def.table_name)
                tables_map[t_def.table_name.lower()] = {
                    "schema": t_def.schema_name,
                    "table": t_def.table_name,
                    "columns": [c.name for c in struct.columns],
                }
            except Exception as e:
                logger.warning(
                    f"Quality engine could not load table '{t_def.schema_name}.{t_def.table_name}': {e}"
                )

        # 2. Iterate Rules
        rules = self.registry.get_all_rules()
        findings: list[QualityFinding] = []
        rules_evaluated = 0
        rules_skipped = 0

        for rule in rules:
            is_applicable, skip_reason = rule.check_applicability(tables_map)
            if not is_applicable:
                rules_skipped += 1
                findings.append(
                    rule.skipped_finding(skip_reason or "Required tables/columns missing.")
                )
                continue

            rules_evaluated += 1
            try:
                finding = rule.evaluate()
                findings.append(finding)
            except Exception as e:
                logger.error(f"Rule '{rule.rule_code}' evaluation error: {e}", exc_info=True)
                findings.append(rule.failed_finding(str(e)))

        # 3. Compute Severity Summary for active findings (affected_count > 0)
        critical_cnt = 0
        high_cnt = 0
        medium_cnt = 0
        low_cnt = 0
        active_findings_cnt = 0

        for f in findings:
            if f.status == QualityFindingStatus.APPLIED and f.affected_count > 0:
                active_findings_cnt += 1
                if f.severity == QualitySeverity.CRITICAL:
                    critical_cnt += 1
                elif f.severity == QualitySeverity.HIGH:
                    high_cnt += 1
                elif f.severity == QualitySeverity.MEDIUM:
                    medium_cnt += 1
                elif f.severity == QualitySeverity.LOW:
                    low_cnt += 1

        duration_ms = (time.perf_counter() - start_time) * 1000
        status = "DEGRADED" if rules_skipped > 0 else "COMPLETED"

        return PersonQualityResponse(
            module="PERSON",
            status=status,
            rules_evaluated=rules_evaluated,
            rules_skipped=rules_skipped,
            findings_count=active_findings_cnt,
            severity_summary=QualitySeveritySummary(
                critical=critical_cnt,
                high=high_cnt,
                medium=medium_cnt,
                low=low_cnt,
            ),
            findings=findings,
            duration_ms=round(duration_ms, 2),
        )
