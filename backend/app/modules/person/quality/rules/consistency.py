from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.person.quality.models import (
    QualityCategory,
    QualityFinding,
    QualityFindingStatus,
    QualitySeverity,
)
from app.modules.person.quality.rules.base import PersonQualityRule


class PersonSelfRelationshipRule(PersonQualityRule):
    rule_code = "PERSON_SELF_RELATIONSHIP"
    category = QualityCategory.CONSISTENCY
    severity = QualitySeverity.HIGH
    title = "Self-referencing relationships"
    description = "Detects relationship records where a person is defined as in a relationship with themselves (PersonID = RelatedPersonID)."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonrelationdet" not in tables_map:
            return False, "Relationship table 'dbo.DLPersonRelationDet' missing."
        cols = tables_map["dlpersonrelationdet"].get("columns", [])
        if "relatedpersonid" not in [c.lower() for c in cols]:
            return False, "Column 'RelatedPersonID' missing from Relationship table."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_relationships,
            SUM(CASE WHEN r.PersonID = r.RelatedPersonID THEN 1 ELSE 0 END) AS self_relationships
        FROM dbo.DLPersonRelationDet r
        JOIN dbo.DLPersonMst p ON r.PersonID = p.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0 AND r.PersonID IS NOT NULL AND r.RelatedPersonID IS NOT NULL;
        """
        rows = execute_readonly_query(query)
        total = int(rows[0].get("total_relationships") or 0)
        self_rel = int(rows[0].get("self_relationships") or 0)
        pct = round((self_rel / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=self_rel,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{self_rel:,} out of {total:,} active person relationship records ({pct}%) are self-referencing anomalies.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonCreatedAfterUpdatedRule(PersonQualityRule):
    rule_code = "PERSON_CREATED_AFTER_UPDATED"
    category = QualityCategory.CONSISTENCY
    severity = QualitySeverity.LOW
    title = "Creation timestamp after update timestamp"
    description = "Detects master person records where the creation timestamp is chronologically after the last modified timestamp."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        cols = tables_map["dlpersonmst"].get("columns", [])
        col_names = [c.lower() for c in cols]
        if "personentdt" not in col_names or "personupddt" not in col_names:
            return (
                False,
                "Timestamp columns 'PersonEntDt' or 'PersonUpdDt' missing from master table.",
            )
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_timestamped,
            SUM(CASE WHEN PersonEntDt > PersonUpdDt THEN 1 ELSE 0 END) AS invalid_timestamps
        FROM dbo.DLPersonMst
        WHERE PersonIsActive = 1 AND ISNULL(PersonIsDeleted, 0) = 0 AND PersonEntDt IS NOT NULL AND PersonUpdDt IS NOT NULL;
        """
        rows = execute_readonly_query(query)
        total = int(rows[0].get("total_timestamped") or 0)
        invalid = int(rows[0].get("invalid_timestamps") or 0)
        pct = round((invalid / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=invalid,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{invalid:,} out of {total:,} timestamped person records ({pct}%) have creation dates after update dates.",
            status=QualityFindingStatus.APPLIED,
        )
