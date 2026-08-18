import { useQuery } from "@tanstack/react-query";
import { fetchCrossDomainIssues, fetchCrossDomainOverview } from "@/api/cross_domain_dq.api";
import { QUERY_KEYS } from "@/constants/config";

export function useCrossDomainOverview(compId?: number) {
  return useQuery({
    queryKey: QUERY_KEYS.CROSS_DOMAIN_DQ.OVERVIEW(compId),
    queryFn: () => fetchCrossDomainOverview(compId),
  });
}

export function useCrossDomainIssues(
  ruleCode?: string,
  category?: string,
  search?: string,
  limit: number = 20,
  offset: number = 0,
  compId?: number,
) {
  return useQuery({
    queryKey: QUERY_KEYS.CROSS_DOMAIN_DQ.ISSUES(ruleCode, category, search, limit, offset, compId),
    queryFn: () => fetchCrossDomainIssues(ruleCode, category, search, limit, offset, compId),
  });
}
