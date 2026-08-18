import { Platform } from "react-native";
import { apiClient } from "./client";
import { formatDate } from "@/utils/formatters";
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
  PersonQualityResponse,
  PersonRecordDetailResponse,
  QualityRuleMeta,
} from "@/types/modules.types";

/**
 * Helper to download a Blob as a file in the browser environment.
 */
export function triggerBrowserDownload(
  blob: Blob,
  defaultFilename: string,
  contentDisposition?: string
) {
  let filename = defaultFilename;
  if (contentDisposition) {
    const match = contentDisposition.match(/filename=["']?([^"';]+)["']?/i);
    if (match && match[1]) {
      filename = match[1].trim();
    }
  }

  if (Platform.OS === "web" && typeof globalThis !== "undefined") {
    const doc = (globalThis as unknown as { document?: Document }).document;
    const win = (globalThis as unknown as { URL?: typeof URL }).URL;
    if (doc && win) {
      const url = win.createObjectURL(blob);
      const link = doc.createElement("a");
      link.href = url;
      link.download = filename;
      doc.body.appendChild(link);
      link.click();
      doc.body.removeChild(link);
      setTimeout(() => {
        win.revokeObjectURL(url);
      }, 1000);
    }
  }
}

/**
 * Fetches all registered business modules.
 */
export async function getModules(): Promise<ModuleInfo[]> {
  const response = await apiClient.get<ModuleInfo[]>("/modules");
  return response.data;
}

/**
 * Fetches detailed module definition including configured tables and relationships.
 */
export async function getModule(moduleCode: string): Promise<ModuleDefinition> {
  const response = await apiClient.get<ModuleDefinition>(
    `/modules/${encodeURIComponent(moduleCode)}`
  );
  return response.data;
}

/**
 * Validates module tables and columns against live database metadata.
 */
export async function validateModule(
  moduleCode: string
): Promise<ModuleValidationResult> {
  const response = await apiClient.get<ModuleValidationResult>(
    `/modules/${encodeURIComponent(moduleCode)}/validate`
  );
  return response.data;
}

/**
 * Fetches domain aggregate metrics for the PERSON module.
 */
export async function getPersonMetrics(): Promise<PersonModuleMetricsResponse> {
  const response = await apiClient.get<PersonModuleMetricsResponse>(
    "/modules/PERSON/metrics"
  );
  return response.data;
}

/**
 * Fetches paginated person records with search, status, and attribute presence filters.
 */
export async function getPersonList(
  params?: PersonListParams
): Promise<PersonListResponse> {
  const response = await apiClient.get<PersonListResponse>(
    "/modules/PERSON/records",
    { params }
  );
  return response.data;
}

/**
 * Fetches complete single person profile record including all child relations.
 */
export async function getPersonDetail(
  personId: number | null
): Promise<PersonRecordDetailResponse | null> {
  if (personId === null || personId === undefined) return null;
  const response = await apiClient.get<PersonRecordDetailResponse>(
    `/modules/PERSON/records/${personId}`
  );
  return response.data;
}

/**
 * Fetches PERSON Contact Quality KPI summary.
 */
export async function getContactQualitySummary(): Promise<ContactQualitySummary> {
  const response = await apiClient.get<ContactQualitySummary>(
    "/modules/PERSON/contact-quality"
  );
  return response.data;
}

/**
 * Fetches paginated PERSON contact quality issues drilldown.
 */
export async function getContactQualityIssues(
  params?: ContactQualityIssueParams
): Promise<ContactQualityIssuesResponse> {
  const response = await apiClient.get<ContactQualityIssuesResponse>(
    "/modules/PERSON/contact-quality/issues",
    { params }
  );
  return response.data;
}

/**
 * Exports all matching PERSON contact quality issues as CSV or Excel (.xlsx).
 */
export async function exportContactQualityIssues(
  params?: ContactQualityIssueParams & { format?: "xlsx" | "csv" }
): Promise<void> {
  const format = params?.format || "xlsx";
  const issue = params?.issue || "INVALID_EMAIL";
  const response = await apiClient.get("/modules/PERSON/contact-quality/export", {
    params,
    responseType: "blob",
  });

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const dateStr = formatDate(new Date());
  const defaultFilename = `daylite_${issue.toLowerCase()}_${dateStr}.${format}`;

  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

/**
 * Exports the 37-KPI quality summary report as CSV or Excel (.xlsx).
 */
export async function exportContactQualitySummary(
  format: "xlsx" | "csv" = "xlsx"
): Promise<void> {
  const response = await apiClient.get("/modules/PERSON/contact-quality/summary/export", {
    params: { format },
    responseType: "blob",
  });

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const dateStr = formatDate(new Date());
  const defaultFilename = `daylite_quality_summary_${dateStr}.${format}`;

  triggerBrowserDownload(response.data as Blob, defaultFilename, contentDisposition);
}

/**
 * Fetches declarations for all 37 Daylite quality rules from backend SSoT registry.
 */
export async function getContactQualityRules(): Promise<QualityRuleMeta[]> {
  const response = await apiClient.get<QualityRuleMeta[]>(
    "/modules/PERSON/contact-quality/rules"
  );
  return response.data;
}

/**
 * Runs PERSON data quality rule assessment and returns quality findings & scores.
 */
export async function getPersonQuality(): Promise<PersonQualityResponse> {
  const response = await apiClient.get<PersonQualityResponse>(
    "/modules/PERSON/quality"
  );
  return response.data;
}
