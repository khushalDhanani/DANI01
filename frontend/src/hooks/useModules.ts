import { useQuery } from "@tanstack/react-query";
import {
  getContactQualityIssues,
  getContactQualitySummary,
  getModule,
  getModules,
  getPersonDetail,
  getPersonList,
  getPersonMetrics,
  validateModule,
} from "@/api/modules.api";
import type {
  ContactQualityIssueParams,
  ContactQualityIssuesResponse,
  ContactQualitySummary,
  ModuleDefinition,
  ModuleInfo,
  ModuleValidationResult,
  PersonListParams,
  PersonListResponse,
  PersonModuleMetricsResponse,
  PersonRecordDetailResponse,
} from "@/types/modules.types";

/**
 * Hook to fetch all registered business modules.
 */
export function useModulesList() {
  return useQuery<ModuleInfo[], Error>({
    queryKey: ["modules"],
    queryFn: getModules,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch definition of a specific business module.
 */
export function useModuleDefinition(moduleCode?: string) {
  return useQuery<ModuleDefinition, Error>({
    queryKey: ["module", moduleCode],
    queryFn: () => getModule(moduleCode!),
    enabled: Boolean(moduleCode),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook to fetch live database metadata validation for a module.
 */
export function useModuleValidation(moduleCode?: string) {
  return useQuery<ModuleValidationResult, Error>({
    queryKey: ["module", moduleCode, "validate"],
    queryFn: () => validateModule(moduleCode!),
    enabled: Boolean(moduleCode),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Hook to fetch domain aggregate metrics for the PERSON module.
 */
export function usePersonMetrics() {
  return useQuery<PersonModuleMetricsResponse, Error>({
    queryKey: ["module", "PERSON", "metrics"],
    queryFn: getPersonMetrics,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook to fetch paginated Person records with search & filters.
 */
export function usePersonList(params?: PersonListParams) {
  return useQuery<PersonListResponse, Error>({
    queryKey: ["module", "PERSON", "records", params],
    queryFn: () => getPersonList(params),
    staleTime: 1000 * 30, // 30 seconds
  });
}

/**
 * Hook to fetch single Person detail record.
 */
export function usePersonDetail(personId?: number | null) {
  return useQuery<PersonRecordDetailResponse | null, Error>({
    queryKey: ["module", "PERSON", "record", personId],
    queryFn: () => getPersonDetail(personId ?? null),
    enabled: Boolean(personId),
    staleTime: 1000 * 60 * 2,
  });
}

/**
 * Hook to fetch PERSON Contact Quality KPI summary.
 */
export function useContactQualitySummary() {
  return useQuery<ContactQualitySummary, Error>({
    queryKey: ["module", "PERSON", "contact-quality-summary"],
    queryFn: getContactQualitySummary,
    staleTime: 1000 * 60 * 2,
  });
}

/**
 * Hook to fetch paginated PERSON contact quality issues drilldown.
 */
export function useContactQualityIssues(params?: ContactQualityIssueParams) {
  return useQuery<ContactQualityIssuesResponse, Error>({
    queryKey: ["module", "PERSON", "contact-quality-issues", params],
    queryFn: () => getContactQualityIssues(params),
    staleTime: 1000 * 30,
  });
}
