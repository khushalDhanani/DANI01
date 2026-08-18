import React from "react";
import { render, screen } from "@testing-library/react-native";
import { ContactEmailQualityTab } from "@/features/modules/contact/ContactEmailQualityTab";
import { ContactPhoneQualityTab } from "@/features/modules/contact/ContactPhoneQualityTab";
import { useContactQuality, useContactQualityIssues } from "@/hooks/useContact";
import type { ContactDataQualityResponse } from "@/types/contact.types";

jest.mock("@/hooks/useContact", () => ({
  useContactQuality: jest.fn(),
  useContactQualityIssues: jest.fn(),
}));

const mockQuality: ContactDataQualityResponse = {
  overall_health_score: 91.7,
  critical_issues_count: 17,
  warning_issues_count: 117,
  info_issues_count: 2673,
  rules: [
    {
      rule_code: "MISSING_ALL_PHONES",
      rule_name: "Active Employee Missing All Phone Numbers",
      severity: "CRITICAL",
      description: "Active employee with zero phone numbers recorded.",
      issue_count: 17,
      impact: "Zero emergency reachability.",
      recommendation: "Collect mobile number.",
    },
    {
      rule_code: "DUPLICATE_PERSONAL_EMAIL",
      rule_name: "Duplicate Personal Email",
      severity: "WARNING",
      description: "Personal email shared across active staff.",
      issue_count: 3,
      impact: "Shared login accounts.",
      recommendation: "Verify individual emails.",
    },
    {
      rule_code: "MISSING_ANY_EMAIL",
      rule_name: "Active Employee Without Any Email",
      severity: "INFO",
      description: "Active employee has no company or personal email.",
      issue_count: 251,
      impact: "Cannot receive electronic notices.",
      recommendation: "Optional collection.",
    },
  ],
  summary_by_severity: {
    CRITICAL: 17,
    WARNING: 117,
    INFO: 2673,
  },
  generated_at: "2026-08-17T12:00:00Z",
};

describe("Contact Quality Tabs", () => {
  beforeEach(() => {
    (useContactQuality as jest.Mock).mockReturnValue({
      data: mockQuality,
      isLoading: false,
      isError: false,
    });

    (useContactQualityIssues as jest.Mock).mockReturnValue({
      data: { total: 0, items: [] },
      isLoading: false,
      isError: false,
    });
  });

  it("renders ContactEmailQualityTab with health score and email rules", async () => {
    await render(<ContactEmailQualityTab />);
    expect(screen.getByText("91.7%")).toBeTruthy();
    expect(screen.getByText("Email Health & Formatting Audit")).toBeTruthy();
    expect(screen.getByText("Duplicate Personal Email")).toBeTruthy();
  });

  it("renders ContactPhoneQualityTab with phone and emergency rules", async () => {
    await render(<ContactPhoneQualityTab />);
    expect(screen.getByText("91.7%")).toBeTruthy();
    expect(screen.getByText("Phone, ICE & Address Quality Audit")).toBeTruthy();
    expect(screen.getByText("Active Employee Missing All Phone Numbers")).toBeTruthy();
  });
});
