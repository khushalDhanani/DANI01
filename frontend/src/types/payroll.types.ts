export interface PayrollTableSchemaInfo {
  table_name: string;
  table_type: string;

  record_count: number;
  primary_key: string;
  foreign_keys: string[];
}

export interface PayrollRelationshipInfo {
  source_table: string;
  target_table: string;
  cardinality: string;
  status: string;
  join_condition: string;
}

export interface PayrollMetadataResponse {
  module_code: string;
  module_name: string;
  tables: PayrollTableSchemaInfo[];
  relationships: PayrollRelationshipInfo[];
}

export interface PayrollMonthlySummaryItem {
  sal_month: string;
  record_count: number;
  total_earned: number;
  total_deduction: number;
  total_net_pay: number;
}

export interface PayrollOverviewResponse {
  total_payroll_records: number;
  total_employees_with_payroll: number;
  total_employees_without_payroll: number;
  latest_payroll_month: string;
  latest_month_record_count: number;
  latest_month_net_pay: number;
  lifetime_total_net_pay: number;
  lifetime_total_earned: number;
  lifetime_total_deduction: number;
  monthly_trends: PayrollMonthlySummaryItem[];
  generated_at: string;
}

export interface PayrollRegisterItem {
  earned_sal_id: number;
  emp_id: number;
  emp_code: string;
  emp_name: string;
  dept_name?: string;
  sal_month: string;
  paid_days: number;
  present_days: number;
  total_earned: number;
  total_deduction: number;
  net_pay: number;
  ctc_gross: number;
  pay_date?: string;
  is_active: boolean;
}

export interface PayrollRegisterListResponse {
  total: number;
  limit: number;
  offset: number;
  items: PayrollRegisterItem[];
}

export interface PayrollQualityRuleInfo {
  rule_code: string;
  rule_name: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  description: string;
  issue_count: number;
  impact: string;
  recommendation: string;
}

export interface PayrollDataQualityResponse {
  overall_health_score: number;
  total_issues_count: number;
  critical_issues_count: number;
  warning_issues_count: number;
  info_issues_count: number;
  rules: PayrollQualityRuleInfo[];
  summary_by_severity: Record<string, number>;
  generated_at: string;
}

export interface PayrollQualityIssueItem {
  record_id: number;
  rule_code: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  emp_id?: number;
  emp_code?: string;
  emp_name?: string;
  issue_detail: string;
  sal_month?: string;
  status_detail: string;
}

export interface PayrollQualityIssuesListResponse {
  total: number;
  limit: number;
  offset: number;
  items: PayrollQualityIssueItem[];
}

export interface EmployeePayslipItem {
  earned_sal_id: number;
  sal_month: string;
  paid_days: number;
  present_days: number;
  absent_days: number;
  total_earned: number;
  total_deduction: number;
  net_pay: number;
  bank_name?: string;
  bank_account_no?: string;
  pay_date?: string;
}

export interface EmployeePayrollHistoryResponse {
  emp_id: number;
  emp_code: string;
  emp_name: string;
  dept_name?: string;
  is_active: boolean;
  total_payslips_count: number;
  lifetime_net_pay: number;
  latest_month: string;
  history_items: EmployeePayslipItem[];
  generated_at: string;
}
