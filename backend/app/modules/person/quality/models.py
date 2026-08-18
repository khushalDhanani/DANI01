"""
models.py

Domain models, enums, dataclasses, and Pydantic schemas for the Daylite Person Quality engine.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.person.quality.common.persons import (
    ACTIVE_PERSON_WHERE_SQL,
    PERSON_NAME_SQL,
)


class QualityCategory(StrEnum):
    COMPLETENESS = "COMPLETENESS"
    VALIDITY = "VALIDITY"
    INTEGRITY = "INTEGRITY"
    CONSISTENCY = "CONSISTENCY"


class QualitySeverity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class QualityFindingStatus(StrEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"
    APPLIED = "APPLIED"


class QualityFinding(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rule_code: str = Field(..., description="Unique rule code")
    category: QualityCategory = Field(...)
    severity: QualitySeverity = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    affected_count: int = Field(default=0)
    total_evaluated: int = Field(default=0)
    affected_percent: float = Field(default=0.0)
    exact: bool = Field(default=True)
    message: str = Field(...)
    status: QualityFindingStatus = Field(...)
    skip_reason: str | None = Field(default=None)
    sample_records: list[dict[str, Any]] = Field(default_factory=list)


class QualitySeveritySummary(BaseModel):
    critical: int = Field(default=0)
    high: int = Field(default=0)
    medium: int = Field(default=0)
    low: int = Field(default=0)
    info: int = Field(default=0)


class PersonQualityResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    module: str = Field(default="PERSON")
    status: str = Field(default="COMPLETED")
    rules_evaluated: int = Field(default=0)
    rules_skipped: int = Field(default=0)
    findings_count: int = Field(default=0)
    severity_summary: QualitySeveritySummary = Field(default_factory=QualitySeveritySummary)
    findings: list[QualityFinding] = Field(default_factory=list)
    duration_ms: float = Field(default=0.0)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class IssueCountUnit(StrEnum):
    PERSON = "PERSON"  # Root entity (dbo.DLPersonMst)
    CONTACT = "CONTACT"  # Communication channel (dbo.DLPersonPhoneEmailURLDet)
    ADDRESS = "ADDRESS"  # Physical location (dbo.DLPersonAddressDet)
    COMPANY_LINK = "COMPANY_LINK"  # Corporate affiliation (dbo.DLPersonCompanyLinkDet)
    EXTRA_FIELD = "EXTRA_FIELD"  # Custom attribute (dbo.DLPersonExtraFieldValueDet)
    DUPLICATE_GROUP = "DUPLICATE_GROUP"  # Anomaly cluster sharing identical invalid identity


class ContactQualityIssueType(StrEnum):
    # 1. Contact Issues
    MISSING_EMAIL = "MISSING_EMAIL"
    MISSING_PHONE = "MISSING_PHONE"
    INVALID_EMAIL = "INVALID_EMAIL"
    INVALID_PHONE = "INVALID_PHONE"
    INVALID_URL = "INVALID_URL"
    DUPLICATE_EMAIL_CROSS = "DUPLICATE_EMAIL_CROSS"
    DUPLICATE_EMAIL_SAME = "DUPLICATE_EMAIL_SAME"
    DUPLICATE_PHONE_CROSS = "DUPLICATE_PHONE_CROSS"
    DUPLICATE_PHONE_SAME = "DUPLICATE_PHONE_SAME"
    UNVERIFIED_CONTACT = "UNVERIFIED_CONTACT"
    MULTIPLE_PRIMARY = "MULTIPLE_PRIMARY"
    PRIMARY_INACTIVE = "PRIMARY_INACTIVE"

    # 2. Address Quality Issues
    MISSING_POSTAL_CODE = "MISSING_POSTAL_CODE"
    INVALID_PIN_CODE_FORMAT = "INVALID_PIN_CODE_FORMAT"
    STREET_WITHOUT_CITY = "STREET_WITHOUT_CITY"
    CITY_WITHOUT_STATE = "CITY_WITHOUT_STATE"
    MISSING_GEOCODES = "MISSING_GEOCODES"
    DUPLICATE_ADDRESSES_SAME_PERSON = "DUPLICATE_ADDRESSES_SAME_PERSON"

    # 3. Profile & Chronological Integrity
    ANNIVERSARY_BEFORE_BIRTH = "ANNIVERSARY_BEFORE_BIRTH"
    INVALID_BIRTH_DATE = "INVALID_BIRTH_DATE"
    BIRTH_DATE_DEFAULT_OR_ANCIENT = "BIRTH_DATE_DEFAULT_OR_ANCIENT"
    SUSPICIOUS_DUMMY_NAMES = "SUSPICIOUS_DUMMY_NAMES"
    MISSING_LAST_NAME = "MISSING_LAST_NAME"

    # 4. Employment & Lifecycle Consistency
    ACTIVE_EMP_MISSING_TITLE = "ACTIVE_EMP_MISSING_TITLE"
    INACTIVE_WITH_ACTIVE_EMPID = "INACTIVE_WITH_ACTIVE_EMPID"
    STATUS_ACTIVE_AND_DELETED = "STATUS_ACTIVE_AND_DELETED"
    STALE_TEMP_PERSONS = "STALE_TEMP_PERSONS"

    # 5. Governance, Blacklist & Compliance
    BLACKLIST_UNAPPROVED = "BLACKLIST_UNAPPROVED"
    BLACKLIST_MISSING_DETAILS = "BLACKLIST_MISSING_DETAILS"

    # 6. Entity Linkages & Child Records
    ORPHAN_COMPANY_LINK = "ORPHAN_COMPANY_LINK"
    DUPLICATE_COMPANY_LINKS = "DUPLICATE_COMPANY_LINKS"
    COMPANY_MISSING_ROLE = "COMPANY_MISSING_ROLE"
    EXTRA_FIELD_ORPHAN_ID = "EXTRA_FIELD_ORPHAN_ID"
    DUPLICATE_EXTRA_FIELDS = "DUPLICATE_EXTRA_FIELDS"

    # 7. Audit Trail & Sync Integration
    DELETED_MISSING_TIMESTAMP = "DELETED_MISSING_TIMESTAMP"
    AUDIT_DEL_BEFORE_ENT = "AUDIT_DEL_BEFORE_ENT"
    SYNC_ZIMBRA_MISSING_ID = "SYNC_ZIMBRA_MISSING_ID"


QualityDimension = Literal[
    "CONTACTS",
    "ADDRESSES",
    "PROFILE",
    "EMPLOYMENT",
    "GOVERNANCE",
]

TargetEntity = Literal[
    "PERSON",
    "CONTACT",
    "ADDRESS",
    "COMPANY_LINK",
    "EXTRA_FIELD",
]


@dataclass(frozen=True)
class QualityRuleMeta:
    code: ContactQualityIssueType
    title: str
    dimension: str
    severity: str
    count_unit: IssueCountUnit
    unit_label_singular: str
    unit_label_plural: str
    description: str


@dataclass(frozen=True)
class QualityRule:
    code: ContactQualityIssueType
    title: str
    dimension: QualityDimension
    severity: Literal["CRITICAL", "WARNING", "INFO"]
    count_unit: IssueCountUnit
    unit_label_singular: str
    unit_label_plural: str
    summary_field: str
    description: str
    target_entity: TargetEntity
    predicate_sql: str
    requires_active_person: bool = True
    contact_type: str = "PROFILE"
    value_expr_sql: str | None = None
    label_expr_sql: str | None = None
    group_key_sql: str | None = None
    group_label_sql: str | None = None
    group_records_count_sql: str | None = None
    group_persons_count_sql: str | None = None

    @property
    def from_clause_sql(self) -> str:
        if self.target_entity == "CONTACT":
            return "ClassifiedContacts c JOIN dbo.DLPersonMst p ON c.PersonID = p.PersonID"
        elif self.target_entity == "ADDRESS":
            return "dbo.DLPersonAddressDet a JOIN dbo.DLPersonMst p ON a.PersonID = p.PersonID"
        elif self.target_entity == "COMPANY_LINK":
            return "dbo.DLPersonCompanyLinkDet l JOIN dbo.DLPersonMst p ON l.PersonID = p.PersonID"
        elif self.target_entity == "EXTRA_FIELD":
            return (
                "dbo.DLPersonExtraFieldValueDet e JOIN dbo.DLPersonMst p ON e.PersonID = p.PersonID"
            )
        else:  # PERSON
            return "dbo.DLPersonMst p"

    @property
    def where_clause_sql(self) -> str:
        if self.target_entity in ("ADDRESS", "COMPANY_LINK", "EXTRA_FIELD") or (
            self.target_entity == "PERSON" and self.requires_active_person
        ):
            return f"{ACTIVE_PERSON_WHERE_SQL} AND {self.predicate_sql}"
        return self.predicate_sql

    def issue_relation_sql(self) -> str:
        """
        Returns the canonical FROM ... WHERE relation defining what constitutes one defect instance.
        """
        return f"FROM {self.from_clause_sql} WHERE {self.where_clause_sql}"

    @property
    def select_columns_sql(self) -> str:
        val_expr = self.value_expr_sql or "NULL"
        lbl_expr = self.label_expr_sql or "NULL"

        if self.target_entity == "CONTACT":
            return f"""
            c.PersonID,
            {PERSON_NAME_SQL} AS PersonName,
            c.PersonPhoneID AS ContactID,
            c.ContactCategory AS ContactType,
            c.LabelName AS LabelName,
            c.TypeValue AS CurrentValue,
            '{self.code.value}' AS IssueCode,
            '{self.description}' AS IssueDescription,
            '{self.severity}' AS Severity,
            c.IsVerified AS IsVerified,
            c.IsPrimary AS IsPrimary,
            p.PersonIsActive AS IsActive
            """.strip()
        elif self.target_entity == "ADDRESS":
            return f"""
            a.PersonID,
            {PERSON_NAME_SQL} AS PersonName,
            a.PersonAddID AS ContactID,
            'ADDRESS' AS ContactType,
            {lbl_expr} AS LabelName,
            {val_expr} AS CurrentValue,
            '{self.code.value}' AS IssueCode,
            '{self.description}' AS IssueDescription,
            '{self.severity}' AS Severity,
            NULL AS IsVerified,
            NULL AS IsPrimary,
            p.PersonIsActive AS IsActive
            """.strip()
        elif self.target_entity == "COMPANY_LINK":
            return f"""
            l.PersonID,
            {PERSON_NAME_SQL} AS PersonName,
            l.PersonLinkID AS ContactID,
            'COMPANY_LINK' AS ContactType,
            {lbl_expr} AS LabelName,
            {val_expr} AS CurrentValue,
            '{self.code.value}' AS IssueCode,
            '{self.description}' AS IssueDescription,
            '{self.severity}' AS Severity,
            NULL AS IsVerified,
            NULL AS IsPrimary,
            p.PersonIsActive AS IsActive
            """.strip()
        elif self.target_entity == "EXTRA_FIELD":
            return f"""
            e.PersonID,
            {PERSON_NAME_SQL} AS PersonName,
            e.PersonExtraFieldValueID AS ContactID,
            'CUSTOM_FIELD' AS ContactType,
            {lbl_expr} AS LabelName,
            {val_expr} AS CurrentValue,
            '{self.code.value}' AS IssueCode,
            '{self.description}' AS IssueDescription,
            '{self.severity}' AS Severity,
            NULL AS IsVerified,
            NULL AS IsPrimary,
            p.PersonIsActive AS IsActive
            """.strip()
        else:  # PERSON
            return f"""
            p.PersonID,
            {PERSON_NAME_SQL} AS PersonName,
            NULL AS ContactID,
            '{self.contact_type}' AS ContactType,
            {lbl_expr} AS LabelName,
            {val_expr} AS CurrentValue,
            '{self.code.value}' AS IssueCode,
            '{self.description}' AS IssueDescription,
            '{self.severity}' AS Severity,
            NULL AS IsVerified,
            NULL AS IsPrimary,
            p.PersonIsActive AS IsActive
            """.strip()


class ContactQualitySummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # 1. Contact Channels
    persons_without_email: int = Field(default=0, description="Persons with no email record")
    persons_without_phone: int = Field(default=0, description="Persons with no phone number")
    invalid_emails: int = Field(default=0, description="Malformed or invalid email contact records")
    invalid_phones: int = Field(default=0, description="Malformed or invalid phone contact records")
    invalid_urls: int = Field(default=0, description="Malformed web URL contact records")
    unverified_contacts: int = Field(default=0, description="Total unverified contact records")
    duplicate_email_cross_persons: int = Field(
        default=0, description="Unique email groups shared across multiple Persons"
    )
    duplicate_email_same_person: int = Field(
        default=0, description="Duplicate email sets entered more than once for same Person"
    )
    duplicate_phone_cross_persons: int = Field(
        default=0, description="Unique phone groups shared across multiple Persons"
    )
    duplicate_phone_same_person: int = Field(
        default=0, description="Duplicate phone sets entered more than once for same Person"
    )
    persons_multiple_primary: int = Field(
        default=0, description="Persons with more than 1 primary contact record"
    )
    primary_contact_inactive: int = Field(
        default=0, description="Primary contact marked inactive/disabled"
    )

    # 2. Address Quality
    addr_missing_postal_code: int = Field(
        default=0, description="Address records without postal code"
    )
    addr_invalid_pin_format: int = Field(
        default=0, description="Postal codes with invalid length or non-numeric digits"
    )
    addr_street_without_city: int = Field(
        default=0, description="Addresses with street populated but missing city"
    )
    addr_city_without_state: int = Field(
        default=0, description="Addresses with city populated but missing state"
    )
    addr_missing_geocodes: int = Field(
        default=0, description="Addresses missing latitude or longitude coordinates"
    )
    addr_duplicate_same_person: int = Field(
        default=0, description="Duplicate address sets entered more than once for same Person"
    )

    # 3. Profile & Chronological Integrity
    person_anniversary_before_birth: int = Field(
        default=0, description="Persons with anniversary earlier than birth date"
    )
    person_invalid_birth_date: int = Field(
        default=0, description="Persons with future birth dates or dates prior to 1900"
    )
    person_birth_date_ancient: int = Field(
        default=0, description="Persons with placeholder birth date (1900-01-01) or age > 100"
    )
    person_suspicious_dummy_names: int = Field(
        default=0, description="Persons with dummy or placeholder names"
    )
    person_missing_lastname_only: int = Field(
        default=0, description="Persons having first name but missing last name"
    )

    # 4. Employment & Status Consistency
    active_emp_missing_title: int = Field(
        default=0, description="Active employees having EmpID but missing job title"
    )
    inactive_with_empid: int = Field(
        default=0, description="Inactive persons still holding active EmpID"
    )
    status_active_and_deleted: int = Field(
        default=0, description="Persons marked simultaneously Active and Deleted"
    )
    stale_temp_persons: int = Field(default=0, description="Temporary persons older than 90 days")

    # 5. Governance & Blacklist Compliance
    blacklist_unapproved: int = Field(
        default=0, description="Blacklisted persons lacking HOD approval"
    )
    blacklist_missing_details: int = Field(
        default=0, description="Blacklisted persons missing date or reason type"
    )

    # 6. Entity Linkages & Child Records
    company_orphan_links: int = Field(
        default=0, description="Company affiliation link records referencing invalid company ID"
    )
    company_duplicate_links: int = Field(
        default=0, description="Duplicate company affiliation sets for same Person"
    )
    company_missing_role: int = Field(
        default=0, description="Company link records missing job role designation"
    )
    extra_field_orphan_id: int = Field(
        default=0, description="Custom field records referencing invalid field schema"
    )
    extra_field_duplicate_entries: int = Field(
        default=0, description="Duplicate custom field value sets under same Person"
    )

    # 7. Audit Trail & Sync Integration
    deleted_missing_del_date: int = Field(
        default=0, description="Deleted persons missing deletion timestamp"
    )
    audit_del_before_ent: int = Field(
        default=0, description="Persons with deletion timestamp earlier than creation timestamp"
    )
    sync_zimbra_missing_id: int = Field(
        default=0, description="Sync enabled persons missing Zimbra contact ID"
    )

    # 8. Distinct Person Quality Telemetry (Entity-Level Analytics)
    persons_with_critical_issues: int = Field(
        default=0,
        description="COUNT(DISTINCT PersonID) of active persons with >= 1 critical quality issue",
    )
    persons_with_warning_issues: int = Field(
        default=0,
        description="COUNT(DISTINCT PersonID) of active persons with >= 1 warning quality issue",
    )
    persons_with_any_issue: int = Field(
        default=0, description="COUNT(DISTINCT PersonID) of active persons with >= 1 quality issue"
    )
    total_clean_persons: int = Field(
        default=0, description="Active evaluated persons with 0 quality issues"
    )
    health_score_pct: float = Field(
        default=100.0,
        description="Percentage of active evaluated persons with clean data (0 issues)",
    )

    # 9. Standardized Aggregate Findings (Rule-Level Analytics)
    total_critical_findings: int = Field(
        default=0, description="Sum of findings across all critical validation checks"
    )
    total_warning_findings: int = Field(
        default=0, description="Sum of findings across all warning validation checks"
    )
    total_info_findings: int = Field(
        default=0, description="Sum of findings across all info validation checks"
    )

    # Scope & Metadata (Root Entity: dbo.DLPersonMst)
    total_persons_evaluated: int = Field(
        default=0,
        description="COUNT(DISTINCT PersonID) WHERE PersonIsActive = 1 AND ISNULL(PersonIsDeleted, 0) = 0",
    )
    total_inactive_persons: int = Field(
        default=0,
        description="Informational count of inactive persons (PersonIsActive = 0 or NULL)",
    )
    total_deleted_persons: int = Field(
        default=0, description="Informational count of deleted persons (PersonIsDeleted = 1)"
    )
    related_tables_checked: int = Field(
        default=8, description="Count of related PERSON tables checked"
    )
    calculated_at: str = Field(...)
    duration_ms: float = Field(...)


class ContactQualityIssueItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    person_id: int = Field(..., alias="PersonID")
    person_name: str = Field(..., alias="PersonName")
    contact_id: int | None = Field(default=None, alias="ContactID")
    contact_type: str = Field(..., alias="ContactType")
    label_name: str | None = Field(default=None, alias="LabelName")
    current_value: str | None = Field(default=None, alias="CurrentValue")
    masked_value: str | None = Field(default=None, alias="MaskedValue")
    issue_code: str = Field(..., alias="IssueCode")
    issue_description: str = Field(..., alias="IssueDescription")
    severity: str = Field(default="WARNING", alias="Severity")  # CRITICAL, HIGH, WARNING, INFO
    is_verified: bool | None = Field(default=None, alias="IsVerified")
    is_primary: bool | None = Field(default=None, alias="IsPrimary")
    is_active: bool | None = Field(default=None, alias="IsActive")


class ContactQualityGroupMember(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    person_id: int = Field(..., alias="PersonID")
    person_name: str = Field(..., alias="PersonName")
    contact_id: int | None = Field(default=None, alias="ContactID")
    contact_type: str = Field(..., alias="ContactType")
    label_name: str | None = Field(default=None, alias="LabelName")
    current_value: str | None = Field(default=None, alias="CurrentValue")
    masked_value: str | None = Field(default=None, alias="MaskedValue")
    issue_code: str = Field(..., alias="IssueCode")
    issue_description: str = Field(..., alias="IssueDescription")
    severity: str = Field(default="WARNING", alias="Severity")
    is_verified: bool | None = Field(default=None, alias="IsVerified")
    is_primary: bool | None = Field(default=None, alias="IsPrimary")
    is_active: bool | None = Field(default=None, alias="IsActive")


class ContactQualityGroupItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    group_key: str = Field(..., alias="GroupKey")
    group_label: str = Field(..., alias="GroupLabel")
    affected_persons_count: int = Field(..., alias="AffectedPersonsCount")
    affected_records_count: int = Field(..., alias="AffectedRecordsCount")
    members: list[ContactQualityGroupMember] = Field(default_factory=list, alias="Members")


class ContactQualityIssuesResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    issue: str = Field(..., description="Active issue filter code")
    count_unit: IssueCountUnit = Field(
        default=IssueCountUnit.PERSON, description="Declared counting unit for this rule"
    )
    unit_label_singular: str = Field(default="Record", description="Display label singular")
    unit_label_plural: str = Field(default="Records", description="Display label plural")
    total: int = Field(..., description="Total count in units of count_unit")
    total_affected_persons: int | None = Field(
        default=None, description="Total affected persons count if applicable"
    )
    total_affected_records: int | None = Field(
        default=None, description="Total underlying records count if applicable"
    )
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Pagination offset")
    items: list[ContactQualityIssueItem] = Field(
        default_factory=list, description="Issue items (for 1-to-1/record rules)"
    )
    groups: list[ContactQualityGroupItem] = Field(
        default_factory=list, description="Group items (for DUPLICATE_GROUP rules)"
    )
    calculated_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO calculation timestamp of the snapshot",
    )
