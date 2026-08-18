export type OrgUnitType =
  | "COMPANY"
  | "LOCATION"
  | "MAIN_DEPT"
  | "DEPARTMENT"
  | "DESIGNATION"
  | "GRADE";

export interface OrgScaleCounts {
  total_companies: number;
  active_companies: number;
  total_locations: number;
  active_locations: number;
  total_main_depts: number;
  active_main_depts: number;
  total_departments: number;
  active_departments: number;
  total_designations: number;
  active_designations: number;
  total_grades: number;
  active_grades: number;
  total_active_units: number;
  total_inactive_units: number;
}

export interface OrgHeadcountItem {
  id: number;
  name: string;
  code?: string | null;
  count: number;
  percentage: number;
}

export interface OrgOverviewResponse {
  scale_counts: OrgScaleCounts;
  headcount_by_company: OrgHeadcountItem[];
  headcount_by_location: OrgHeadcountItem[];
  headcount_by_top_departments: OrgHeadcountItem[];
  headcount_by_grade: OrgHeadcountItem[];
  active_employee_total: number;
  generated_at: string;
}

export interface OrgHierarchyNode {
  id: number;
  name: string;
  code?: string | null;
  level: "COMPANY" | "LOCATION" | "DEPARTMENT" | "DESIGNATION" | string;
  headcount: number;
  head_emp_id?: number | null;
  head_name?: string | null;
  head_code?: string | null;
  children: OrgHierarchyNode[];
}

export interface OrgHierarchyResponse {
  companies: OrgHierarchyNode[];
  total_active_employees: number;
  total_hierarchical_paths: number;
}

export interface OrgUnitListItem {
  unit_id: number;
  unit_type: OrgUnitType;
  unit_code?: string | null;
  unit_name: string;
  parent_id?: number | null;
  parent_name?: string | null;
  head_emp_id?: number | null;
  head_name?: string | null;
  head_code?: string | null;
  active_headcount: number;
  is_active: boolean;
  is_deleted: boolean;
}

export interface OrgUnitListResponse {
  total: number;
  limit: number;
  offset: number;
  items: OrgUnitListItem[];
}

export interface OrgQualityRuleResult {
  rule_code: string;
  rule_name: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  description: string;
  issue_count: number;
  impact: string;
  recommendation: string;
}

export interface OrgDataQualityResponse {
  overall_health_score: number;
  critical_issues_count: number;
  warning_issues_count: number;
  info_issues_count: number;
  rules: OrgQualityRuleResult[];
  summary_by_severity: Record<string, number>;
  generated_at: string;
}

export interface OrgQualityIssueRecord {
  record_id: number | string;
  entity_type: string;
  entity_name: string;
  issue_code: string;
  issue_detail: string;
  extra_context?: Record<string, unknown>;
}

export interface OrgQualityIssuesListResponse {
  issue_code: string;
  issue_name: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  total: number;
  limit: number;
  offset: number;
  items: OrgQualityIssueRecord[];
}

export interface OrgReportingNode {
  emp_id: number;
  emp_code?: string | null;
  full_name: string;
  designation?: string | null;
  department?: string | null;
  location?: string | null;
  role_type: "EXECUTIVE" | "DIRECTOR" | "HOD" | "LEAD" | "STAFF" | string;
  direct_reports_count: number;
  subordinates: OrgReportingNode[];
}

export interface OrgReportingTreeResponse {
  roots: OrgReportingNode[];
  total_assigned_managers: number;
}
