import { useQuery } from "@tanstack/react-query";
import { employeeApi } from "@/api/employee.api";
import { QUERY_KEYS } from "@/constants/config";
import type {
  EmployeeDetailResponse,
  EmployeeListResponse,
  EmployeeOverviewResponse,
  EmployeeRecordsFilterParams,
  EmployeeStructureResponse,
  QualityIssuesListResponse,
  EmployeeDataQualityResponse,
} from "@/types/employee.types";

export function useEmployeeOverview(compId?: number) {
  return useQuery<EmployeeOverviewResponse>({
    queryKey: QUERY_KEYS.EMPLOYEE.OVERVIEW(compId),
    queryFn: () => employeeApi.getOverview(compId),
    staleTime: 30000,
  });
}


export function useEmployeeStructure() {
  return useQuery<EmployeeStructureResponse>({
    queryKey: QUERY_KEYS.EMPLOYEE.STRUCTURE,
    queryFn: () => employeeApi.getStructure(),
    staleTime: 60000,
  });
}

export function useEmployeeQuality() {
  return useQuery<EmployeeDataQualityResponse>({
    queryKey: QUERY_KEYS.EMPLOYEE.QUALITY,
    queryFn: () => employeeApi.getQuality(),
    staleTime: 30000,
  });
}

export function useEmployeeQualityIssues(
  issue: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
) {
  return useQuery<QualityIssuesListResponse>({
    queryKey: QUERY_KEYS.EMPLOYEE.QUALITY_ISSUES(issue, search, limit, offset),
    queryFn: () => employeeApi.getQualityIssues(issue, search, limit, offset),
    enabled: Boolean(issue),
  });
}

export function useEmployeeRecords(params: EmployeeRecordsFilterParams = {}) {
  return useQuery<EmployeeListResponse>({
    queryKey: QUERY_KEYS.EMPLOYEE.RECORDS(params),
    queryFn: () => employeeApi.getRecords(params),
  });
}

export function useEmployeeRecordDetail(empId: number | null) {
  return useQuery<EmployeeDetailResponse>({
    queryKey: QUERY_KEYS.EMPLOYEE.DETAIL(empId ?? 0),
    queryFn: () => employeeApi.getDetail(empId!),
    enabled: Boolean(empId && empId > 0),
  });
}
