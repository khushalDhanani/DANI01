import { useQuery } from "@tanstack/react-query";
import {
  fetchAttendanceDirectory,
  fetchAttendanceOrgHierarchy,
  fetchAttendanceOverview,
  fetchAttendanceQuality,
  fetchAttendanceQualityIssues,
  fetchDepartmentDetail,
  fetchEmployeeLifetimeAnalytics,
  fetchLeaveApplications,

  fetchLeaveBalances,
  fetchLeaveOverview,
} from "../api/attendance.api";
import { QUERY_KEYS } from "../constants/config";

export function useAttendanceOverview(deptId?: number, compId?: number) {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.OVERVIEW(deptId, compId),
    queryFn: () => fetchAttendanceOverview(deptId, compId),
  });
}

export function useAttendanceOrgHierarchy() {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.ORG_HIERARCHY,
    queryFn: fetchAttendanceOrgHierarchy,
  });
}

export function useDepartmentDetail(deptId?: number) {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.DEPARTMENT_DETAIL(deptId!),
    queryFn: () => fetchDepartmentDetail(deptId!),
    enabled: Boolean(deptId),
  });
}


export function useAttendanceDirectory(
  statusFilter?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0,
  deptId?: number,
  compId?: number,
  empId?: number
) {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.DIRECTORY(statusFilter, search, limit, offset, deptId, compId, empId),
    queryFn: () => fetchAttendanceDirectory(statusFilter, search, limit, offset, deptId, compId, empId),
  });
}



export function useLeaveOverview() {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.LEAVE_OVERVIEW,
    queryFn: fetchLeaveOverview,
  });
}

export function useLeaveApplications(
  statusFilter?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0
) {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.LEAVE_APPLICATIONS(statusFilter, search, limit, offset),
    queryFn: () => fetchLeaveApplications(statusFilter, search, limit, offset),
  });
}

export function useLeaveBalances(
  yearMonth?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0
) {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.LEAVE_BALANCES(yearMonth, search, limit, offset),
    queryFn: () => fetchLeaveBalances(yearMonth, search, limit, offset),
  });
}

export function useAttendanceQuality() {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.QUALITY,
    queryFn: fetchAttendanceQuality,
  });
}

export function useAttendanceQualityIssues(
  issueCode?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0
) {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.QUALITY_ISSUES(issueCode || "", search, limit, offset),
    queryFn: () => fetchAttendanceQualityIssues(issueCode!, search, limit, offset),
    enabled: Boolean(issueCode),
  });
}

export function useEmployeeLifetimeAnalytics(empId?: number) {
  return useQuery({
    queryKey: QUERY_KEYS.ATTENDANCE.EMPLOYEE_LIFETIME_ANALYTICS(empId || 0),
    queryFn: () => fetchEmployeeLifetimeAnalytics(empId!),
    enabled: Boolean(empId),
  });
}

