from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IssueSeverity(StrEnum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class EmployeeStatusCount(BaseModel):
    total: int = Field(..., description="Total employees in master table")
    active: int = Field(..., description="Currently active valid employees")
    inactive: int = Field(..., description="Inactive non-resigned employees")
    resigned: int = Field(..., description="Resigned employees")
    deleted: int = Field(..., description="Soft-deleted employees")


class DistributionItem(BaseModel):
    label: str
    count: int
    percentage: float = 0.0


class EmployeeOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status_counts: EmployeeStatusCount
    gender_distribution: list[DistributionItem]
    employment_type_distribution: list[DistributionItem]
    department_distribution: list[DistributionItem]
    company_distribution: list[DistributionItem]
    top_locations: list[DistributionItem]
    user_account_coverage: dict[str, Any]
    reporting_coverage: dict[str, Any]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TableNodeMetadata(BaseModel):
    schema_name: str = Field(..., alias="schema")
    table_name: str = Field(..., alias="table")
    role: str
    row_count: int
    key_column: str
    confidence: str = "CONFIRMED"
    description: str


class RelationshipEdge(BaseModel):
    source_table: str
    target_table: str
    source_key: str
    target_key: str
    relationship_type: str
    confidence: str = "CONFIRMED"
    description: str


class EmployeeStructureResponse(BaseModel):
    master_table: str = "dbo.EmployeeMst"
    canonical_key: str = "EmpID"
    business_key: str = "EmpCode"
    tables: list[TableNodeMetadata]
    relationships: list[RelationshipEdge]
    confidence_summary: dict[str, int]


class QualityRuleResult(BaseModel):
    rule_code: str
    rule_name: str
    severity: IssueSeverity
    description: str
    issue_count: int
    impact: str
    recommendation: str


class EmployeeDataQualityResponse(BaseModel):
    overall_health_score: float
    critical_issues_count: int
    warning_issues_count: int
    info_issues_count: int
    rules: list[QualityRuleResult]
    summary_by_severity: dict[str, int]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class QualityIssueRecord(BaseModel):
    emp_id: int | None = None
    emp_code: str | None = None
    full_name: str | None = None
    company_email: str | None = None
    phone: str | None = None
    department_name: str | None = None
    designation_name: str | None = None
    emp_is_active: bool | None = None
    emp_resign_date: date | datetime | None = None
    issue_code: str
    issue_detail: str


class QualityIssuesListResponse(BaseModel):
    issue_code: str
    issue_name: str
    severity: IssueSeverity
    total: int
    limit: int
    offset: int
    items: list[QualityIssueRecord]


class EmployeeListItem(BaseModel):
    emp_id: int
    emp_code: str | None = None
    full_name: str
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    company_email: str | None = None
    personal_email: str | None = None
    phone: str | None = None
    pan_no: str | None = None
    aadhar_no: str | None = None
    joining_date: date | datetime | None = None
    resign_date: date | datetime | None = None
    is_active: bool
    is_deleted: bool
    employment_type: str | None = None
    company_name: str | None = None
    department_name: str | None = None
    designation_name: str | None = None
    location_name: str | None = None
    grade_desc: str | None = None
    functional_mgr_id: int | None = None
    functional_mgr_name: str | None = None
    admin_mgr_id: int | None = None
    admin_mgr_name: str | None = None
    user_id: int | None = None
    user_name: str | None = None
    user_is_active: bool | None = None
    role_desc: str | None = None


class EmployeeListResponse(BaseModel):
    total: int
    active_count: int
    inactive_count: int
    limit: int
    offset: int
    items: list[EmployeeListItem]


class OfficialHistoryItem(BaseModel):
    office_det_id: int
    dept_name: str | None = None
    desig_name: str | None = None
    loc_name: str | None = None
    grade_desc: str | None = None
    applicable_from: date | None = None
    joining_date: date | None = None
    resign_date: date | None = None
    is_active: bool


class FamilyMemberItem(BaseModel):
    family_det_id: int
    name: str
    relation_name: str | None = None
    birth_date: date | None = None
    phone: str | None = None
    is_emergency_contact: bool = False


class QualificationItem(BaseModel):
    qual_det_id: int
    degree_name: str | None = None
    passing_year: int | None = None
    percentage_grade: str | None = None
    institute_name: str | None = None


class ExperienceItem(BaseModel):
    exp_det_id: int
    company_name: str | None = None
    designation: str | None = None
    from_date: date | None = None
    to_date: date | None = None
    last_drawn_ctc: str | None = None


class EmployeeDetailResponse(BaseModel):
    emp_id: int
    emp_code: str | None = None
    title: str | None = None
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    full_name: str
    gender: str | None = None
    birth_date: date | None = None
    blood_group: str | None = None
    marital_status: str | None = None
    religion: str | None = None
    caste_category: str | None = None
    nationality: str | None = None

    # Contact
    company_email: str | None = None
    personal_email: str | None = None
    phone1: str | None = None
    phone2: str | None = None
    direct_number: str | None = None
    ext_number: str | None = None
    cug_number: str | None = None

    # Addresses
    correspondence_address: str | None = None
    corr_city: str | None = None
    corr_state: str | None = None
    corr_pincode: str | None = None
    permanent_address: str | None = None
    perm_city: str | None = None
    perm_state: str | None = None
    perm_pincode: str | None = None

    # Identifiers
    pan_no: str | None = None
    aadhar_no: str | None = None
    uan_no: str | None = None
    pf_no: str | None = None
    esic_no: str | None = None
    voter_id: str | None = None
    driving_license_no: str | None = None
    pran_no: str | None = None
    sap_gl_code: str | None = None
    microsoft_object_id: str | None = None

    # Status
    joining_date: date | datetime | None = None
    resign_date: date | datetime | None = None
    is_active: bool
    is_deleted: bool
    employment_type: str | None = None
    company_name: str | None = None

    # Current Position
    current_dept: str | None = None
    current_desig: str | None = None
    current_location: str | None = None
    current_grade: str | None = None

    # Managers
    functional_mgr_id: int | None = None
    functional_mgr_code: str | None = None
    functional_mgr_name: str | None = None
    admin_mgr_id: int | None = None
    admin_mgr_code: str | None = None
    admin_mgr_name: str | None = None

    # User Account
    user_id: int | None = None
    user_name: str | None = None
    user_email: str | None = None
    user_ad_id: str | None = None
    user_is_active: bool | None = None
    role_desc: str | None = None

    # Detail Lists
    official_history: list[OfficialHistoryItem] = []
    family_members: list[FamilyMemberItem] = []
    qualifications: list[QualificationItem] = []
    experiences: list[ExperienceItem] = []
