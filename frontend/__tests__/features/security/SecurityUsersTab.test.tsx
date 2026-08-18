import React from "react";
import { render, screen } from "@testing-library/react-native";
import { SecurityUsersTab } from "@/features/modules/security/SecurityUsersTab";
import { useSecurityUsers } from "@/hooks/useSecurity";
import type { SecurityUserListResponse } from "@/types/security.types";

jest.mock("@/hooks/useSecurity", () => ({
  useSecurityUsers: jest.fn(),
}));

const mockUsersData: SecurityUserListResponse = {
  total: 1,
  limit: 20,
  offset: 0,
  items: [
    {
      user_id: 1,
      username: "superadmin",
      user_email: "admin@aether.co.in",
      user_mobile: "9876543210",
      role_id: 1,
      role_desc: "All",
      emp_id: 100,
      emp_code: "1001",
      emp_name: "John Doe",
      emp_status: "ACTIVE",
      is_active: true,
      is_deleted: false,
      is_master_admin: true,
      is_mfa_enabled: true,
      is_mobile_app_user: true,
      last_access_api: "2026-08-17T10:00:00Z",
      created_at: "2025-01-01T00:00:00Z",
      registered_devices_count: 2,
    },
  ],
};

describe("SecurityUsersTab Component", () => {
  it("renders user directory rows and security badges", async () => {
    (useSecurityUsers as jest.Mock).mockReturnValue({
      data: mockUsersData,
      isLoading: false,
      isFetching: false,
    });

    await render(<SecurityUsersTab />);
    expect(screen.getByText("superadmin")).toBeTruthy();
    expect(screen.getByText("admin@aether.co.in")).toBeTruthy();
    expect(screen.getByText("All")).toBeTruthy();
    expect(screen.getByText("John Doe")).toBeTruthy();
    expect(screen.getByText("ADMIN")).toBeTruthy();
    expect(screen.getByText("Export Directory")).toBeTruthy();
  });
});
