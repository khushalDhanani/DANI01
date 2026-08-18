"""
Pydantic schemas for the Contact & Email Analysis module.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.modules.employee.schemas import IssueSeverity


class ContactEmailOverview(BaseModel):
    total_active_employees: int
    with_company_email: int
    with_company_email_pct: float
    with_personal_email: int
    with_personal_email_pct: float
    with_alternate_email: int
    with_alternate_email_pct: float
    with_any_email: int
    with_any_email_pct: float
    without_any_email: int
    without_any_email_pct: float
    without_company_email: int
    without_company_email_pct: float
    without_personal_email: int
    without_personal_email_pct: float


class ContactPhoneOverview(BaseModel):
    with_primary_phone: int
    with_primary_phone_pct: float
    with_secondary_phone: int
    with_secondary_phone_pct: float
    with_corr_phone1: int
    with_corr_phone1_pct: float
    with_corr_phone2: int
    with_corr_phone2_pct: float
    with_any_phone: int
    with_any_phone_pct: float
    without_primary_phone: int
    without_primary_phone_pct: float
    without_any_phone: int
    without_any_phone_pct: float
    primary_phone_verified: int
    primary_phone_verified_pct: float
    secondary_phone_verified: int
    secondary_phone_verified_pct: float


class ContactAddressOverview(BaseModel):
    with_permanent_address: int
    with_permanent_address_pct: float
    with_correspondence_address: int
    with_correspondence_address_pct: float
    with_permanent_pincode: int
    with_correspondence_pincode: int
    with_ice_emergency_contact: int
    with_ice_emergency_contact_pct: float


class ContactDomainBreakdownItem(BaseModel):
    domain: str
    count: int
    percentage: float


class ContactOverviewResponse(BaseModel):
    total_active_employees: int
    email_metrics: ContactEmailOverview
    phone_metrics: ContactPhoneOverview
    address_metrics: ContactAddressOverview
    domain_breakdown: list[ContactDomainBreakdownItem]
    security_user_sync: dict[str, Any]
    generated_at: str


class ContactDirectoryItem(BaseModel):
    emp_id: int
    emp_code: str | None = None
    full_name: str
    department: str | None = None
    designation: str | None = None
    location: str | None = None
    company_email: str | None = None
    personal_email: str | None = None
    alternate_email: str | None = None
    primary_phone: str | None = None
    is_verified_phone1: bool = False
    secondary_phone: str | None = None
    is_verified_phone2: bool = False
    corr_phone1: str | None = None
    ice_mobile: str | None = None
    ice_contact_name: str | None = None
    permanent_pincode: str | None = None
    correspondence_pincode: str | None = None
    has_valid_email: bool = False
    has_valid_phone: bool = False


class ContactDirectoryListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ContactDirectoryItem] = Field(default_factory=list)


class ContactQualityRuleResult(BaseModel):
    rule_code: str
    rule_name: str
    severity: IssueSeverity
    description: str
    issue_count: int
    impact: str
    recommendation: str


class ContactDataQualityResponse(BaseModel):
    overall_health_score: float
    critical_issues_count: int
    warning_issues_count: int
    info_issues_count: int
    rules: list[ContactQualityRuleResult]
    summary_by_severity: dict[str, int]
    generated_at: str


class ContactQualityIssueItem(BaseModel):
    record_id: int
    emp_code: str | None = None
    entity_name: str
    issue_code: str
    issue_detail: str
    contact_value: str | None = None


class ContactQualityIssuesListResponse(BaseModel):
    issue_code: str
    issue_name: str
    severity: IssueSeverity
    total: int
    limit: int
    offset: int
    items: list[ContactQualityIssueItem] = Field(default_factory=list)
