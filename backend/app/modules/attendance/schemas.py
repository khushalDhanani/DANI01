from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.modules.employee.schemas import IssueSeverity


class AttendanceMetrics(BaseModel):
    total_attendance_records: int
    employees_with_attendance: int
    present_days: int
    present_pct: float
    absent_days: int
    absent_pct: float
    half_days: int
    half_days_pct: float
    leave_days: int
    leave_days_pct: float
    weekly_offs: int
    paid_holidays: int


class PunchMetrics(BaseModel):
    total_punches_logged: int
    valid_punch_pairs: int
    missing_punch_out_count: int
    missing_punch_in_count: int
    late_arrivals_count: int
    early_departures_count: int
    overtime_records_count: int
    total_overtime_hours: float


class ShiftDistributionItem(BaseModel):
    shift_id: int
    shift_code: str
    shift_description: str
    from_time: str
    to_time: str
    assigned_attendance_count: int
    percentage: float


class AttendanceOverviewResponse(BaseModel):
    attendance_metrics: AttendanceMetrics
    punch_metrics: PunchMetrics
    shift_distribution: list[ShiftDistributionItem]
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class AttendanceLogItem(BaseModel):
    att_id: int
    emp_id: int
    emp_code: str | None = None
    emp_name: str
    att_date: str
    att_sal_type: str
    status_label: str
    in_time: str | None = None
    out_time: str | None = None
    off_in_time: str | None = None
    off_out_time: str | None = None
    shift_code: str | None = None
    shift_desc: str | None = None
    late_mins: int = 0
    early_mins: int = 0
    ot_mins: int = 0
    emp_status: str


class AttendanceDirectoryResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[AttendanceLogItem]


class LeaveOverviewResponse(BaseModel):
    total_leave_requests: int
    approved_requests: int
    approved_pct: float
    pending_requests: int
    pending_pct: float
    rejected_requests: int
    rejected_pct: float
    cancelled_requests: int
    cancelled_pct: float
    active_employees_on_leave: int
    total_employees_with_leave_balance: int
    leave_type_distribution: list[dict[str, Any]]
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class LeaveApplicationItem(BaseModel):
    leave_request_id: int
    emp_id: int
    emp_code: str | None = None
    emp_name: str
    request_date: str
    from_date: str
    to_date: str
    leave_type_code: str | None = None
    leave_type_desc: str | None = None
    leave_days: float
    approve_days: float | None = None
    status_id: int | None = None
    status_desc: str
    is_cancelled: bool
    reason: str | None = None


class LeaveApplicationsListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[LeaveApplicationItem]


class LeaveBalanceItem(BaseModel):
    bal_id: int
    emp_id: int
    emp_code: str | None = None
    emp_name: str
    year_month: str
    total_present: float
    total_absent: float
    op_pl: float
    earned_pl: float
    availed_pl: float
    encashed_pl: float
    net_pl_bal: float
    op_cl: float
    earned_cl: float
    availed_cl: float
    net_cl_bal: float
    op_sl: float
    earned_sl: float
    availed_sl: float
    net_sl_bal: float


class LeaveBalancesListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[LeaveBalanceItem]


class AttendanceQualityRuleResult(BaseModel):
    rule_code: str
    rule_name: str
    severity: IssueSeverity
    description: str
    issue_count: int
    impact: str
    recommendation: str


class AttendanceQualityIssueItem(BaseModel):
    record_id: str
    entity_name: str
    entity_type: str
    context_info: str | None = None
    issue_detail: str
    status_detail: str | None = None


class AttendanceQualityIssuesListResponse(BaseModel):
    issue_code: str
    total: int
    limit: int
    offset: int
    items: list[AttendanceQualityIssueItem]


class AttendanceDataQualityResponse(BaseModel):
    overall_health_score: float
    critical_issues_count: int
    warning_issues_count: int
    info_issues_count: int
    rules: list[AttendanceQualityRuleResult]
    summary_by_severity: dict[str, int]
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class OrgHierarchyAttendanceNode(BaseModel):
    id: int
    name: str
    code: str | None = None
    level: str  # COMPANY | LOCATION | DEPARTMENT
    headcount: int = 0
    total_attendance_records: int = 0
    present_count: int = 0
    present_pct: float = 0.0
    late_count: int = 0
    late_pct: float = 0.0
    total_ot_hours: float = 0.0
    avg_ot_hours_per_emp: float = 0.0
    children: list["OrgHierarchyAttendanceNode"] = Field(default_factory=list)


class AttendanceOrgHierarchyResponse(BaseModel):
    companies: list[OrgHierarchyAttendanceNode]
    locations: list[OrgHierarchyAttendanceNode]
    departments: list[OrgHierarchyAttendanceNode]
    hierarchy_tree: list[OrgHierarchyAttendanceNode]
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class DepartmentDetailResponse(BaseModel):
    dept_id: int
    dept_name: str
    dept_code: str | None = None
    headcount: int
    total_attendance_records: int
    present_count: int
    present_pct: float
    absent_count: int
    absent_pct: float
    late_count: int
    late_pct: float
    total_ot_hours: float
    avg_ot_hours_per_emp: float
    active_leaves_count: int
    pending_leaves_count: int
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class EmployeeLifetimeLeaveTypeBreakdown(BaseModel):
    leave_type: str
    leave_code: str | None = "PL"
    request_count: int
    total_days_taken: float
    avg_days_per_request: float = 0.0
    share_pct: float = 0.0
    last_availed_date: str | None = None


class EmployeeLifetimeAttendanceResponse(BaseModel):
    emp_id: int
    emp_code: str
    emp_name: str
    join_date: str | None = None
    tenure_days: int = 0
    tenure_label: str = "N/A"
    dept_name: str | None = None
    loc_name: str | None = None
    is_active: bool = True
    total_attendance_records: int = 0
    present_days: int = 0
    present_pct: float = 0.0
    absent_days: int = 0
    absent_pct: float = 0.0
    half_days: int = 0
    leave_days: int = 0
    weekly_offs: int = 0
    paid_holidays: int = 0
    late_arrivals_count: int = 0
    total_late_mins: int = 0
    early_exits_count: int = 0
    total_early_mins: int = 0
    overtime_records_count: int = 0
    total_ot_hours: float = 0.0
    missing_punch_outs: int = 0
    missing_punch_ins: int = 0
    unpunched_salary_days: int = 0
    unauthorized_absence_days: int = 0
    leave_covered_absence_days: int = 0
    unauthorized_absence_pct: float = 0.0
    absconding_risk_level: str = "LOW"
    leaves_breakdown: list[EmployeeLifetimeLeaveTypeBreakdown] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
