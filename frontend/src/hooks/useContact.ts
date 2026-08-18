import { useQuery } from "@tanstack/react-query";
import {
  fetchContactDirectory,
  fetchContactOverview,
  fetchContactQuality,
  fetchContactQualityIssues,
} from "@/api/contact.api";
import { QUERY_KEYS } from "@/constants/config";
import type {
  ContactDataQualityResponse,
  ContactDirectoryListResponse,
  ContactEmailFilter,
  ContactOverviewResponse,
  ContactPhoneFilter,
  ContactQualityIssuesListResponse,
} from "@/types/contact.types";

export function useContactOverview() {
  return useQuery<ContactOverviewResponse>({
    queryKey: QUERY_KEYS.CONTACT.OVERVIEW,
    queryFn: () => fetchContactOverview(),
    staleTime: 30000,
  });
}

export function useContactDirectory(
  emailFilter?: ContactEmailFilter,
  phoneFilter?: ContactPhoneFilter,
  search?: string,
  limit: number = 25,
  offset: number = 0
) {
  return useQuery<ContactDirectoryListResponse>({
    queryKey: QUERY_KEYS.CONTACT.DIRECTORY(emailFilter, phoneFilter, search, limit, offset),
    queryFn: () => fetchContactDirectory(emailFilter, phoneFilter, search, limit, offset),
  });
}

export function useContactQuality() {
  return useQuery<ContactDataQualityResponse>({
    queryKey: QUERY_KEYS.CONTACT.QUALITY,
    queryFn: () => fetchContactQuality(),
    staleTime: 30000,
  });
}

export function useContactQualityIssues(
  issue: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
) {
  return useQuery<ContactQualityIssuesListResponse>({
    queryKey: QUERY_KEYS.CONTACT.QUALITY_ISSUES(issue, search, limit, offset),
    queryFn: () => fetchContactQualityIssues(issue, search, limit, offset),
    enabled: Boolean(issue),
  });
}
