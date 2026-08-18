import React from "react";
import { render, screen } from "@testing-library/react-native";
import { SecurityQualityTab } from "@/features/modules/security/SecurityQualityTab";
import { useSecurityQuality, useSecurityQualityIssues } from "@/hooks/useSecurity";
import type { SecurityDataQualityResponse } from "@/types/security.types";

jest.mock("@/hooks/useSecurity", () => ({
  useSecurityQuality: jest.fn(),
  useSecurityQualityIssues: jest.fn(),
}));

const mockQualityData: SecurityDataQualityResponse = {
  overall_security_score: 88.3,
  critical_issues_count: 145,
  warning_issues_count: 116,
  info_issues_count: 6125,
  rules: [
    {
      rule_code: "ACTIVE_USER_INACTIVE_EMP",
      rule_name: "Active User Account Linked to Inactive/Resigned Employee",
      severity: "CRITICAL",
      description: "User account remains active while the linked Employee is marked Inactive.",
      issue_count: 125,
      impact: "Departed staff retain login access.",
      recommendation: "Immediately deactivate account.",
    },
  ],
  summary_by_severity: { CRITICAL: 145, WARNING: 116, INFO: 6125 },
  generated_at: "2026-08-17T12:00:00Z",
};

describe("SecurityQualityTab Component", () => {
  it("renders health score and rule cards", async () => {
    (useSecurityQuality as jest.Mock).mockReturnValue({
      data: mockQualityData,
      isLoading: false,
      isError: false,
    });
    (useSecurityQualityIssues as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      isFetching: false,
    });

    await render(<SecurityQualityTab />);
    expect(screen.getByText("Security & Access Health Score")).toBeTruthy();
    expect(screen.getByText("88.3%")).toBeTruthy();
    expect(screen.getByText("Active User Account Linked to Inactive/Resigned Employee")).toBeTruthy();
    expect(screen.getByText("ACTIVE_USER_INACTIVE_EMP")).toBeTruthy();
    expect(screen.getByText("125 issues")).toBeTruthy();
  });
});
