import type { IssueSeverity } from "./employee.types";

export interface AttendanceMetrics {
  total_attendance_records: number;
  employees_with_attendance: number;
  present_days: number;
  present_pct: number;
  absent_days: number;
  absent_pct: number;
  half_days: number;
  half_days_pct: number;
  leave_days: number;
  leave_days_pct: number;
  weekly_offs: number;
  paid_holidays: number;
}

export interface PunchMetrics {
  total_punches_logged: number;
  valid_punch_pairs: number;
  missing_punch_out_count: number;
  missing_punch_in_count: number;
  late_arrivals_count: number;
  early_departures_count: number;
  overtime_records_count: number;
  total_overtime_hours: number;
}

export interface ShiftDistributionItem {
  shift_id: number;
  shift_code: string;
  shift_description: string;
  from_time: string;
  to_time: string;
  assigned_attendance_count: number;
  percentage: number;
}

export interface AttendanceOverviewResponse {
  attendance_metrics: AttendanceMetrics;
  punch_metrics: PunchMetrics;
  shift_distribution: ShiftDistributionItem[];
  generated_at: string;
}

export interface AttendanceLogItem {
  att_id: number;
  emp_id: number;
  emp_code?: string;
  emp_name: string;
  att_date: string;
  att_sal_type: string;
  status_label: string;
  in_time?: string;
  out_time?: string;
  off_in_time?: string;
  off_out_time?: string;
  shift_code?: string;
  shift_desc?: string;
  late_mins: number;
  early_mins: number;
  ot_mins: number;
  emp_status: string;
}

export interface AttendanceDirectoryResponse {
  total: number;
  limit: number;
  offset: number;
  items: AttendanceLogItem[];
}

export interface LeaveOverviewResponse {
  total_leave_requests: number;
  approved_requests: number;
  approved_pct: number;
  pending_requests: number;
  pending_pct: number;
  rejected_requests: number;
  rejected_pct: number;
  cancelled_requests: number;
  cancelled_pct: number;
  active_employees_on_leave: number;
  total_employees_with_leave_balance: number;
  leave_type_distribution: {
    leave_type: string;
    short_code?: string;
    request_count: number;
  }[];
  generated_at: string;
}

export interface LeaveApplicationItem {
  leave_request_id: number;
  emp_id: number;
  emp_code?: string;
  emp_name: string;
  request_date: string;
  from_date: string;
  to_date: string;
  leave_type_code?: string;
  leave_type_desc?: string;
  leave_days: number;
  approve_days?: number;
  status_id?: number;
  status_desc: string;
  is_cancelled: boolean;
  reason?: string;
}

export interface LeaveApplicationsListResponse {
  total: number;
  limit: number;
  offset: number;
  items: LeaveApplicationItem[];
}

export interface LeaveBalanceItem {
  bal_id: number;
  emp_id: number;
  emp_code?: string;
  emp_name: string;
  year_month: string;
  total_present: number;
  total_absent: number;
  op_pl: number;
  earned_pl: number;
  availed_pl: number;
  encashed_pl: number;
  net_pl_bal: number;
  op_cl: number;
  earned_cl: number;
  availed_cl: number;
  net_cl_bal: number;
  op_sl: number;
  earned_sl: number;
  availed_sl: number;
  net_sl_bal: number;
}

export interface LeaveBalancesListResponse {
  total: number;
  limit: number;
  offset: number;
  items: LeaveBalanceItem[];
}

export interface AttendanceQualityRuleResult {
  rule_code: string;
  rule_name: string;
  severity: IssueSeverity;
  description: string;
  issue_count: number;
  impact: string;
  recommendation: string;
}

export interface AttendanceQualityIssueItem {
  record_id: string;
  entity_name: string;
  entity_type: string;
  context_info?: string;
  issue_detail: string;
  status_detail?: string;
}

export interface AttendanceQualityIssuesListResponse {
  issue_code: string;
  total: number;
  limit: number;
  offset: number;
  items: AttendanceQualityIssueItem[];
}

export interface AttendanceDataQualityResponse {
  overall_health_score: number;
  critical_issues_count: number;
  warning_issues_count: number;
  info_issues_count: number;
  rules: AttendanceQualityRuleResult[];
  summary_by_severity: Record<string, number>;
  generated_at: string;
}

export interface OrgHierarchyAttendanceNode {
  id: number;
  name: string;
  code?: string;
  level: "COMPANY" | "LOCATION" | "DEPARTMENT";
  headcount: number;
  total_attendance_records: number;
  present_count: number;
  present_pct: number;
  late_count: number;
  late_pct: number;
  total_ot_hours: number;
  avg_ot_hours_per_emp: number;
  children: OrgHierarchyAttendanceNode[];
}

export interface AttendanceOrgHierarchyResponse {
  companies: OrgHierarchyAttendanceNode[];
  locations: OrgHierarchyAttendanceNode[];
  departments: OrgHierarchyAttendanceNode[];
  hierarchy_tree: OrgHierarchyAttendanceNode[];
  generated_at: string;
}

export interface DepartmentDetailResponse {
  dept_id: number;
  dept_name: string;
  dept_code?: string;
  headcount: number;
  total_attendance_records: number;
  present_count: number;
  present_pct: number;
  absent_count: number;
  absent_pct: number;
  late_count: number;
  late_pct: number;
  total_ot_hours: number;
  avg_ot_hours_per_emp: number;
  active_leaves_count: number;
  pending_leaves_count: number;
  generated_at: string;
}

export interface EmployeeLifetimeLeaveTypeBreakdown {
  leave_type: string;
  leave_code?: string;
  request_count: number;
  total_days_taken: number;
  avg_days_per_request?: number;
  share_pct?: number;
  last_availed_date?: string;
}

export interface EmployeeLifetimeAttendanceResponse {
  emp_id: number;
  emp_code: string;
  emp_name: string;
  join_date?: string;
  tenure_days: number;
  tenure_label: string;
  dept_name?: string;
  loc_name?: string;
  is_active: boolean;
  total_attendance_records: number;
  present_days: number;
  present_pct: number;
  absent_days: number;
  absent_pct: number;
  half_days: number;
  leave_days: number;
  weekly_offs: number;
  paid_holidays: number;
  late_arrivals_count: number;
  total_late_mins: number;
  early_exits_count: number;
  total_early_mins: number;
  overtime_records_count: number;
  total_ot_hours: number;
  missing_punch_outs: number;
  missing_punch_ins: number;
  unpunched_salary_days: number;
  unauthorized_absence_days: number;
  leave_covered_absence_days: number;
  unauthorized_absence_pct: number;
  absconding_risk_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  leaves_breakdown: EmployeeLifetimeLeaveTypeBreakdown[];
  risk_signals: string[];
  generated_at: string;
}




