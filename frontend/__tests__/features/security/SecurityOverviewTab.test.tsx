import React from "react";
import { render, screen } from "@testing-library/react-native";
import { SecurityOverviewTab } from "@/features/modules/security/SecurityOverviewTab";
import { useSecurityOverview } from "@/hooks/useSecurity";
import type { SecurityOverviewResponse } from "@/types/security.types";

jest.mock("@/hooks/useSecurity", () => ({
  useSecurityOverview: jest.fn(),
}));

const mockOverview: SecurityOverviewResponse = {
  account_metrics: {
    total_user_accounts: 5420,
    active_users: 4214,
    active_users_pct: 77.7,
    inactive_users: 785,
    inactive_users_pct: 14.5,
    deleted_users: 421,
    deleted_users_pct: 7.8,
    linked_to_employee: 2459,
    linked_to_employee_pct: 45.4,
    unlinked_users: 2961,
    unlinked_users_pct: 54.6,
  },
  employee_link_metrics: {
    total_active_employees: 1316,
    active_emps_with_active_user: 1284,
    active_emps_with_active_user_pct: 97.6,
    active_emps_without_active_user: 32,
    active_emps_without_active_user_pct: 2.4,
  },
  posture_metrics: {
    master_admins_count: 52,
    mfa_enabled_count: 13,
    mfa_enabled_pct: 0.3,
    mobile_app_users_count: 1554,
    sma_users_count: 219,
    api_accessed_count: 2333,
    never_logged_in_count: 3087,
    total_registered_devices: 2038,
  },
  role_distribution: [
    { role_id: 13, role_desc: "Candidate", total_users: 2600, active_users: 2571, percentage: 61.0 },
    { role_id: 2, role_desc: "Employee", total_users: 2355, active_users: 1364, percentage: 32.4 },
  ],
  generated_at: "2026-08-17T12:00:00Z",
};

describe("SecurityOverviewTab Component", () => {
  it("renders loading indicator when hook is loading", async () => {
    (useSecurityOverview as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    });

    await render(<SecurityOverviewTab />);
    expect(screen.getByText("Loading user & security intelligence...")).toBeTruthy();
  });

  it("renders security overview cards and role distribution", async () => {
    (useSecurityOverview as jest.Mock).mockReturnValue({
      data: mockOverview,
      isLoading: false,
      isError: false,
    });

    await render(<SecurityOverviewTab />);
    expect(screen.getByText("User & Security Access Intelligence")).toBeTruthy();
    expect(screen.getByText("4,214")).toBeTruthy();
    expect(screen.getByText("785")).toBeTruthy();
    expect(screen.getByText("421")).toBeTruthy();
    expect(screen.getByText("52")).toBeTruthy();
    expect(screen.getByText("1,284")).toBeTruthy();
    expect(screen.getByText("Candidate")).toBeTruthy();
    expect(screen.getByText("Employee")).toBeTruthy();
  });
});
