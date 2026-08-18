import { apiClient } from "./client";
import { triggerBrowserDownload } from "./modules.api";
import type {
  EmployeePayrollHistoryResponse,
  PayrollDataQualityResponse,
  PayrollMetadataResponse,
  PayrollOverviewResponse,
  PayrollQualityIssuesListResponse,
  PayrollRegisterListResponse,
} from "@/types/payroll.types";

export async function fetchPayrollMetadata(): Promise<PayrollMetadataResponse> {
  const { data } = await apiClient.get<PayrollMetadataResponse>("/modules/PAYROLL/metadata");
  return data;
}

export async function fetchPayrollOverview(compId?: number): Promise<PayrollOverviewResponse> {
  const params = new URLSearchParams();
  if (compId) params.append("comp_id", String(compId));
  const { data } = await apiClient.get<PayrollOverviewResponse>(
    `/modules/PAYROLL/overview?${params.toString()}`,
  );
  return data;
}


export async function fetchPayrollDirectory(
  statusFilter?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0,
  deptId?: number,
  compId?: number,
  month?: string,
  empId?: number,
): Promise<PayrollRegisterListResponse> {
  const params = new URLSearchParams();
  if (statusFilter) params.append("status", statusFilter);
  if (search) params.append("search", search);
  params.append("limit", String(limit));
  params.append("offset", String(offset));
  if (deptId) params.append("dept_id", String(deptId));
  if (compId) params.append("comp_id", String(compId));
  if (month) params.append("month", month);
  if (empId) params.append("emp_id", String(empId));

  const { data } = await apiClient.get<PayrollRegisterListResponse>(
    `/modules/PAYROLL/directory?${params.toString()}`,
  );
  return data;
}

export async function downloadPayrollDirectoryExport(
  statusFilter?: string,
  search?: string,
): Promise<void> {
  const params = new URLSearchParams();
  if (statusFilter) params.append("status", statusFilter);
  if (search) params.append("search", search);

  const response = await apiClient.get<Blob>("/modules/PAYROLL/directory/export", {
    params,
    responseType: "blob",
  });

  triggerBrowserDownload(
    response.data,
    "payroll_directory.csv",
    response.headers["content-disposition"],
  );
}

export async function fetchPayrollQuality(): Promise<PayrollDataQualityResponse> {
  const { data } = await apiClient.get<PayrollDataQualityResponse>("/modules/PAYROLL/quality");
  return data;
}

export async function fetchPayrollQualityIssues(
  issueCode?: string,
  limit: number = 20,
  offset: number = 0,
): Promise<PayrollQualityIssuesListResponse> {
  const params = new URLSearchParams();
  if (issueCode) params.append("issue", issueCode);
  params.append("limit", String(limit));
  params.append("offset", String(offset));

  const { data } = await apiClient.get<PayrollQualityIssuesListResponse>(
    `/modules/PAYROLL/quality/issues?${params.toString()}`,
  );
  return data;
}

export async function downloadPayrollQualityExport(issueCode: string): Promise<void> {
  const params = new URLSearchParams();
  params.append("issue", issueCode);

  const response = await apiClient.get<Blob>("/modules/PAYROLL/quality/export", {
    params,
    responseType: "blob",
  });

  triggerBrowserDownload(
    response.data,
    `payroll_issues_${issueCode.toLowerCase()}.csv`,
    response.headers["content-disposition"],
  );
}

export async function fetchEmployeePayrollHistory(
  empId: number,
): Promise<EmployeePayrollHistoryResponse> {
  const { data } = await apiClient.get<EmployeePayrollHistoryResponse>(
    `/modules/PAYROLL/employee/${empId}/history`,
  );
  return data;
}
