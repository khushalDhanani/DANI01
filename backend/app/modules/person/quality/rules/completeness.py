from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.person.quality.models import (
    QualityCategory,
    QualityFinding,
    QualityFindingStatus,
    QualitySeverity,
)
from app.modules.person.quality.rules.base import PersonQualityRule


class PersonMissingAddressRule(PersonQualityRule):
    rule_code = "PERSON_MISSING_ADDRESS"
    category = QualityCategory.COMPLETENESS
    severity = QualitySeverity.HIGH
    title = "Active persons without address"
    description = "Checks the proportion of active master person records that have no associated address details."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        if "dlpersonaddressdet" not in tables_map:
            return False, "Address table 'dbo.DLPersonAddressDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        WITH DistinctAddresses AS (
            SELECT DISTINCT PersonID FROM dbo.DLPersonAddressDet WHERE PersonID IS NOT NULL
        )
        SELECT
            COUNT_BIG(1) AS total_active,
            SUM(CASE WHEN a.PersonID IS NULL THEN 1 ELSE 0 END) AS missing_addr
        FROM dbo.DLPersonMst p
        LEFT JOIN DistinctAddresses a ON p.PersonID = a.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0;
        """
        rows = execute_readonly_query(query)
        total = int(rows[0].get("total_active") or 0)
        missing = int(rows[0].get("missing_addr") or 0)
        pct = round((missing / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=missing,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{missing:,} out of {total:,} active persons ({pct}%) have no address record.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonMissingContactRule(PersonQualityRule):
    rule_code = "PERSON_MISSING_CONTACT"
    category = QualityCategory.COMPLETENESS
    severity = QualitySeverity.HIGH
    title = "Active persons without contact channels"
    description = "Checks active persons missing all forms of contact records (phone, email, etc.)."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        if "dlpersonphoneemailurldet" not in tables_map:
            return False, "Contact table 'dbo.DLPersonPhoneEmailURLDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        WITH DistinctContacts AS (
            SELECT DISTINCT PersionID AS PersonID FROM dbo.DLPersonPhoneEmailURLDet WHERE PersionID IS NOT NULL
        )
        SELECT
            COUNT_BIG(1) AS total_active,
            SUM(CASE WHEN c.PersonID IS NULL THEN 1 ELSE 0 END) AS missing_contact
        FROM dbo.DLPersonMst p
        LEFT JOIN DistinctContacts c ON p.PersonID = c.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0;
        """
        rows = execute_readonly_query(query)
        total = int(rows[0].get("total_active") or 0)
        missing = int(rows[0].get("missing_contact") or 0)
        pct = round((missing / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=missing,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{missing:,} out of {total:,} active persons ({pct}%) have no communication contact records.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonMissingEmailRule(PersonQualityRule):
    rule_code = "PERSON_MISSING_EMAIL"
    category = QualityCategory.COMPLETENESS
    severity = QualitySeverity.MEDIUM
    title = "Active persons without email address"
    description = "Checks active persons who do not have any registered email address."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        if "dlpersonphoneemailurldet" not in tables_map:
            return False, "Contact table 'dbo.DLPersonPhoneEmailURLDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        WITH DistinctEmails AS (
            SELECT DISTINCT PersionID AS PersonID FROM dbo.DLPersonPhoneEmailURLDet
            WHERE PersionID IS NOT NULL AND TypeValue LIKE '%@%'
        )
        SELECT
            COUNT_BIG(1) AS total_active,
            SUM(CASE WHEN e.PersonID IS NULL THEN 1 ELSE 0 END) AS missing_email
        FROM dbo.DLPersonMst p
        LEFT JOIN DistinctEmails e ON p.PersonID = e.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0;
        """
        rows = execute_readonly_query(query)
        total = int(rows[0].get("total_active") or 0)
        missing = int(rows[0].get("missing_email") or 0)
        pct = round((missing / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=missing,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{missing:,} out of {total:,} active persons ({pct}%) have no registered email address.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonMissingPhoneRule(PersonQualityRule):
    rule_code = "PERSON_MISSING_PHONE"
    category = QualityCategory.COMPLETENESS
    severity = QualitySeverity.LOW
    title = "Active persons without phone number"
    description = "Checks active persons who do not have any registered telephone or mobile number."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        if "dlpersonphoneemailurldet" not in tables_map:
            return False, "Contact table 'dbo.DLPersonPhoneEmailURLDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        WITH DistinctPhones AS (
            SELECT DISTINCT PersionID AS PersonID FROM dbo.DLPersonPhoneEmailURLDet
            WHERE PersionID IS NOT NULL
              AND TypeValue NOT LIKE '%@%'
              AND TypeValue NOT LIKE 'http%'
              AND TypeValue NOT LIKE 'www%'
        )
        SELECT
            COUNT_BIG(1) AS total_active,
            SUM(CASE WHEN ph.PersonID IS NULL THEN 1 ELSE 0 END) AS missing_phone
        FROM dbo.DLPersonMst p
        LEFT JOIN DistinctPhones ph ON p.PersonID = ph.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0;
        """
        rows = execute_readonly_query(query)
        total = int(rows[0].get("total_active") or 0)
        missing = int(rows[0].get("missing_phone") or 0)
        pct = round((missing / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=missing,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{missing:,} out of {total:,} active persons ({pct}%) have no telephone number.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonMissingCompanyLinkRule(PersonQualityRule):
    rule_code = "PERSON_MISSING_COMPANY_LINK"
    category = QualityCategory.COMPLETENESS
    severity = QualitySeverity.MEDIUM
    title = "Active persons without company link"
    description = (
        "Checks active persons who have no organization or corporate affiliation link records."
    )

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonmst" not in tables_map:
            return False, "Root table 'dbo.DLPersonMst' missing."
        if "dlpersoncompanylinkdet" not in tables_map:
            return False, "Company link table 'dbo.DLPersonCompanyLinkDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        WITH DistinctCompanyLinks AS (
            SELECT DISTINCT PersonID FROM dbo.DLPersonCompanyLinkDet WHERE PersonID IS NOT NULL
        )
        SELECT
            COUNT_BIG(1) AS total_active,
            SUM(CASE WHEN cl.PersonID IS NULL THEN 1 ELSE 0 END) AS missing_company
        FROM dbo.DLPersonMst p
        LEFT JOIN DistinctCompanyLinks cl ON p.PersonID = cl.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0;
        """
        rows = execute_readonly_query(query)
        total = int(rows[0].get("total_active") or 0)
        missing = int(rows[0].get("missing_company") or 0)
        pct = round((missing / total) * 100, 2) if total > 0 else 0.0

        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=missing,
            total_evaluated=total,
            affected_percent=pct,
            exact=True,
            message=f"{missing:,} out of {total:,} active persons ({pct}%) have no organization company links.",
            status=QualityFindingStatus.APPLIED,
        )
