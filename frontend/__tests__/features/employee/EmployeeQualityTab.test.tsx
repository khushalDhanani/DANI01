import React from "react";
import { render, screen } from "@testing-library/react-native";
import { EmployeeQualityTab } from "@/features/modules/employee/EmployeeQualityTab";
import type { EmployeeDataQualityResponse } from "@/types/employee.types";

jest.mock("@/hooks/useEmployee", () => ({
  useEmployeeQualityIssues: jest.fn().mockReturnValue({
    data: { items: [], total: 0 },
    isLoading: false,
  }),
}));

const mockQuality: EmployeeDataQualityResponse = {
  overall_health_score: 88.5,
  critical_issues_count: 29,
  warning_issues_count: 486,
  info_issues_count: 121,
  rules: [
    {
      rule_code: "DUP_EMP_CODE",
      rule_name: "Duplicate Employee Code",
      severity: "CRITICAL",
      description: "Multiple records share identical badge code",
      issue_count: 20,
      impact: "High risk of record confusion",
      recommendation: "Re-index employee codes",
    },
    {
      rule_code: "MISSING_EMAIL",
      rule_name: "Missing Corporate Email",
      severity: "WARNING",
      description: "Active employees without corporate email",
      issue_count: 12,
      impact: "Cannot receive company notifications",
      recommendation: "Provision email address",
    },
  ],
  summary_by_severity: { CRITICAL: 29, WARNING: 486, INFO: 121 },
  generated_at: "2026-08-17T12:00:00Z",
};

describe("EmployeeQualityTab Feature Component", () => {
  it("renders loading state when isLoading is true", async () => {
    await render(<EmployeeQualityTab quality={undefined} isLoading={true} />);
    expect(screen.getByText("Auditing employee data quality...")).toBeTruthy();
  });

  it("renders quality score and issue severity counts", async () => {
    await render(<EmployeeQualityTab quality={mockQuality} isLoading={false} />);
    expect(screen.getByText("88.5%")).toBeTruthy();
    expect(screen.getByText("29")).toBeTruthy();
    expect(screen.getByText("486")).toBeTruthy();
    expect(screen.getByText("121")).toBeTruthy();
  });

  it("renders data quality rules with issue counts and impact", async () => {
    await render(<EmployeeQualityTab quality={mockQuality} isLoading={false} />);
    expect(screen.getByText("Duplicate Employee Code")).toBeTruthy();
    expect(screen.getByText("DUP_EMP_CODE")).toBeTruthy();
    expect(screen.getByText("20")).toBeTruthy();
    expect(screen.getByText("Missing Corporate Email")).toBeTruthy();
    expect(screen.getByText("MISSING_EMAIL")).toBeTruthy();
    expect(screen.getByText("12")).toBeTruthy();
  });
});
