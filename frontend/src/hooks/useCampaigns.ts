import { useQuery } from "@tanstack/react-query";
import {
  fetchCampaignDetail,
  fetchCampaigns,
  fetchPRAuditLogs,
  fetchPRTransactions,
} from "@/api/campaign.api";
import type {
  PRAuditLogsQueryParams,
  PRTransactionsQueryParams,
} from "@/types/campaign.types";

export const campaignKeys = {
  all: ["campaigns"] as const,
  lists: () => [...campaignKeys.all, "list"] as const,
  detail: (id: number) => [...campaignKeys.all, "detail", id] as const,
  transactions: (params: PRTransactionsQueryParams) =>
    [...campaignKeys.all, "transactions", params] as const,
  auditLogs: (params: PRAuditLogsQueryParams) =>
    [...campaignKeys.all, "auditLogs", params] as const,
};

export function useCampaigns() {
  return useQuery({
    queryKey: campaignKeys.lists(),
    queryFn: fetchCampaigns,
  });
}

export function useCampaignDetail(campId: number | null | undefined) {
  return useQuery({
    queryKey: campaignKeys.detail(campId ?? 0),
    queryFn: () => fetchCampaignDetail(campId!),
    enabled: !!campId,
  });
}

export function usePRTransactions(params: PRTransactionsQueryParams = {}) {
  return useQuery({
    queryKey: campaignKeys.transactions(params),
    queryFn: () => fetchPRTransactions(params),
  });
}

export function useCampaignAuditLog(params: PRAuditLogsQueryParams = {}) {
  return useQuery({
    queryKey: campaignKeys.auditLogs(params),
    queryFn: () => fetchPRAuditLogs(params),
  });
}
