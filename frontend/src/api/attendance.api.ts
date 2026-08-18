import { apiClient } from "./client";
import { triggerBrowserDownload } from "./modules.api";
import type {
  AttendanceDataQualityResponse,
  AttendanceDirectoryResponse,
  AttendanceOrgHierarchyResponse,
  AttendanceOverviewResponse,
  AttendanceQualityIssuesListResponse,
  DepartmentDetailResponse,
  EmployeeLifetimeAttendanceResponse,
  LeaveApplicationsListResponse,

  LeaveBalancesListResponse,
  LeaveOverviewResponse,
} from "../types/attendance.types";

export async function fetchAttendanceOverview(
  deptId?: number,
  compId?: number
): Promise<AttendanceOverviewResponse> {
  const params: Record<string, number> = {};
  if (deptId) params.dept_id = deptId;
  if (compId) params.comp_id = compId;

  if (Object.keys(params).length > 0) {
    const { data } = await apiClient.get<AttendanceOverviewResponse>(
      "/modules/ATTENDANCE/overview",
      { params }
    );
    return data;
  }
  const { data } = await apiClient.get<AttendanceOverviewResponse>(
    "/modules/ATTENDANCE/overview"
  );
  return data;
}

export async function fetchDepartmentDetail(
  deptId: number
): Promise<DepartmentDetailResponse> {
  const { data } = await apiClient.get<DepartmentDetailResponse>(
    `/modules/ATTENDANCE/department/${deptId}`
  );
  return data;
}

export async function fetchAttendanceOrgHierarchy(): Promise<AttendanceOrgHierarchyResponse> {
  const { data } = await apiClient.get<AttendanceOrgHierarchyResponse>(
    "/modules/ATTENDANCE/org-hierarchy"
  );

  return data;
}

export async function fetchAttendanceDirectory(
  statusFilter?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0,
  deptId?: number,
  compId?: number,
  empId?: number
): Promise<AttendanceDirectoryResponse> {
  const params: Record<string, string | number> = { limit, offset };
  if (statusFilter) params.status = statusFilter;
  if (search) params.search = search;
  if (deptId) params.dept_id = deptId;
  if (compId) params.comp_id = compId;
  if (empId) params.emp_id = empId;

  const { data } = await apiClient.get<AttendanceDirectoryResponse>(
    "/modules/ATTENDANCE/directory",
    { params }
  );
  return data;
}



export async function downloadAttendanceDirectoryExport(
  statusFilter?: string,
  search?: string
): Promise<void> {
  const params: Record<string, string> = {};
  if (statusFilter) params.status = statusFilter;
  if (search) params.search = search;

  const response = await apiClient.get<Blob>("/modules/ATTENDANCE/directory/export", {
    params,
    responseType: "blob",
  });

  triggerBrowserDownload(
    response.data,
    "attendance_directory.csv",
    response.headers["content-disposition"]
  );
}

export async function fetchLeaveOverview(): Promise<LeaveOverviewResponse> {
  const { data } = await apiClient.get<LeaveOverviewResponse>(
    "/modules/ATTENDANCE/leave/overview"
  );
  return data;
}

export async function fetchLeaveApplications(
  statusFilter?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0
): Promise<LeaveApplicationsListResponse> {
  const params: Record<string, string | number> = { limit, offset };
  if (statusFilter) params.status = statusFilter;
  if (search) params.search = search;

  const { data } = await apiClient.get<LeaveApplicationsListResponse>(
    "/modules/ATTENDANCE/leave/applications",
    { params }
  );
  return data;
}

export async function downloadLeaveApplicationsExport(
  statusFilter?: string,
  search?: string
): Promise<void> {
  const params: Record<string, string> = {};
  if (statusFilter) params.status = statusFilter;
  if (search) params.search = search;

  const response = await apiClient.get<Blob>("/modules/ATTENDANCE/leave/applications/export", {
    params,
    responseType: "blob",
  });

  triggerBrowserDownload(
    response.data,
    "leave_applications.csv",
    response.headers["content-disposition"]
  );
}

export async function fetchLeaveBalances(
  yearMonth?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0
): Promise<LeaveBalancesListResponse> {
  const params: Record<string, string | number> = { limit, offset };
  if (yearMonth) params.year_month = yearMonth;
  if (search) params.search = search;

  const { data } = await apiClient.get<LeaveBalancesListResponse>(
    "/modules/ATTENDANCE/leave/balances",
    { params }
  );
  return data;
}

export async function fetchAttendanceQuality(): Promise<AttendanceDataQualityResponse> {
  const { data } = await apiClient.get<AttendanceDataQualityResponse>(
    "/modules/ATTENDANCE/quality"
  );
  return data;
}

export async function fetchAttendanceQualityIssues(
  issueCode: string,
  search?: string,
  limit: number = 20,
  offset: number = 0
): Promise<AttendanceQualityIssuesListResponse> {
  const params: Record<string, string | number> = { issue: issueCode, limit, offset };
  if (search) params.search = search;

  const { data } = await apiClient.get<AttendanceQualityIssuesListResponse>(
    "/modules/ATTENDANCE/quality/issues",
    { params }
  );
  return data;
}

export async function downloadAttendanceQualityIssuesExport(
  issueCode: string,
  search?: string
): Promise<void> {
  const params: Record<string, string> = { issue: issueCode };
  if (search) params.search = search;

  const response = await apiClient.get<Blob>(
    "/modules/ATTENDANCE/quality/issues/export",
    {
      params,
      responseType: "blob",
    }
  );

  triggerBrowserDownload(
    response.data,
    `attendance_issue_${issueCode.toLowerCase()}.csv`,
    response.headers["content-disposition"]
  );
}

export async function fetchEmployeeLifetimeAnalytics(
  empId: number
): Promise<EmployeeLifetimeAttendanceResponse> {
  const { data } = await apiClient.get<EmployeeLifetimeAttendanceResponse>(
    `/modules/ATTENDANCE/employee/${empId}/analytics`
  );
  return data;
}


