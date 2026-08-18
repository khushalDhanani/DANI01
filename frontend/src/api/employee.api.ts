import { apiClient } from "./client";
import type {
  EmployeeDetailResponse,
  EmployeeListResponse,
  EmployeeOverviewResponse,
  EmployeeRecordsFilterParams,
  EmployeeStructureResponse,
  QualityIssuesListResponse,
  EmployeeDataQualityResponse,
} from "@/types/employee.types";

export async function fetchEmployeeOverview(compId?: number): Promise<EmployeeOverviewResponse> {
  const params = new URLSearchParams();
  if (compId) params.append("comp_id", String(compId));
  const queryStr = params.toString();
  const response = await apiClient.get<EmployeeOverviewResponse>(
    `/modules/EMPLOYEE/overview${queryStr ? `?${queryStr}` : ""}`,
  );
  return response.data;
}



export async function fetchEmployeeStructure(): Promise<EmployeeStructureResponse> {
  const response = await apiClient.get<EmployeeStructureResponse>("/modules/EMPLOYEE/structure");
  return response.data;
}

export async function fetchEmployeeQuality(): Promise<EmployeeDataQualityResponse> {
  const response = await apiClient.get<EmployeeDataQualityResponse>("/modules/EMPLOYEE/quality");
  return response.data;
}

export async function fetchEmployeeQualityIssues(
  issue: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
): Promise<QualityIssuesListResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set("issue", issue);
  if (search) queryParams.set("search", search);
  queryParams.set("limit", limit.toString());
  queryParams.set("offset", offset.toString());

  const response = await apiClient.get<QualityIssuesListResponse>(
    `/modules/EMPLOYEE/quality/issues?${queryParams.toString()}`
  );
  return response.data;
}

export async function fetchEmployeeRecords(
  params: EmployeeRecordsFilterParams = {}
): Promise<EmployeeListResponse> {
  const queryParams = new URLSearchParams();
  if (params.search) queryParams.set("search", params.search);
  if (params.status) queryParams.set("status", params.status);
  if (params.dept_id !== undefined) queryParams.set("dept_id", params.dept_id.toString());
  if (params.desig_id !== undefined) queryParams.set("desig_id", params.desig_id.toString());
  if (params.loc_id !== undefined) queryParams.set("loc_id", params.loc_id.toString());
  if (params.compId !== undefined) queryParams.set("comp_id", params.compId.toString());

  if (params.limit !== undefined) queryParams.set("limit", params.limit.toString());
  if (params.offset !== undefined) queryParams.set("offset", params.offset.toString());
  if (params.sort_by) queryParams.set("sort_by", params.sort_by);
  if (params.sort_order) queryParams.set("sort_order", params.sort_order);

  const queryStr = queryParams.toString();
  const response = await apiClient.get<EmployeeListResponse>(
    `/modules/EMPLOYEE/records${queryStr ? `?${queryStr}` : ""}`
  );
  return response.data;
}

import { triggerBrowserDownload } from "./modules.api";

export async function fetchEmployeeDetail(empId: number): Promise<EmployeeDetailResponse> {
  const response = await apiClient.get<EmployeeDetailResponse>(`/modules/EMPLOYEE/records/${empId}`);
  return response.data;
}

export async function exportEmployeeRecords(params: {
  status?: string;
  search?: string;
  format?: string;
} = {}): Promise<void> {
  const status = params.status || "ACTIVE";
  const format = params.format || "csv";
  const response = await apiClient.get("/modules/EMPLOYEE/records/export", {
    params: { status, search: params.search, format },
    responseType: "blob",
  });

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const defaultFilename = `employees_${status.toLowerCase()}.${format}`;
  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

export async function exportEmployeeQualityIssues(params: {
  issue: string;
  search?: string;
  format?: string;
}): Promise<void> {
  const format = params.format || "csv";
  const response = await apiClient.get("/modules/EMPLOYEE/quality/export", {
    params: { issue: params.issue, search: params.search, format },
    responseType: "blob",
  });

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const defaultFilename = `quality_issue_${params.issue.toLowerCase()}.${format}`;
  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

export const employeeApi = {
  getOverview: fetchEmployeeOverview,
  getStructure: fetchEmployeeStructure,
  getQuality: fetchEmployeeQuality,
  getQualityIssues: fetchEmployeeQualityIssues,
  getRecords: fetchEmployeeRecords,
  getDetail: fetchEmployeeDetail,
  exportRecords: exportEmployeeRecords,
  exportQualityIssues: exportEmployeeQualityIssues,
};
