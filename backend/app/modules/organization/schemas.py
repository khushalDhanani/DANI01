from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.employee.schemas import IssueSeverity


class OrgUnitType(StrEnum):
    COMPANY = "COMPANY"
    LOCATION = "LOCATION"
    MAIN_DEPT = "MAIN_DEPT"
    DEPARTMENT = "DEPARTMENT"
    DESIGNATION = "DESIGNATION"
    GRADE = "GRADE"


class OrgScaleCounts(BaseModel):
    total_companies: int = Field(..., description="Total companies in master table")
    active_companies: int = Field(..., description="Active companies")
    total_locations: int = Field(..., description="Total locations / sites")
    active_locations: int = Field(..., description="Active operational sites")
    total_main_depts: int = Field(..., description="Total main functional divisions")
    active_main_depts: int = Field(..., description="Active main functional divisions")
    total_departments: int = Field(..., description="Total operational sub-departments")
    active_departments: int = Field(..., description="Active operational departments")
    total_designations: int = Field(..., description="Total job designations")
    active_designations: int = Field(..., description="Active designations")
    total_grades: int = Field(..., description="Total grade bands")
    active_grades: int = Field(..., description="Active grade bands")
    total_active_units: int = Field(..., description="Sum of all active organizational units")
    total_inactive_units: int = Field(
        ..., description="Sum of all inactive/deleted organizational units"
    )


class OrgHeadcountItem(BaseModel):
    id: int
    name: str
    code: str | None = None
    count: int
    percentage: float = 0.0


class OrgOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    scale_counts: OrgScaleCounts
    headcount_by_company: list[OrgHeadcountItem]
    headcount_by_location: list[OrgHeadcountItem]
    headcount_by_top_departments: list[OrgHeadcountItem]
    headcount_by_grade: list[OrgHeadcountItem]
    active_employee_total: int
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OrgHierarchyNode(BaseModel):
    id: int
    name: str
    code: str | None = None
    level: str
    headcount: int = 0
    head_emp_id: int | None = None
    head_name: str | None = None
    head_code: str | None = None
    children: list["OrgHierarchyNode"] = Field(default_factory=list)


class OrgHierarchyResponse(BaseModel):
    companies: list[OrgHierarchyNode]
    total_active_employees: int
    total_hierarchical_paths: int


class OrgUnitListItem(BaseModel):
    unit_id: int
    unit_type: OrgUnitType
    unit_code: str | None = None
    unit_name: str
    parent_id: int | None = None
    parent_name: str | None = None
    head_emp_id: int | None = None
    head_name: str | None = None
    head_code: str | None = None
    active_headcount: int = 0
    is_active: bool
    is_deleted: bool = False


class OrgUnitListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[OrgUnitListItem]


class OrgQualityRuleResult(BaseModel):
    rule_code: str
    rule_name: str
    severity: IssueSeverity
    description: str
    issue_count: int
    impact: str
    recommendation: str


class OrgDataQualityResponse(BaseModel):
    overall_health_score: float
    critical_issues_count: int
    warning_issues_count: int
    info_issues_count: int
    rules: list[OrgQualityRuleResult]
    summary_by_severity: dict[str, int]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OrgQualityIssueRecord(BaseModel):
    record_id: int | str
    entity_type: str
    entity_name: str
    issue_code: str
    issue_detail: str
    extra_context: dict[str, Any] = Field(default_factory=dict)


class OrgQualityIssuesListResponse(BaseModel):
    issue_code: str
    issue_name: str
    severity: IssueSeverity
    total: int
    limit: int
    offset: int
    items: list[OrgQualityIssueRecord]


class OrgReportingNode(BaseModel):
    emp_id: int
    emp_code: str | None = None
    full_name: str
    designation: str | None = None
    department: str | None = None
    location: str | None = None
    role_type: str = "STAFF"
    direct_reports_count: int = 0
    subordinates: list["OrgReportingNode"] = Field(default_factory=list)


class OrgReportingTreeResponse(BaseModel):
    roots: list[OrgReportingNode]
    total_assigned_managers: int
