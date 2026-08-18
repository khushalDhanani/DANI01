export type IssueSeverity = "CRITICAL" | "WARNING" | "INFO";

export interface EmployeeStatusCount {
  total: number;
  active: number;
  inactive: number;
  resigned: number;
  deleted: number;
}

export interface DistributionItem {
  label: string;
  count: number;
  percentage: number;
}

export interface EmployeeOverviewResponse {
  status_counts: EmployeeStatusCount;
  gender_distribution: DistributionItem[];
  employment_type_distribution: DistributionItem[];
  department_distribution: DistributionItem[];
  company_distribution: DistributionItem[];
  top_locations: DistributionItem[];
  user_account_coverage: {
    active_employees_with_login: number;
    login_coverage_pct: number;
    total_active_logins: number;
  };
  reporting_coverage: {
    active_employees_with_manager: number;
    manager_coverage_pct: number;
  };
  generated_at: string;
}

export interface TableNodeMetadata {
  schema: string;
  table: string;
  role: string;
  row_count: number;
  key_column: string;
  confidence: "CONFIRMED" | "LIKELY";
  description: string;
}

export interface RelationshipEdge {
  source_table: string;
  target_table: string;
  source_key: string;
  target_key: string;
  relationship_type: string;
  confidence: "CONFIRMED" | "LIKELY";
  description: string;
}

export interface EmployeeStructureResponse {
  master_table: string;
  canonical_key: string;
  business_key: string;
  tables: TableNodeMetadata[];
  relationships: RelationshipEdge[];
  confidence_summary: Record<string, number>;
}

export interface QualityRuleResult {
  rule_code: string;
  rule_name: string;
  severity: IssueSeverity;
  description: string;
  issue_count: number;
  impact: string;
  recommendation: string;
}

export interface EmployeeDataQualityResponse {
  overall_health_score: number;
  critical_issues_count: number;
  warning_issues_count: number;
  info_issues_count: number;
  rules: QualityRuleResult[];
  summary_by_severity: Record<string, number>;
  generated_at: string;
}

export interface QualityIssueRecord {
  emp_id: number | null;
  emp_code: string | null;
  full_name: string | null;
  company_email: string | null;
  phone: string | null;
  department_name: string | null;
  designation_name: string | null;
  emp_is_active: boolean | null;
  emp_resign_date: string | null;
  issue_code: string;
  issue_detail: string;
}

export interface QualityIssuesListResponse {
  issue_code: string;
  issue_name: string;
  severity: IssueSeverity;
  total: number;
  limit: number;
  offset: number;
  items: QualityIssueRecord[];
}

export interface EmployeeListItem {
  emp_id: number;
  emp_code: string | null;
  full_name: string;
  first_name: string;
  middle_name: string | null;
  last_name: string | null;
  gender: string | null;
  birth_date: string | null;
  company_email: string | null;
  personal_email: string | null;
  phone: string | null;
  pan_no: string | null;
  aadhar_no: string | null;
  joining_date: string | null;
  resign_date: string | null;
  is_active: boolean;
  is_deleted: boolean;
  employment_type: string | null;
  company_name: string | null;
  department_name: string | null;
  designation_name: string | null;
  location_name: string | null;
  grade_desc: string | null;
  functional_mgr_id: number | null;
  functional_mgr_name: string | null;
  admin_mgr_id: number | null;
  admin_mgr_name: string | null;
  user_id: number | null;
  user_name: string | null;
  user_is_active: boolean | null;
  role_desc: string | null;
}

export interface EmployeeListResponse {
  total: number;
  active_count: number;
  inactive_count: number;
  limit: number;
  offset: number;
  items: EmployeeListItem[];
}

export interface OfficialHistoryItem {
  office_det_id: number;
  dept_name: string | null;
  desig_name: string | null;
  loc_name: string | null;
  grade_desc: string | null;
  applicable_from: string | null;
  joining_date: string | null;
  resign_date: string | null;
  is_active: boolean;
}

export interface FamilyMemberItem {
  family_det_id: number;
  name: string;
  relation_name: string | null;
  birth_date: string | null;
  phone: string | null;
  is_emergency_contact: boolean;
}

export interface QualificationItem {
  qual_det_id: number;
  degree_name: string | null;
  passing_year: number | null;
  percentage_grade: string | null;
  institute_name: string | null;
}

export interface ExperienceItem {
  exp_det_id: number;
  company_name: string | null;
  designation: string | null;
  from_date: string | null;
  to_date: string | null;
  last_drawn_ctc: string | null;
}

export interface EmployeeDetailResponse {
  emp_id: number;
  emp_code: string | null;
  title: string | null;
  first_name: string;
  middle_name: string | null;
  last_name: string | null;
  full_name: string;
  gender: string | null;
  birth_date: string | null;
  blood_group: string | null;
  marital_status: string | null;
  religion: string | null;
  caste_category: string | null;
  nationality: string | null;
  company_email: string | null;
  personal_email: string | null;
  phone1: string | null;
  phone2: string | null;
  direct_number: string | null;
  ext_number: string | null;
  cug_number: string | null;
  correspondence_address: string | null;
  corr_pincode: string | null;
  permanent_address: string | null;
  perm_pincode: string | null;
  pan_no: string | null;
  aadhar_no: string | null;
  uan_no: string | null;
  pf_no: string | null;
  esic_no: string | null;
  voter_id: string | null;
  driving_license_no: string | null;
  pran_no: string | null;
  sap_gl_code: string | null;
  microsoft_object_id: string | null;
  joining_date: string | null;
  resign_date: string | null;
  is_active: boolean;
  is_deleted: boolean;
  employment_type: string | null;
  company_name: string | null;
  current_dept: string | null;
  current_desig: string | null;
  current_location: string | null;
  current_grade: string | null;
  functional_mgr_id: number | null;
  functional_mgr_code: string | null;
  functional_mgr_name: string | null;
  admin_mgr_id: number | null;
  admin_mgr_code: string | null;
  admin_mgr_name: string | null;
  user_id: number | null;
  user_name: string | null;
  user_email: string | null;
  user_ad_id: string | null;
  user_is_active: boolean | null;
  role_desc: string | null;
  official_history: OfficialHistoryItem[];
  family_members: FamilyMemberItem[];
  qualifications: QualificationItem[];
  experiences: ExperienceItem[];
}

export interface EmployeeRecordsFilterParams {
  search?: string;
  status?: string;
  dept_id?: number;
  desig_id?: number;
  loc_id?: number;
  compId?: number;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

