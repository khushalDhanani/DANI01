import React from "react";
import { render, screen } from "@testing-library/react-native";
import { EmployeeOverviewTab } from "@/features/modules/employee/EmployeeOverviewTab";
import type { EmployeeOverviewResponse } from "@/types/employee.types";

const mockOverview: EmployeeOverviewResponse = {
  status_counts: {
    total: 3091,
    active: 1316,
    inactive: 116,
    resigned: 1555,
    deleted: 104,
  },
  gender_distribution: [
    { label: "Male", count: 1000, percentage: 76.0 },
    { label: "Female", count: 316, percentage: 24.0 },
  ],
  employment_type_distribution: [
    { label: "Permanent", count: 1300, percentage: 98.8 },
    { label: "Contract", count: 16, percentage: 1.2 },
  ],
  department_distribution: [
    { label: "Procurement Team", count: 400, percentage: 30.4 },
    { label: "Production Team", count: 300, percentage: 22.8 },
  ],
  company_distribution: [
    { label: "Aether Industries Limited", count: 1316, percentage: 100.0 },
  ],
  top_locations: [
    { label: "Site 1", count: 800, percentage: 60.8 },
  ],
  user_account_coverage: {
    active_employees_with_login: 1200,
    login_coverage_pct: 91.2,
    total_active_logins: 4214,
  },
  reporting_coverage: {
    active_employees_with_manager: 1222,
    manager_coverage_pct: 92.8,
  },
  generated_at: "2026-08-17T12:00:00Z",
};

describe("EmployeeOverviewTab Feature Component", () => {
  it("renders loading indicator when isLoading is true", async () => {
    await render(<EmployeeOverviewTab overview={undefined} isLoading={true} />);
    expect(screen.getByText("Loading workforce metrics...")).toBeTruthy();
  });

  it("renders authoritative headcount numbers correctly", async () => {
    await render(<EmployeeOverviewTab overview={mockOverview} isLoading={false} />);
    expect(screen.getByText("3,091")).toBeTruthy();
    expect(screen.getByText("1,316")).toBeTruthy();
    expect(screen.getByText("116")).toBeTruthy();
    expect(screen.getByText("1,555")).toBeTruthy();
    expect(screen.getByText("104")).toBeTruthy();
  });

  it("renders coverage percentages for users and managers", async () => {
    await render(<EmployeeOverviewTab overview={mockOverview} isLoading={false} />);
    expect(screen.getByText("91.2%")).toBeTruthy();
    expect(screen.getByText("92.8%")).toBeTruthy();
  });

  it("renders top departments", async () => {
    await render(<EmployeeOverviewTab overview={mockOverview} isLoading={false} />);
    expect(screen.getByText("Procurement Team")).toBeTruthy();
    expect(screen.getByText("Production Team")).toBeTruthy();
  });
});
