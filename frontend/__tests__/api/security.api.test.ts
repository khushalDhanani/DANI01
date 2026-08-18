import { apiClient } from "@/api/client";
import {
  fetchSecurityOverview,
  fetchSecurityQuality,
  fetchSecurityQualityIssues,
  fetchSecurityRolePermissions,
  fetchSecurityRoles,
  fetchSecurityUsers,
} from "@/api/security.api";

jest.mock("@/api/client", () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

describe("Security API client", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("fetchSecurityOverview calls /modules/SECURITY/overview", async () => {
    const mockOverview = { account_metrics: { total_user_accounts: 5420 } };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockOverview });

    const result = await fetchSecurityOverview();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/SECURITY/overview");
    expect(result).toEqual(mockOverview);
  });

  it("fetchSecurityUsers passes parameters properly", async () => {
    const mockUsers = { total: 10, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockUsers });

    const result = await fetchSecurityUsers(1, "ACTIVE", "Admin", 25, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/SECURITY/users?role_id=1&status_filter=ACTIVE&search=Admin&limit=25&offset=0"
    );
    expect(result).toEqual(mockUsers);
  });

  it("fetchSecurityRoles calls /modules/SECURITY/roles", async () => {
    const mockRoles = { total_roles: 16, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockRoles });

    const result = await fetchSecurityRoles();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/SECURITY/roles");
    expect(result).toEqual(mockRoles);
  });

  it("fetchSecurityRolePermissions calls /modules/SECURITY/roles/{id}/permissions", async () => {
    const mockDetail = { role_id: 1, permissions: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockDetail });

    const result = await fetchSecurityRolePermissions(1);
    expect(apiClient.get).toHaveBeenCalledWith("/modules/SECURITY/roles/1/permissions");
    expect(result).toEqual(mockDetail);
  });

  it("fetchSecurityQuality calls /modules/SECURITY/quality", async () => {
    const mockQuality = { overall_security_score: 88.3, rules: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockQuality });

    const result = await fetchSecurityQuality();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/SECURITY/quality");
    expect(result).toEqual(mockQuality);
  });

  it("fetchSecurityQualityIssues calls /modules/SECURITY/quality/issues", async () => {
    const mockIssues = { issue_code: "ACTIVE_USER_INACTIVE_EMP", total: 125, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockIssues });

    const result = await fetchSecurityQualityIssues("ACTIVE_USER_INACTIVE_EMP", "John", 25, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/SECURITY/quality/issues?issue=ACTIVE_USER_INACTIVE_EMP&search=John&limit=25&offset=0"
    );
    expect(result).toEqual(mockIssues);
  });
});
