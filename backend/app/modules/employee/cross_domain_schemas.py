from typing import Any

from pydantic import BaseModel, Field


class CrossDomainQualityRuleInfo(BaseModel):
    rule_code: str = Field(..., description="Unique rule code identifier")
    rule_name: str = Field(..., description="Human-readable rule title")
    severity: str = Field(..., description="Severity level: CRITICAL, WARNING, INFO")
    category: str = Field(
        ...,
        description="Rule category e.g. MASTER, ORG, HIERARCHY, SECURITY, ATTENDANCE, LEAVE, PAYROLL",
    )
    description: str = Field(..., description="Technical description of the data rule")
    impact: str = Field(..., description="Business impact of rule violations")
    issue_count: int = Field(..., description="Total violation records flagged")
    affected_employees_count: int = Field(..., description="Distinct affected employees flagged")


class CrossDomainCategorySummary(BaseModel):
    category_code: str = Field(..., description="Category identifier code")
    category_name: str = Field(..., description="Human-readable category name")
    rule_count: int = Field(..., description="Number of active rules in this category")
    total_issues: int = Field(..., description="Total issue count across rules in category")
    critical_issues: int = Field(..., description="Critical issue count in category")
    warning_issues: int = Field(..., description="Warning issue count in category")
    info_issues: int = Field(..., description="Info issue count in category")


class CrossDomainModuleSummary(BaseModel):
    module_code: str = Field(..., description="Target domain / module identifier code")
    module_name: str = Field(..., description="Module title")
    total_issues: int = Field(..., description="Total issues in module")


class CrossDomainOverviewResponse(BaseModel):
    total_issues: int = Field(..., description="Total violation records flagged across all domains")
    critical_issues_count: int = Field(..., description="Critical severity issue count")
    warning_issues_count: int = Field(..., description="Warning severity issue count")
    info_issues_count: int = Field(..., description="Info severity issue count")
    total_affected_employees: int = Field(
        ..., description="Distinct active/inactive employees affected"
    )
    overall_health_score: float = Field(
        ..., description="Data quality health score percentage (0 - 100%)"
    )
    rules: list[CrossDomainQualityRuleInfo] = Field(
        default_factory=list, description="Quality rule matrix"
    )
    categories: list[CrossDomainCategorySummary] = Field(
        default_factory=list, description="Category-wise summaries"
    )
    modules: list[CrossDomainModuleSummary] = Field(
        default_factory=list, description="Module/Table-wise summaries"
    )


class CrossDomainIssueRecord(BaseModel):
    record_id: str = Field(..., description="Unique record identifier or composite key")
    emp_id: int | None = Field(default=None, description="Employee ID")
    emp_code: str | None = Field(default=None, description="Employee Code")
    emp_name: str | None = Field(default=None, description="Employee Full Name")
    table_name: str = Field(..., description="Target source database table")
    rule_failed: str = Field(..., description="Rule code identifier that failed")
    severity: str = Field(..., description="Severity level: CRITICAL, WARNING, INFO")
    category: str = Field(..., description="Category code")
    issue_detail: str = Field(..., description="Descriptive evidence detailing the failure")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional contextual fields"
    )


class CrossDomainIssuesListResponse(BaseModel):
    items: list[CrossDomainIssueRecord] = Field(
        default_factory=list, description="Paginated evidence records"
    )
    total: int = Field(..., description="Total evidence items matching filter")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")
    rule_code: str | None = Field(default=None, description="Active rule code filter")
    category: str | None = Field(default=None, description="Active category filter")
    search: str | None = Field(default=None, description="Active search term")
