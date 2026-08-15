from typing import Any

from app.db import mssql
from app.modules.person.quality.models import (
    QualityCategory,
    QualityFinding,
    QualityFindingStatus,
    QualitySeverity,
)
from app.modules.person.quality.rules.base import PersonQualityRule


class PersonInvalidEmailRule(PersonQualityRule):
    rule_code = "PERSON_INVALID_EMAIL"
    category = QualityCategory.VALIDITY
    severity = QualitySeverity.HIGH
    title = "Malformed email addresses"
    description = "Detects email contact records with invalid format patterns (missing domain structure or containing whitespace)."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonphoneemailurldet" not in tables_map:
            return False, "Contact table 'dbo.DLPersonPhoneEmailURLDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_emails,
            SUM(CASE WHEN c.TypeValue NOT LIKE '%_@_%._%' OR c.TypeValue LIKE '% %' THEN 1 ELSE 0 END) AS invalid_emails
        FROM dbo.DLPersonPhoneEmailURLDet c
        JOIN dbo.DLPersonMst p ON c.PersionID = p.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0 AND c.TypeValue LIKE '%@%';
        """
        rows = mssql.execute_readonly_query(query)
        total = int(rows[0].get("total_emails") or 0)
        invalid = int(rows[0].get("invalid_emails") or 0)
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
            message=f"{invalid:,} out of {total:,} active person email records ({pct}%) have invalid syntax or formatting.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonInvalidPhoneRule(PersonQualityRule):
    rule_code = "PERSON_INVALID_PHONE"
    category = QualityCategory.VALIDITY
    severity = QualitySeverity.MEDIUM
    title = "Malformed telephone numbers"
    description = "Detects phone contact records with invalid lengths (< 5 digits) or alphabetical characters."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonphoneemailurldet" not in tables_map:
            return False, "Contact table 'dbo.DLPersonPhoneEmailURLDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_phones,
            SUM(CASE WHEN LEN(RTRIM(LTRIM(c.TypeValue))) < 5 OR c.TypeValue LIKE '%[a-zA-Z]%' THEN 1 ELSE 0 END) AS invalid_phones
        FROM dbo.DLPersonPhoneEmailURLDet c
        JOIN dbo.DLPersonMst p ON c.PersionID = p.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0
          AND c.TypeValue NOT LIKE '%@%'
          AND c.TypeValue NOT LIKE 'http%'
          AND c.TypeValue NOT LIKE 'www%';
        """
        rows = mssql.execute_readonly_query(query)
        total = int(rows[0].get("total_phones") or 0)
        invalid = int(rows[0].get("invalid_phones") or 0)
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
            message=f"{invalid:,} out of {total:,} active person phone records ({pct}%) have malformed length or invalid characters.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonInvalidUrlRule(PersonQualityRule):
    rule_code = "PERSON_INVALID_URL"
    category = QualityCategory.VALIDITY
    severity = QualitySeverity.LOW
    title = "Malformed URL addresses"
    description = "Detects web addresses that lack valid top-level domain punctuation."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonphoneemailurldet" not in tables_map:
            return False, "Contact table 'dbo.DLPersonPhoneEmailURLDet' missing."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_urls,
            SUM(CASE WHEN c.TypeValue NOT LIKE '%.%' THEN 1 ELSE 0 END) AS invalid_urls
        FROM dbo.DLPersonPhoneEmailURLDet c
        JOIN dbo.DLPersonMst p ON c.PersionID = p.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0 AND (c.TypeValue LIKE 'http%' OR c.TypeValue LIKE 'www%');
        """
        rows = mssql.execute_readonly_query(query)
        total = int(rows[0].get("total_urls") or 0)
        invalid = int(rows[0].get("invalid_urls") or 0)
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
            message=f"{invalid:,} out of {total:,} active person URL records ({pct}%) are malformed.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonInvalidLatitudeRule(PersonQualityRule):
    rule_code = "PERSON_INVALID_LATITUDE"
    category = QualityCategory.VALIDITY
    severity = QualitySeverity.LOW
    title = "Out-of-range latitude coordinates"
    description = "Checks that non-null geographic latitude coordinates fall within the valid range of -90 to +90 degrees."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonaddressdet" not in tables_map:
            return False, "Address table 'dbo.DLPersonAddressDet' missing."
        cols = tables_map["dlpersonaddressdet"].get("columns", [])
        if "latitude" not in [c.lower() for c in cols]:
            return False, "Column 'Latitude' missing from Address table."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_lats,
            SUM(CASE WHEN TRY_CAST(a.Latitude AS float) IS NULL OR TRY_CAST(a.Latitude AS float) < -90 OR TRY_CAST(a.Latitude AS float) > 90 THEN 1 ELSE 0 END) AS invalid_lats
        FROM dbo.DLPersonAddressDet a
        JOIN dbo.DLPersonMst p ON a.PersonID = p.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0 AND a.Latitude IS NOT NULL AND LTRIM(RTRIM(CAST(a.Latitude AS varchar(100)))) <> '';
        """
        rows = mssql.execute_readonly_query(query)
        total = int(rows[0].get("total_lats") or 0)
        invalid = int(rows[0].get("invalid_lats") or 0)
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
            message=f"{invalid:,} out of {total:,} active person latitude records ({pct}%) are outside the -90 to 90 range.",
            status=QualityFindingStatus.APPLIED,
        )


class PersonInvalidLongitudeRule(PersonQualityRule):
    rule_code = "PERSON_INVALID_LONGITUDE"
    category = QualityCategory.VALIDITY
    severity = QualitySeverity.LOW
    title = "Out-of-range longitude coordinates"
    description = "Checks that non-null geographic longitude coordinates fall within the valid range of -180 to +180 degrees."

    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        if "dlpersonaddressdet" not in tables_map:
            return False, "Address table 'dbo.DLPersonAddressDet' missing."
        cols = tables_map["dlpersonaddressdet"].get("columns", [])
        if "longitude" not in [c.lower() for c in cols]:
            return False, "Column 'Longitude' missing from Address table."
        return True, None

    def evaluate(self) -> QualityFinding:
        query = """
        SELECT
            COUNT_BIG(1) AS total_longs,
            SUM(CASE WHEN TRY_CAST(a.Longitude AS float) IS NULL OR TRY_CAST(a.Longitude AS float) < -180 OR TRY_CAST(a.Longitude AS float) > 180 THEN 1 ELSE 0 END) AS invalid_longs
        FROM dbo.DLPersonAddressDet a
        JOIN dbo.DLPersonMst p ON a.PersonID = p.PersonID
        WHERE p.PersonIsActive = 1 AND ISNULL(p.PersonIsDeleted, 0) = 0 AND a.Longitude IS NOT NULL AND LTRIM(RTRIM(CAST(a.Longitude AS varchar(100)))) <> '';
        """
        rows = mssql.execute_readonly_query(query)
        total = int(rows[0].get("total_longs") or 0)
        invalid = int(rows[0].get("invalid_longs") or 0)
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
            message=f"{invalid:,} out of {total:,} active person longitude records ({pct}%) are outside the -180 to 180 range.",
            status=QualityFindingStatus.APPLIED,
        )
