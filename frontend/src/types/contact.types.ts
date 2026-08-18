/**
 * Types for Contact & Email Analysis Module
 */

export interface ContactEmailOverview {
  total_active_employees: number;
  with_company_email: number;
  with_company_email_pct: number;
  with_personal_email: number;
  with_personal_email_pct: number;
  with_alternate_email: number;
  with_alternate_email_pct: number;
  with_any_email: number;
  with_any_email_pct: number;
  without_any_email: number;
  without_any_email_pct: number;
  without_company_email: number;
  without_company_email_pct: number;
  without_personal_email: number;
  without_personal_email_pct: number;
}

export interface ContactPhoneOverview {
  with_primary_phone: number;
  with_primary_phone_pct: number;
  with_secondary_phone: number;
  with_secondary_phone_pct: number;
  with_corr_phone1: number;
  with_corr_phone1_pct: number;
  with_corr_phone2: number;
  with_corr_phone2_pct: number;
  with_any_phone: number;
  with_any_phone_pct: number;
  without_primary_phone: number;
  without_primary_phone_pct: number;
  without_any_phone: number;
  without_any_phone_pct: number;
  primary_phone_verified: number;
  primary_phone_verified_pct: number;
  secondary_phone_verified: number;
  secondary_phone_verified_pct: number;
}

export interface ContactAddressOverview {
  with_permanent_address: number;
  with_permanent_address_pct: number;
  with_correspondence_address: number;
  with_correspondence_address_pct: number;
  with_permanent_pincode: number;
  with_correspondence_pincode: number;
  with_ice_emergency_contact: number;
  with_ice_emergency_contact_pct: number;
}

export interface ContactDomainBreakdownItem {
  domain: string;
  count: number;
  percentage: number;
}

export interface ContactOverviewResponse {
  total_active_employees: number;
  email_metrics: ContactEmailOverview;
  phone_metrics: ContactPhoneOverview;
  address_metrics: ContactAddressOverview;
  domain_breakdown: ContactDomainBreakdownItem[];
  security_user_sync: {
    total_active_users?: number;
    users_with_email?: number;
    users_with_mobile?: number;
  };
  generated_at: string;
}

export interface ContactDirectoryItem {
  emp_id: number;
  emp_code?: string | null;
  full_name: string;
  department?: string | null;
  designation?: string | null;
  location?: string | null;
  company_email?: string | null;
  personal_email?: string | null;
  alternate_email?: string | null;
  primary_phone?: string | null;
  is_verified_phone1: boolean;
  secondary_phone?: string | null;
  is_verified_phone2: boolean;
  corr_phone1?: string | null;
  ice_mobile?: string | null;
  ice_contact_name?: string | null;
  permanent_pincode?: string | null;
  correspondence_pincode?: string | null;
  has_valid_email: boolean;
  has_valid_phone: boolean;
}

export interface ContactDirectoryListResponse {
  total: number;
  limit: number;
  offset: number;
  items: ContactDirectoryItem[];
}

export type IssueSeverity = 'CRITICAL' | 'WARNING' | 'INFO';

export interface ContactQualityRuleResult {
  rule_code: string;
  rule_name: string;
  severity: IssueSeverity;
  description: string;
  issue_count: number;
  impact: string;
  recommendation: string;
}

export interface ContactDataQualityResponse {
  overall_health_score: number;
  critical_issues_count: number;
  warning_issues_count: number;
  info_issues_count: number;
  rules: ContactQualityRuleResult[];
  summary_by_severity: Record<string, number>;
  generated_at: string;
}

export interface ContactQualityIssueItem {
  record_id: number;
  emp_code?: string | null;
  entity_name: string;
  issue_code: string;
  issue_detail: string;
  contact_value?: string | null;
}

export interface ContactQualityIssuesListResponse {
  issue_code: string;
  issue_name: string;
  severity: IssueSeverity;
  total: number;
  limit: number;
  offset: number;
  items: ContactQualityIssueItem[];
}

export type ContactEmailFilter = 'WITH_COMPANY_EMAIL' | 'WITH_PERSONAL_EMAIL' | 'WITHOUT_ANY_EMAIL' | 'WITH_ANY_EMAIL';
export type ContactPhoneFilter = 'WITH_PRIMARY_PHONE' | 'MISSING_PRIMARY_PHONE' | 'UNVERIFIED_PHONE' | 'WITH_ICE_CONTACT';
