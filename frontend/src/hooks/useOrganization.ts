import { useQuery } from "@tanstack/react-query";
import {
  fetchOrgHierarchy,
  fetchOrgOverview,
  fetchOrgQuality,
  fetchOrgQualityIssues,
  fetchOrgReportingTree,
  fetchOrgUnits,
} from "@/api/organization.api";
import { QUERY_KEYS } from "@/constants/config";
import type {
  OrgDataQualityResponse,
  OrgHierarchyResponse,
  OrgOverviewResponse,
  OrgQualityIssuesListResponse,
  OrgReportingTreeResponse,
  OrgUnitListResponse,
  OrgUnitType,
} from "@/types/organization.types";

export function useOrgOverview() {
  return useQuery<OrgOverviewResponse>({
    queryKey: QUERY_KEYS.ORGANIZATION.OVERVIEW,
    queryFn: () => fetchOrgOverview(),
    staleTime: 30000,
  });
}

export function useOrgHierarchy() {
  return useQuery<OrgHierarchyResponse>({
    queryKey: QUERY_KEYS.ORGANIZATION.HIERARCHY,
    queryFn: () => fetchOrgHierarchy(),
    staleTime: 60000,
  });
}

export function useOrgUnits(
  unitType?: OrgUnitType,
  search?: string,
  compId?: number,
  limit: number = 25,
  offset: number = 0
) {
  return useQuery<OrgUnitListResponse>({
    queryKey: QUERY_KEYS.ORGANIZATION.UNITS(unitType, search, compId, limit, offset),
    queryFn: () => fetchOrgUnits(unitType, search, compId, limit, offset),
  });
}

export function useOrgReportingTree() {
  return useQuery<OrgReportingTreeResponse>({
    queryKey: QUERY_KEYS.ORGANIZATION.REPORTING,
    queryFn: () => fetchOrgReportingTree(),
    staleTime: 60000,
  });
}

export function useOrgQuality() {
  return useQuery<OrgDataQualityResponse>({
    queryKey: QUERY_KEYS.ORGANIZATION.QUALITY,
    queryFn: () => fetchOrgQuality(),
    staleTime: 30000,
  });
}

export function useOrgQualityIssues(
  issue: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
) {
  return useQuery<OrgQualityIssuesListResponse>({
    queryKey: QUERY_KEYS.ORGANIZATION.QUALITY_ISSUES(issue, search, limit, offset),
    queryFn: () => fetchOrgQualityIssues(issue, search, limit, offset),
    enabled: Boolean(issue),
  });
}
