from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.modules.employee.schemas import IssueSeverity


class PayrollTableSchemaInfo(BaseModel):
    table_name: str
    table_type: str
    record_count: int
    primary_key: str
    foreign_keys: list[str] = Field(default_factory=list)


class PayrollRelationshipInfo(BaseModel):
    source_table: str
    target_table: str
    cardinality: str
    status: str  # Confirmed / Likely
    join_condition: str


class PayrollMetadataResponse(BaseModel):
    module_code: str = "PAYROLL"
    module_name: str = "Payroll & Salary Analysis"
    tables: list[PayrollTableSchemaInfo] = Field(default_factory=list)
    relationships: list[PayrollRelationshipInfo] = Field(default_factory=list)


class PayrollMonthlySummaryItem(BaseModel):
    sal_month: str
    record_count: int
    total_earned: float
    total_deduction: float
    total_net_pay: float


class PayrollOverviewResponse(BaseModel):
    total_payroll_records: int = 0
    total_employees_with_payroll: int = 0
    total_employees_without_payroll: int = 0
    latest_payroll_month: str = "N/A"
    latest_month_record_count: int = 0
    latest_month_net_pay: float = 0.0
    lifetime_total_net_pay: float = 0.0
    lifetime_total_earned: float = 0.0
    lifetime_total_deduction: float = 0.0
    monthly_trends: list[PayrollMonthlySummaryItem] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class PayrollRegisterItem(BaseModel):
    earned_sal_id: int
    emp_id: int
    emp_code: str
    emp_name: str
    dept_name: str | None = None
    sal_month: str
    paid_days: float = 0.0
    present_days: float = 0.0
    total_earned: float = 0.0
    total_deduction: float = 0.0
    net_pay: float = 0.0
    ctc_gross: float = 0.0
    pay_date: str | None = None
    is_active: bool = True


class PayrollRegisterListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[PayrollRegisterItem] = Field(default_factory=list)


class PayrollQualityRuleInfo(BaseModel):
    rule_code: str
    rule_name: str
    severity: IssueSeverity
    description: str
    issue_count: int
    impact: str
    recommendation: str


class PayrollDataQualityResponse(BaseModel):
    overall_health_score: float = 100.0
    total_issues_count: int = 0
    critical_issues_count: int = 0
    warning_issues_count: int = 0
    info_issues_count: int = 0
    rules: list[PayrollQualityRuleInfo] = Field(default_factory=list)
    summary_by_severity: dict[str, int] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class PayrollQualityIssueItem(BaseModel):
    record_id: int
    rule_code: str
    severity: IssueSeverity
    emp_id: int | None = None
    emp_code: str | None = None
    emp_name: str | None = None
    issue_detail: str
    sal_month: str | None = None
    status_detail: str = "VIOLATION"


class PayrollQualityIssuesListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[PayrollQualityIssueItem] = Field(default_factory=list)


class EmployeePayslipItem(BaseModel):
    earned_sal_id: int
    sal_month: str
    paid_days: float = 0.0
    present_days: float = 0.0
    absent_days: float = 0.0
    total_earned: float = 0.0
    total_deduction: float = 0.0
    net_pay: float = 0.0
    bank_name: str | None = None
    bank_account_no: str | None = None
    pay_date: str | None = None


class EmployeePayrollHistoryResponse(BaseModel):
    emp_id: int
    emp_code: str
    emp_name: str
    dept_name: str | None = None
    is_active: bool = True
    total_payslips_count: int = 0
    lifetime_net_pay: float = 0.0
    latest_month: str = "N/A"
    history_items: list[EmployeePayslipItem] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
