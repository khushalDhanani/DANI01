import { apiClient } from "./client";
import type {
  PRAuditLogsQueryParams,
  PRCampaignDetail,
  PRCampaignSummary,
  PRTransactionLogPageResponse,
  PRTransactionPageResponse,
  PRTransactionsQueryParams,
} from "@/types/campaign.types";

export async function fetchCampaigns(): Promise<PRCampaignSummary[]> {
  const response = await apiClient.get<PRCampaignSummary[]>("/campaigns");
  return response.data;
}

export async function fetchCampaignDetail(campId: number): Promise<PRCampaignDetail> {
  const response = await apiClient.get<PRCampaignDetail>(`/campaigns/${campId}`);
  return response.data;
}

export async function fetchPRTransactions(
  params: PRTransactionsQueryParams = {}
): Promise<PRTransactionPageResponse> {
  const queryParams = new URLSearchParams();
  if (params.camp_id !== undefined) queryParams.set("camp_id", params.camp_id.toString());
  if (params.review_status_id !== undefined)
    queryParams.set("review_status_id", params.review_status_id.toString());
  if (params.delivery_status_id !== undefined)
    queryParams.set("delivery_status_id", params.delivery_status_id.toString());
  if (params.search) queryParams.set("search", params.search);
  if (params.limit !== undefined) queryParams.set("limit", params.limit.toString());
  if (params.offset !== undefined) queryParams.set("offset", params.offset.toString());

  const queryStr = queryParams.toString();
  const response = await apiClient.get<PRTransactionPageResponse>(
    `/campaigns/transactions${queryStr ? `?${queryStr}` : ""}`
  );
  return response.data;
}

export async function fetchPRAuditLogs(
  params: PRAuditLogsQueryParams = {}
): Promise<PRTransactionLogPageResponse> {
  const queryParams = new URLSearchParams();
  if (params.camp_id !== undefined) queryParams.set("camp_id", params.camp_id.toString());
  if (params.limit !== undefined) queryParams.set("limit", params.limit.toString());
  if (params.offset !== undefined) queryParams.set("offset", params.offset.toString());

  const queryStr = queryParams.toString();
  const response = await apiClient.get<PRTransactionLogPageResponse>(
    `/campaigns/audit-log${queryStr ? `?${queryStr}` : ""}`
  );
  return response.data;
}

export const campaignApi = {
  getCampaigns: fetchCampaigns,
  getCampaignDetail: fetchCampaignDetail,
  getPRTransactions: fetchPRTransactions,
  getCampaignAuditLog: fetchPRAuditLogs,
};

