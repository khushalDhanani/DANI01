import { useQuery } from "@tanstack/react-query";
import {
  fetchEmployeePayrollHistory,
  fetchPayrollDirectory,
  fetchPayrollMetadata,
  fetchPayrollOverview,
  fetchPayrollQuality,
  fetchPayrollQualityIssues,
} from "@/api/payroll.api";
import { QUERY_KEYS } from "@/constants/config";

export function usePayrollMetadata() {
  return useQuery({
    queryKey: ["payroll", "metadata"],
    queryFn: fetchPayrollMetadata,
  });
}

export function usePayrollOverview(compId?: number) {
  return useQuery({
    queryKey: QUERY_KEYS.PAYROLL.OVERVIEW(compId),
    queryFn: () => fetchPayrollOverview(compId),
  });
}


export function usePayrollDirectory(
  statusFilter?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0,
  deptId?: number,
  compId?: number,
  month?: string,
  empId?: number,
) {
  return useQuery({
    queryKey: QUERY_KEYS.PAYROLL.DIRECTORY(
      statusFilter,
      search,
      limit,
      offset,
      deptId,
      compId,
      month,
      empId,
    ),
    queryFn: () =>
      fetchPayrollDirectory(statusFilter, search, limit, offset, deptId, compId, month, empId),
  });
}

export function usePayrollQuality() {
  return useQuery({
    queryKey: QUERY_KEYS.PAYROLL.QUALITY,
    queryFn: fetchPayrollQuality,
  });
}

export function usePayrollQualityIssues(
  issueCode?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0,
) {
  return useQuery({
    queryKey: QUERY_KEYS.PAYROLL.QUALITY_ISSUES(issueCode || "", search, limit, offset),
    queryFn: () => fetchPayrollQualityIssues(issueCode, limit, offset),
  });
}

export function useEmployeePayrollHistory(empId?: number) {
  return useQuery({
    queryKey: QUERY_KEYS.PAYROLL.EMPLOYEE_HISTORY(empId!),
    queryFn: () => fetchEmployeePayrollHistory(empId!),
    enabled: !!empId,
  });
}
