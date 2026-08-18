import { apiClient } from "./client";
import { triggerBrowserDownload } from "./modules.api";
import type {
  ContactDataQualityResponse,
  ContactDirectoryListResponse,
  ContactEmailFilter,
  ContactOverviewResponse,
  ContactPhoneFilter,
  ContactQualityIssuesListResponse,
} from "@/types/contact.types";

export async function fetchContactOverview(): Promise<ContactOverviewResponse> {
  const response = await apiClient.get<ContactOverviewResponse>("/modules/CONTACT/overview");
  return response.data;
}

export async function fetchContactDirectory(
  emailFilter?: ContactEmailFilter,
  phoneFilter?: ContactPhoneFilter,
  search?: string,
  limit: number = 25,
  offset: number = 0
): Promise<ContactDirectoryListResponse> {
  const queryParams = new URLSearchParams();
  if (emailFilter) queryParams.set("email_filter", emailFilter);
  if (phoneFilter) queryParams.set("phone_filter", phoneFilter);
  if (search) queryParams.set("search", search);
  queryParams.set("limit", limit.toString());
  queryParams.set("offset", offset.toString());

  const response = await apiClient.get<ContactDirectoryListResponse>(
    `/modules/CONTACT/directory?${queryParams.toString()}`
  );
  return response.data;
}

export async function fetchContactQuality(): Promise<ContactDataQualityResponse> {
  const response = await apiClient.get<ContactDataQualityResponse>("/modules/CONTACT/quality");
  return response.data;
}

export async function fetchContactQualityIssues(
  issue: string,
  search?: string,
  limit: number = 25,
  offset: number = 0
): Promise<ContactQualityIssuesListResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set("issue", issue);
  if (search) queryParams.set("search", search);
  queryParams.set("limit", limit.toString());
  queryParams.set("offset", offset.toString());

  const response = await apiClient.get<ContactQualityIssuesListResponse>(
    `/modules/CONTACT/quality/issues?${queryParams.toString()}`
  );
  return response.data;
}

export async function downloadContactDirectoryExport(
  emailFilter?: ContactEmailFilter,
  phoneFilter?: ContactPhoneFilter,
  search?: string,
  format: string = "csv"
): Promise<void> {
  const queryParams = new URLSearchParams();
  if (emailFilter) queryParams.set("email_filter", emailFilter);
  if (phoneFilter) queryParams.set("phone_filter", phoneFilter);
  if (search) queryParams.set("search", search);
  queryParams.set("format", format);

  const response = await apiClient.get(
    `/modules/CONTACT/directory/export?${queryParams.toString()}`,
    {
      responseType: "blob",
    }
  );

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const defaultFilename = `contact_directory_${emailFilter?.toLowerCase() || "all"}.${format}`;

  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

export async function downloadContactQualityIssuesExport(
  issue: string,
  search?: string,
  format: string = "csv"
): Promise<void> {
  const queryParams = new URLSearchParams();
  queryParams.set("issue", issue);
  if (search) queryParams.set("search", search);
  queryParams.set("format", format);

  const response = await apiClient.get(
    `/modules/CONTACT/quality/export?${queryParams.toString()}`,
    {
      responseType: "blob",
    }
  );

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const defaultFilename = `contact_quality_${issue.toLowerCase()}.${format}`;

  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

export const contactApi = {
  getOverview: fetchContactOverview,
  getDirectory: fetchContactDirectory,
  getQuality: fetchContactQuality,
  getQualityIssues: fetchContactQualityIssues,
  exportDirectory: downloadContactDirectoryExport,
  exportQualityIssues: downloadContactQualityIssuesExport,
};
