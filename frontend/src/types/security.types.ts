import type { IssueSeverity } from './employee.types';

export interface SecurityAccountOverview {
  total_user_accounts: number;
  active_users: number;
  active_users_pct: number;
  inactive_users: number;
  inactive_users_pct: number;
  deleted_users: number;
  deleted_users_pct: number;
  linked_to_employee: number;
  linked_to_employee_pct: number;
  unlinked_users: number;
  unlinked_users_pct: number;
}

export interface SecurityEmpLinkOverview {
  total_active_employees: number;
  active_emps_with_active_user: number;
  active_emps_with_active_user_pct: number;
  active_emps_without_active_user: number;
  active_emps_without_active_user_pct: number;
}

export interface SecurityPostureOverview {
  master_admins_count: number;
  mfa_enabled_count: number;
  mfa_enabled_pct: number;
  mobile_app_users_count: number;
  sma_users_count: number;
  api_accessed_count: number;
  never_logged_in_count: number;
  total_registered_devices: number;
}

export interface SecurityRoleDistributionItem {
  role_id: number;
  role_desc: string;
  total_users: number;
  active_users: number;
  percentage: number;
}

export interface SecurityOverviewResponse {
  account_metrics: SecurityAccountOverview;
  employee_link_metrics: SecurityEmpLinkOverview;
  posture_metrics: SecurityPostureOverview;
  role_distribution: SecurityRoleDistributionItem[];
  generated_at: string;
}

export interface SecurityUserItem {
  user_id: number;
  username: string | null;
  user_email: string | null;
  user_mobile: string | null;
  role_id: number | null;
  role_desc: string | null;
  emp_id: number | null;
  emp_code: string | null;
  emp_name: string | null;
  emp_status: string | null;
  is_active: boolean;
  is_deleted: boolean;
  is_master_admin: boolean;
  is_mfa_enabled: boolean;
  is_mobile_app_user: boolean;
  last_access_api: string | null;
  created_at: string | null;
  registered_devices_count: number;
}

export interface SecurityUserListResponse {
  total: number;
  limit: number;
  offset: number;
  items: SecurityUserItem[];
}

export interface SecurityRoleItem {
  role_id: number;
  role_desc: string;
  comp_id: number | null;
  is_active: boolean;
  is_deleted: boolean;
  total_assigned_users: number;
  active_assigned_users: number;
  assigned_menus_count: number;
  insert_perms_count: number;
  update_perms_count: number;
  delete_perms_count: number;
  view_perms_count: number;
}

export interface SecurityRoleListResponse {
  total_roles: number;
  active_roles: number;
  items: SecurityRoleItem[];
}

export interface SecurityMenuPermissionItem {
  role_menu_id: number;
  menu_id: number;
  menu_name: string | null;
  form_name: string | null;
  route_portal: string | null;
  can_insert: boolean;
  can_update: boolean;
  can_delete: boolean;
  can_view: boolean;
  is_active: boolean;
}

export interface SecurityRoleDetailResponse {
  role_id: number;
  role_desc: string;
  is_active: boolean;
  is_deleted: boolean;
  total_permissions: number;
  permissions: SecurityMenuPermissionItem[];
}

export interface SecurityQualityRuleResult {
  rule_code: string;
  rule_name: string;
  severity: IssueSeverity;
  description: string;
  issue_count: number;
  impact: string;
  recommendation: string;
}

export interface SecurityDataQualityResponse {
  overall_security_score: number;
  critical_issues_count: number;
  warning_issues_count: number;
  info_issues_count: number;
  rules: SecurityQualityRuleResult[];
  summary_by_severity: Record<string, number>;
  generated_at: string;
}

export interface SecurityQualityIssueItem {
  record_id: number;
  entity_type: string;
  entity_name: string;
  issue_code: string;
  issue_detail: string;
  account_role: string | null;
  status_detail: string | null;
}

export interface SecurityQualityIssuesListResponse {
  issue_code: string;
  issue_name: string;
  severity: IssueSeverity;
  total: number;
  limit: number;
  offset: number;
  items: SecurityQualityIssueItem[];
}
