export interface CrossDomainQualityRuleInfo {
  rule_code: string;

  rule_name: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  category: string;
  description: string;
  impact: string;
  issue_count: number;
  affected_employees_count: number;
}

export interface CrossDomainCategorySummary {
  category_code: string;
  category_name: string;
  rule_count: number;
  total_issues: number;
  critical_issues: number;
  warning_issues: number;
  info_issues: number;
}

export interface CrossDomainModuleSummary {
  module_code: string;
  module_name: string;
  total_issues: number;
}

export interface CrossDomainOverviewResponse {
  total_issues: number;
  critical_issues_count: number;
  warning_issues_count: number;
  info_issues_count: number;
  total_affected_employees: number;
  overall_health_score: number;
  rules: CrossDomainQualityRuleInfo[];
  categories: CrossDomainCategorySummary[];
  modules: CrossDomainModuleSummary[];
}

export interface CrossDomainIssueRecord {
  record_id: string;
  emp_id?: number | null;
  emp_code?: string | null;
  emp_name?: string | null;
  table_name: string;
  rule_failed: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  category: string;
  issue_detail: string;
}

export interface CrossDomainIssuesListResponse {
  items: CrossDomainIssueRecord[];
  total: number;
  limit: number;
  offset: number;
  rule_code?: string;
  category?: string;
  search?: string;
}
