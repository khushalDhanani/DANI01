import React from "react";
import { render, screen } from "@testing-library/react-native";
import { SecurityRolesTab } from "@/features/modules/security/SecurityRolesTab";
import { useSecurityRolePermissions, useSecurityRoles } from "@/hooks/useSecurity";
import type { SecurityRoleListResponse } from "@/types/security.types";

jest.mock("@/hooks/useSecurity", () => ({
  useSecurityRoles: jest.fn(),
  useSecurityRolePermissions: jest.fn(),
}));

const mockRolesData: SecurityRoleListResponse = {
  total_roles: 2,
  active_roles: 2,
  items: [
    {
      role_id: 1,
      role_desc: "All",
      comp_id: 1,
      is_active: true,
      is_deleted: false,
      total_assigned_users: 10,
      active_assigned_users: 6,
      assigned_menus_count: 651,
      insert_perms_count: 651,
      update_perms_count: 651,
      delete_perms_count: 651,
      view_perms_count: 651,
    },
    {
      role_id: 2,
      role_desc: "Employee",
      comp_id: 1,
      is_active: true,
      is_deleted: false,
      total_assigned_users: 2355,
      active_assigned_users: 1364,
      assigned_menus_count: 45,
      insert_perms_count: 10,
      update_perms_count: 10,
      delete_perms_count: 0,
      view_perms_count: 45,
    },
  ],
};

describe("SecurityRolesTab Component", () => {
  it("renders role cards and permission counts", async () => {
    (useSecurityRoles as jest.Mock).mockReturnValue({
      data: mockRolesData,
      isLoading: false,
      isError: false,
    });
    (useSecurityRolePermissions as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
    });

    await render(<SecurityRolesTab />);
    expect(screen.getByText("Role-Based Access Control (RBAC) Matrix")).toBeTruthy();
    expect(screen.getByText("All")).toBeTruthy();
    expect(screen.getByText("Employee")).toBeTruthy();
    expect(screen.getByText("6 active")).toBeTruthy();
    expect(screen.getByText("1364 active")).toBeTruthy();
  });
});
