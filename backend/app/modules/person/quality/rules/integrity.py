from typing import Any

from app.db import mssql
from app.modules.person.quality.models import (
    QualityCategory,
    QualityFinding,
    QualityFindingStatus,
    QualitySeverity,
)
from app.modules.person.quality.rules.base import PersonQualityRule


class PersonOrphanAddressRule(PersonQualityRule):
    rule_code = "PERSON_ORPHAN_ADDRESS"
    category = QualityCategory.INTEGRITY
    severity = QualitySeverity.CRITICAL
    title = "Orphaned address records"
    description = "Detects address records whose foreign PersonID does not reference any existing master person entity."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        if "dlpersonaddressdet" not in tables_map:
            return False, "Address table 'dbo.DLPersonAddressDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_addresses,
            SUM(CASE WHEN p.PersonID IS NULL THEN 1 ELSE 0 END) AS orphan_addresses
        FROM dbo.DLPersonAddressDet a
        LEFT JOIN dbo.DLPersonMst p ON a.PersonID = p.PersonID
        WHERE a.PersonID IS NOT NULL;
        """
        rows = mssql.execute_readonly_query(query)
        total = int(rows[0].get("total_addresses") or 0)
        orphans = int(rows[0].get("orphan_addresses") or 0)
        pct = round((orphans / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=orphans,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{orphans:,} out of {total:,} address records ({pct}%) are orphaned without parent persons.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonOrphanContactRule(PersonQualityRule):
    rule_code = "PERSON_ORPHAN_CONTACT"
    category = QualityCategory.INTEGRITY
    severity = QualitySeverity.CRITICAL
    title = "Orphaned contact records"
    description = "Detects contact communication records whose foreign PersonID does not reference any existing master person entity."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        if "dlpersonphoneemailurldet" not in tables_map:
            return False, "Contact table 'dbo.DLPersonPhoneEmailURLDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_contacts,
            SUM(CASE WHEN p.PersonID IS NULL THEN 1 ELSE 0 END) AS orphan_contacts
        FROM dbo.DLPersonPhoneEmailURLDet c
        LEFT JOIN dbo.DLPersonMst p ON c.PersionID = p.PersonID
        WHERE c.PersionID IS NOT NULL;
        """
        rows = mssql.execute_readonly_query(query)
        total = int(rows[0].get("total_contacts") or 0)
        orphans = int(rows[0].get("orphan_contacts") or 0)
        pct = round((orphans / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=orphans,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{orphans:,} out of {total:,} contact records ({pct}%) are orphaned without parent persons.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonOrphanCompanyLinkRule(PersonQualityRule):
    rule_code = "PERSON_ORPHAN_COMPANY_LINK"
    category = QualityCategory.INTEGRITY
    severity = QualitySeverity.CRITICAL
    title = "Orphaned company link records"
    description = "Detects company affiliation links whose foreign PersonID does not reference any existing master person entity."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        if "dlpersoncompanylinkdet" not in tables_map:
            return False, "Company link table 'dbo.DLPersonCompanyLinkDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_company_links,
            SUM(CASE WHEN p.PersonID IS NULL THEN 1 ELSE 0 END) AS orphan_company_links
        FROM dbo.DLPersonCompanyLinkDet cl
        LEFT JOIN dbo.DLPersonMst p ON cl.PersonID = p.PersonID
        WHERE cl.PersonID IS NOT NULL;
        """
        rows = mssql.execute_readonly_query(query)
        total = int(rows[0].get("total_company_links") or 0)
        orphans = int(rows[0].get("orphan_company_links") or 0)
        pct = round((orphans / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=orphans,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{orphans:,} out of {total:,} company link records ({pct}%) are orphaned without parent persons.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonOrphanRelationshipRule(PersonQualityRule):
    rule_code = "PERSON_ORPHAN_RELATIONSHIP"
    category = QualityCategory.INTEGRITY
    severity = QualitySeverity.CRITICAL
    title = "Orphaned relationship records"
    description = "Detects inter-personal relationships whose foreign PersonID or RelatedPersonID references non-existent persons."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        if "dlpersonrelationdet" not in tables_map:
            return False, "Relationship table 'dbo.DLPersonRelationDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_relationships,
            SUM(CASE WHEN p1.PersonID IS NULL OR (r.RelatedPersonID IS NOT NULL AND p2.PersonID IS NULL) THEN 1 ELSE 0 END) AS orphan_relationships
        FROM dbo.DLPersonRelationDet r
        LEFT JOIN dbo.DLPersonMst p1 ON r.PersonID = p1.PersonID
        LEFT JOIN dbo.DLPersonMst p2 ON r.RelatedPersonID = p2.PersonID
        WHERE r.PersonID IS NOT NULL;
        """
        rows = mssql.execute_readonly_query(query)
        total = int(rows[0].get("total_relationships") or 0)
        orphans = int(rows[0].get("orphan_relationships") or 0)
        pct = round((orphans / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=orphans,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{orphans:,} out of {total:,} relationship records ({pct}%) are orphaned without valid parent persons.",
            status=QualityFindingStatus.APPLIED,
        )
