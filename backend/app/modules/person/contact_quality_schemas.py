from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class ContactQualityIssueType(str, Enum):
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


class ContactQualitySummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # 1. Contact Channels
    persons_without_email: int = Field(default=0, description="Persons with no email record")
    persons_without_phone: int = Field(default=0, description="Persons with no phone number")
    invalid_emails: int = Field(default=0, description="Malformed or invalid email addresses")
    invalid_phones: int = Field(default=0, description="Malformed or invalid phone numbers")
    invalid_urls: int = Field(default=0, description="Malformed web URLs")
    unverified_contacts: int = Field(default=0, description="Total unverified contact records")
    duplicate_email_cross_persons: int = Field(default=0, description="Unique emails shared across multiple Persons")
    duplicate_email_same_person: int = Field(default=0, description="Duplicate emails entered under same Person")
    duplicate_phone_cross_persons: int = Field(default=0, description="Unique phones shared across multiple Persons")
    duplicate_phone_same_person: int = Field(default=0, description="Duplicate phones entered under same Person")
    persons_multiple_primary: int = Field(default=0, description="Persons with more than one primary contact")
    primary_contact_inactive: int = Field(default=0, description="Primary contacts flagged as inactive")

    # 2. Address & Location Quality
    addr_missing_postal_code: int = Field(default=0, description="Addresses with street/city but no postal code")
    addr_invalid_pin_format: int = Field(default=0, description="Postal codes with non-numeric chars or invalid length")
    addr_street_without_city: int = Field(default=0, description="Addresses with street but missing city name")
    addr_city_without_state: int = Field(default=0, description="Addresses with city but missing state name")
    addr_missing_geocodes: int = Field(default=0, description="Addresses missing latitude or longitude coordinates")
    addr_duplicate_same_person: int = Field(default=0, description="Duplicate addresses under the same Person")

    # 3. Profile & Chronological Integrity
    person_anniversary_before_birth: int = Field(default=0, description="Anniversary date earlier than birth date")
    person_invalid_birth_date: int = Field(default=0, description="Birth date in the future or before 1900")
    person_birth_date_ancient: int = Field(default=0, description="Birth dates with dummy 1900-01-01 or age > 100")
    person_suspicious_dummy_names: int = Field(default=0, description="Persons with placeholder names e.g. test, admin, dummy")
    person_missing_lastname_only: int = Field(default=0, description="Persons with first name but missing last name")

    # 4. Employment & Lifecycle Consistency
    active_emp_missing_title: int = Field(default=0, description="Active employees missing job title designation")
    inactive_with_empid: int = Field(default=0, description="Inactive persons still holding active employee ID")
    status_active_and_deleted: int = Field(default=0, description="Conflicting active and deleted flags")
    stale_temp_persons: int = Field(default=0, description="Temporary persons older than 90 days")

    # 5. Governance & Blacklist Compliance
    blacklist_unapproved: int = Field(default=0, description="Blacklisted persons lacking HOD approval")
    blacklist_missing_details: int = Field(default=0, description="Blacklisted persons missing date or reason type")

    # 6. Entity Linkages & Child Records
    company_orphan_links: int = Field(default=0, description="Company affiliations with non-existent or null company IDs")
    company_duplicate_links: int = Field(default=0, description="Duplicate company links under the same Person")
    company_missing_role: int = Field(default=0, description="Company links missing job role designation")
    extra_field_orphan_id: int = Field(default=0, description="Custom fields referencing non-existent field schema")
    extra_field_duplicate_entries: int = Field(default=0, description="Duplicate custom field values under same Person")

    # 7. Audit Trail & Sync Integration
    deleted_missing_del_date: int = Field(default=0, description="Deleted persons missing deletion timestamp")
    audit_del_before_ent: int = Field(default=0, description="Deletion timestamp earlier than creation timestamp")
    sync_zimbra_missing_id: int = Field(default=0, description="Sync enabled persons missing Zimbra contact ID")

    # Scope & Metadata (Root Entity: dbo.DLPersonMst)
    total_persons_evaluated: int = Field(default=0, description="COUNT(DISTINCT PersonID) WHERE PersonIsActive = 1 AND ISNULL(PersonIsDeleted, 0) = 0")
    total_inactive_persons: int = Field(default=0, description="Informational count of inactive persons (PersonIsActive = 0 or NULL)")
    total_deleted_persons: int = Field(default=0, description="Informational count of deleted persons (PersonIsDeleted = 1)")
    related_tables_checked: int = Field(default=8, description="Count of related PERSON tables checked")
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


class ContactQualityIssuesResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    issue: str = Field(..., description="Active issue filter code")
    total: int = Field(..., description="Total matching issue records")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Pagination offset")
    items: list[ContactQualityIssueItem] = Field(default_factory=list, description="Issue items")
