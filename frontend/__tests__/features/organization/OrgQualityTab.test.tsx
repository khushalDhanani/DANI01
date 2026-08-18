import React from "react";
import { render, screen } from "@testing-library/react-native";
import { OrgQualityTab } from "@/features/modules/organization/OrgQualityTab";
import type { OrgDataQualityResponse } from "@/types/organization.types";

jest.mock("@/hooks/useOrganization", () => ({
  useOrgQualityIssues: jest.fn().mockReturnValue({
    data: { items: [], total: 0 },
    isLoading: false,
  }),
}));

const mockQuality: OrgDataQualityResponse = {
  overall_health_score: 96.5,
  critical_issues_count: 7,
  warning_issues_count: 94,
  info_issues_count: 32,
  rules: [
    {
      rule_code: "MISSING_OFFICIAL_RECORD",
      rule_name: "Active Employee Missing Official Record",
      severity: "CRITICAL",
      description: "Active employees with no job position record in EmployeeOfficialDet.",
      issue_count: 6,
      impact: "Excluded from department payroll and reporting lines.",
      recommendation: "Assign an active posting record.",
    },
    {
      rule_code: "EMPTY_LOCATIONS",
      rule_name: "Empty Active Locations (0 Staff)",
      severity: "WARNING",
      description: "Active locations or plants with zero currently assigned active employees.",
      issue_count: 4,
      impact: "Unused site masters cluttering location selectors.",
      recommendation: "Review whether these sites should be deactivated.",
    },
  ],
  summary_by_severity: { CRITICAL: 7, WARNING: 94, INFO: 32 },
  generated_at: "2026-08-17T12:00:00Z",
};

describe("OrgQualityTab Feature Component", () => {
  it("renders loading state when isLoading is true", async () => {
    await render(<OrgQualityTab quality={undefined} isLoading={true} />);
    expect(screen.getByText("Auditing organization structure data quality...")).toBeTruthy();
  });

  it("renders structure health score and severity counts", async () => {
    await render(<OrgQualityTab quality={mockQuality} isLoading={false} />);
    expect(screen.getByText("96.5%")).toBeTruthy();
    expect(screen.getByText("7")).toBeTruthy();
    expect(screen.getByText("94")).toBeTruthy();
    expect(screen.getByText("32")).toBeTruthy();
  });

  it("renders data quality rules with issue counts and impact", async () => {
    await render(<OrgQualityTab quality={mockQuality} isLoading={false} />);
    expect(screen.getByText("Active Employee Missing Official Record")).toBeTruthy();
    expect(screen.getByText("[MISSING_OFFICIAL_RECORD]")).toBeTruthy();
    expect(screen.getByText("Empty Active Locations (0 Staff)")).toBeTruthy();
    expect(screen.getByText("[EMPTY_LOCATIONS]")).toBeTruthy();
  });
});
