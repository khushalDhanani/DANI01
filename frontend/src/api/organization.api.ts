import { apiClient } from "./client";
import { triggerBrowserDownload } from "./modules.api";
import type {
  OrgDataQualityResponse,
  OrgHierarchyResponse,
  OrgOverviewResponse,
  OrgQualityIssuesListResponse,
  OrgReportingTreeResponse,
  OrgUnitListResponse,
  OrgUnitType,
} from "@/types/organization.types";

export async function fetchOrgOverview(): Promise<OrgOverviewResponse> {
  const response = await apiClient.get<OrgOverviewResponse>("/modules/ORGANIZATION/overview");
  return response.data;
}

export async function fetchOrgHierarchy(): Promise<OrgHierarchyResponse> {
  const response = await apiClient.get<OrgHierarchyResponse>("/modules/ORGANIZATION/hierarchy");
  return response.data;
}

export async function fetchOrgUnits(
  unitType?: OrgUnitType,
  search?: string,
  compId?: number,
  limit: number = 25,
  offset: number = 0
): Promise<OrgUnitListResponse> {
  const queryParams = new URLSearchParams();
  if (unitType) queryParams.set("unit_type", unitType);
  if (search) queryParams.set("search", search);
  if (compId !== undefined) queryParams.set("comp_id", compId.toString());
  queryParams.set("limit", limit.toString());
  queryParams.set("offset", offset.toString());

  const response = await apiClient.get<OrgUnitListResponse>(
    `/modules/ORGANIZATION/units?${queryParams.toString()}`
  );
  return response.data;
}

export async function fetchOrgReportingTree(): Promise<OrgReportingTreeResponse> {
  const response = await apiClient.get<OrgReportingTreeResponse>("/modules/ORGANIZATION/reporting");
  return response.data;
}

export async function fetchOrgQuality(): Promise<OrgDataQualityResponse> {
  const response = await apiClient.get<OrgDataQualityResponse>("/modules/ORGANIZATION/quality");
  return response.data;
}

export async function fetchOrgQualityIssues(
  issue: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
): Promise<OrgQualityIssuesListResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set("issue", issue);
  if (search) queryParams.set("search", search);
  queryParams.set("limit", limit.toString());
  queryParams.set("offset", offset.toString());

  const response = await apiClient.get<OrgQualityIssuesListResponse>(
    `/modules/ORGANIZATION/quality/issues?${queryParams.toString()}`
  );
  return response.data;
}

export async function downloadOrgUnitsExport(
  unitType?: OrgUnitType,
  search?: string,
  format: string = "csv"
): Promise<void> {
  const queryParams = new URLSearchParams();
  if (unitType) queryParams.set("unit_type", unitType);
  if (search) queryParams.set("search", search);
  queryParams.set("format", format);

  const response = await apiClient.get(
    `/modules/ORGANIZATION/units/export?${queryParams.toString()}`,
    {
      responseType: "blob",
    }
  );

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const defaultFilename = `organization_units_${unitType?.toLowerCase() || "all"}.${format}`;

  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

export async function downloadOrgQualityIssuesExport(
  issue: string,
  search?: string,
  format: string = "csv"
): Promise<void> {
  const queryParams = new URLSearchParams();
  queryParams.set("issue", issue);
  if (search) queryParams.set("search", search);
  queryParams.set("format", format);

  const response = await apiClient.get(
    `/modules/ORGANIZATION/quality/export?${queryParams.toString()}`,
    {
      responseType: "blob",
    }
  );

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const defaultFilename = `org_quality_issue_${issue.toLowerCase()}.${format}`;

  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

export const organizationApi = {
  getOverview: fetchOrgOverview,
  getHierarchy: fetchOrgHierarchy,
  getUnits: fetchOrgUnits,
  getReportingTree: fetchOrgReportingTree,
  getQuality: fetchOrgQuality,
  getQualityIssues: fetchOrgQualityIssues,
  exportUnits: downloadOrgUnitsExport,
  exportQualityIssues: downloadOrgQualityIssuesExport,
};
