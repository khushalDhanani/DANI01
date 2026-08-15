import React from "react";
import { render, screen } from "@testing-library/react-native";
import { ContactQualitySection } from "@/features/modules/person/ContactQualitySection";
import type { ContactQualitySummary } from "@/types/modules.types";

jest.mock("expo-router", () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

const mockQualitySummary: ContactQualitySummary = {
  // 1. Contact Channels
  persons_without_email: 12,
  persons_without_phone: 18,
  invalid_emails: 3,
  invalid_phones: 5,
  invalid_urls: 2,
  unverified_contacts: 4,
  duplicate_email_cross_persons: 6,
  duplicate_email_same_person: 1,
  duplicate_phone_cross_persons: 4,
  duplicate_phone_same_person: 2,
  persons_multiple_primary: 1,
  primary_contact_inactive: 1,

  // 2. Address & Location Quality
  addr_missing_postal_code: 8,
  addr_invalid_pin_format: 2,
  addr_street_without_city: 3,
  addr_city_without_state: 4,
  addr_missing_geocodes: 10,
  addr_duplicate_same_person: 1,

  // 3. Profile & Chronological Integrity
  person_anniversary_before_birth: 0,
  person_invalid_birth_date: 1,
  person_birth_date_ancient: 2,
  person_suspicious_dummy_names: 3,
  person_missing_lastname_only: 5,

  // 4. Employment & Lifecycle Consistency
  active_emp_missing_title: 7,
  inactive_with_empid: 2,
  status_active_and_deleted: 0,
  stale_temp_persons: 1,

  // 5. Governance & Blacklist Compliance
  blacklist_unapproved: 0,
  blacklist_missing_details: 0,

  // 6. Entity Linkages & Child Records
  company_orphan_links: 0,
  company_duplicate_links: 0,
  company_missing_role: 0,
  extra_field_orphan_id: 0,
  extra_field_duplicate_entries: 0,

  // 7. Audit Trail & Sync Integration
  deleted_missing_del_date: 0,
  audit_del_before_ent: 0,
  sync_zimbra_missing_id: 0,

  // 8. Distinct Person Quality Telemetry
  persons_with_critical_issues: 8,
  persons_with_warning_issues: 42,
  persons_with_any_issue: 50,
  total_clean_persons: 800,
  health_score_pct: 94.1,

  // 9. Standardized Aggregate Findings
  total_critical_findings: 10,
  total_warning_findings: 55,
  total_info_findings: 16,

  // Scope & Metadata
  total_persons_evaluated: 850,
  total_inactive_persons: 150,
  total_deleted_persons: 50,
  related_tables_checked: 6,
  calculated_at: "2026-02-15T12:00:00Z",
  duration_ms: 120,
};

jest.mock("@/hooks/useModules", () => ({
  useContactQualitySummary: () => ({
    data: mockQualitySummary,
    isLoading: false,
    isError: false,
    refetch: jest.fn(),
  }),
}));

describe("ContactQualitySection Feature Component", () => {
  it("renders quality scorecard with authoritative total counts", async () => {
    await render(<ContactQualitySection />);
    expect(screen.getByText("Data Quality & Integrity Analyzer")).toBeTruthy();
    expect(screen.getByText("850 Active Evaluated")).toBeTruthy();
    expect(screen.getByText("6 Tables Checked")).toBeTruthy();
  });

  it("renders rules and severity metrics accurately", async () => {
    await render(<ContactQualitySection />);
    expect(screen.getByText("Missing Email")).toBeTruthy();
    expect(screen.getByText("Invalid Email")).toBeTruthy();
    expect(screen.getByText("Missing Phone")).toBeTruthy();
  });
});
