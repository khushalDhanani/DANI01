import { useQuery } from "@tanstack/react-query";
import {
  fetchSecurityOverview,
  fetchSecurityQuality,
  fetchSecurityQualityIssues,
  fetchSecurityRolePermissions,
  fetchSecurityRoles,
  fetchSecurityUsers,
} from "@/api/security.api";
import { QUERY_KEYS } from "@/constants/config";
import type {
  SecurityDataQualityResponse,
  SecurityOverviewResponse,
  SecurityQualityIssuesListResponse,
  SecurityRoleDetailResponse,
  SecurityRoleListResponse,
  SecurityUserListResponse,
} from "@/types/security.types";

export function useSecurityOverview() {
  return useQuery<SecurityOverviewResponse>({
    queryKey: QUERY_KEYS.SECURITY.OVERVIEW,
    queryFn: () => fetchSecurityOverview(),
    staleTime: 30000,
  });
}

export function useSecurityUsers(
  roleId?: number,
  statusFilter?: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
) {
  return useQuery<SecurityUserListResponse>({
    queryKey: QUERY_KEYS.SECURITY.USERS(roleId, statusFilter, search, limit, offset),
    queryFn: () => fetchSecurityUsers(roleId, statusFilter, search, limit, offset),
  });
}

export function useSecurityRoles() {
  return useQuery<SecurityRoleListResponse>({
    queryKey: QUERY_KEYS.SECURITY.ROLES,
    queryFn: () => fetchSecurityRoles(),
    staleTime: 30000,
  });
}

export function useSecurityRolePermissions(roleId: number, enabled: boolean = true) {
  return useQuery<SecurityRoleDetailResponse>({
    queryKey: QUERY_KEYS.SECURITY.ROLE_PERMISSIONS(roleId),
    queryFn: () => fetchSecurityRolePermissions(roleId),
    enabled: enabled && roleId > 0,
  });
}

export function useSecurityQuality() {
  return useQuery<SecurityDataQualityResponse>({
    queryKey: QUERY_KEYS.SECURITY.QUALITY,
    queryFn: () => fetchSecurityQuality(),
    staleTime: 30000,
  });
}

export function useSecurityQualityIssues(
  issue: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
) {
  return useQuery<SecurityQualityIssuesListResponse>({
    queryKey: QUERY_KEYS.SECURITY.QUALITY_ISSUES(issue, search, limit, offset),
    queryFn: () => fetchSecurityQualityIssues(issue, search, limit, offset),
    enabled: Boolean(issue),
  });
}
