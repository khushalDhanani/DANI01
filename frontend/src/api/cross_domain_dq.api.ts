import { apiClient } from "./client";
import { triggerBrowserDownload } from "./modules.api";
import type {
  CrossDomainIssuesListResponse,
  CrossDomainOverviewResponse,
} from "@/types/cross_domain_dq.types";

export async function fetchCrossDomainOverview(compId?: number): Promise<CrossDomainOverviewResponse> {
  const params = new URLSearchParams();
  if (compId) params.append("comp_id", String(compId));
  const { data } = await apiClient.get<CrossDomainOverviewResponse>(
    `/modules/CROSS_DOMAIN_DQ/overview?${params.toString()}`,
  );
  return data;
}

export async function fetchCrossDomainIssues(
  ruleCode?: string,
  category?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0,
  compId?: number,
): Promise<CrossDomainIssuesListResponse> {
  const params = new URLSearchParams();
  if (ruleCode) params.append("rule_code", ruleCode);
  if (category) params.append("category", category);
  if (search) params.append("search", search);
  params.append("limit", String(limit));
  params.append("offset", String(offset));
  if (compId) params.append("comp_id", String(compId));

  const { data } = await apiClient.get<CrossDomainIssuesListResponse>(
    `/modules/CROSS_DOMAIN_DQ/issues?${params.toString()}`,
  );
  return data;
}

export async function downloadCrossDomainExport(
  ruleCode?: string,
  category?: string,
  search?: string,
  compId?: number,
): Promise<void> {
  const params = new URLSearchParams();
  if (ruleCode) params.append("rule_code", ruleCode);
  if (category) params.append("category", category);
  if (search) params.append("search", search);
  if (compId) params.append("comp_id", String(compId));

  const response = await apiClient.get<Blob>("/modules/CROSS_DOMAIN_DQ/export", {
    params,
    responseType: "blob",
  });

  const filename = `cross_domain_dq_${(ruleCode || category || "all").toLowerCase()}.csv`;
  triggerBrowserDownload(
    response.data,
    filename,
    response.headers["content-disposition"],
  );
}
