import { apiClient } from "./client";
import { triggerBrowserDownload } from "./modules.api";
import type {
  SecurityDataQualityResponse,
  SecurityOverviewResponse,
  SecurityQualityIssuesListResponse,
  SecurityRoleDetailResponse,
  SecurityRoleListResponse,
  SecurityUserListResponse,
} from "@/types/security.types";

export async function fetchSecurityOverview(): Promise<SecurityOverviewResponse> {
  const response = await apiClient.get<SecurityOverviewResponse>("/modules/SECURITY/overview");
  return response.data;
}

export async function fetchSecurityUsers(
  roleId?: number,
  statusFilter?: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
): Promise<SecurityUserListResponse> {
  const queryParams = new URLSearchParams();
  if (roleId !== undefined) queryParams.set("role_id", roleId.toString());
  if (statusFilter) queryParams.set("status_filter", statusFilter);
  if (search) queryParams.set("search", search);
  queryParams.set("limit", limit.toString());
  queryParams.set("offset", offset.toString());

  const response = await apiClient.get<SecurityUserListResponse>(
    `/modules/SECURITY/users?${queryParams.toString()}`
  );
  return response.data;
}

export async function downloadSecurityUsersExport(
  roleId?: number,
  statusFilter?: string,
  search?: string
): Promise<void> {
  const queryParams = new URLSearchParams();
  if (roleId !== undefined) queryParams.set("role_id", roleId.toString());
  if (statusFilter) queryParams.set("status_filter", statusFilter);
  if (search) queryParams.set("search", search);

  const response = await apiClient.get(
    `/modules/SECURITY/users/export?${queryParams.toString()}`,
    {
      responseType: "blob",
    }
  );

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const defaultFilename = `user_security_directory_${statusFilter?.toLowerCase() || "all"}.csv`;

  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

export async function fetchSecurityRoles(): Promise<SecurityRoleListResponse> {
  const response = await apiClient.get<SecurityRoleListResponse>("/modules/SECURITY/roles");
  return response.data;
}

export async function fetchSecurityRolePermissions(roleId: number): Promise<SecurityRoleDetailResponse> {
  const response = await apiClient.get<SecurityRoleDetailResponse>(
    `/modules/SECURITY/roles/${roleId}/permissions`
  );
  return response.data;
}

export async function fetchSecurityQuality(): Promise<SecurityDataQualityResponse> {
  const response = await apiClient.get<SecurityDataQualityResponse>("/modules/SECURITY/quality");
  return response.data;
}

export async function fetchSecurityQualityIssues(
  issue: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
): Promise<SecurityQualityIssuesListResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set("issue", issue);
  if (search) queryParams.set("search", search);
  queryParams.set("limit", limit.toString());
  queryParams.set("offset", offset.toString());

  const response = await apiClient.get<SecurityQualityIssuesListResponse>(
    `/modules/SECURITY/quality/issues?${queryParams.toString()}`
  );
  return response.data;
}

export async function downloadSecurityQualityIssuesExport(
  issue: string,
  search?: string
): Promise<void> {
  const queryParams = new URLSearchParams();
  queryParams.set("issue", issue);
  if (search) queryParams.set("search", search);

  const response = await apiClient.get(
    `/modules/SECURITY/quality/export?${queryParams.toString()}`,
    {
      responseType: "blob",
    }
  );

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const defaultFilename = `security_issue_${issue.toLowerCase()}.csv`;

  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

export const securityApi = {
  getOverview: fetchSecurityOverview,
  getUsers: fetchSecurityUsers,
  exportUsers: downloadSecurityUsersExport,
  getRoles: fetchSecurityRoles,
  getRolePermissions: fetchSecurityRolePermissions,
  getQuality: fetchSecurityQuality,
  getQualityIssues: fetchSecurityQualityIssues,
  exportQualityIssues: downloadSecurityQualityIssuesExport,
};
