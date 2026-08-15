import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { analysisApi } from "@/api/analysis.api";
import type {
  CreateAnalysisRunRequest,
  QuickAnalysisRequest,
} from "@/types/analysis.types";
import { API_CONFIG, QUERY_KEYS } from "@/constants/config";

export const useRunQuickAnalysis = () => {
  return useMutation({
    mutationFn: ({
      payload,
      signal,
    }: {
      payload?: QuickAnalysisRequest;
      signal?: AbortSignal;
    }) => analysisApi.runQuickAnalysis(payload, signal),
  });
};

export const useAnalysisRuns = (params?: { limit?: number; offset?: number }) => {
  return useQuery({
    queryKey: QUERY_KEYS.ANALYSIS.RUNS_LIST(params),
    queryFn: () => analysisApi.listRuns(params),
    staleTime: 10 * 1000,
  });
};

export const useAnalysisRun = (runId?: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.ANALYSIS.RUN_DETAIL(runId || ""),
    queryFn: () => (runId ? analysisApi.getRun(runId) : Promise.reject("No runId")),
    enabled: Boolean(runId),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return API_CONFIG.POLL_INTERVAL_MS;
      if (
        data.status === "QUEUED" ||
        data.status === "RUNNING" ||
        data.status === "CANCELLING"
      ) {
        return API_CONFIG.POLL_INTERVAL_MS;
      }
      return false;
    },
  });
};

export const useAnalysisRunTables = (
  runId?: string,
  params?: { schema?: string; status?: string; limit?: number; offset?: number }
) => {
  return useQuery({
    queryKey: QUERY_KEYS.ANALYSIS.RUN_TABLES(runId || "", params),
    queryFn: () =>
      runId
        ? analysisApi.getRunTables(runId, params)
        : Promise.reject("No runId"),
    enabled: Boolean(runId),
    staleTime: 5 * 1000,
  });
};

export const useAnalysisRunTableDetail = (
  runId?: string,
  schema?: string,
  table?: string
) => {
  return useQuery({
    queryKey: QUERY_KEYS.ANALYSIS.RUN_TABLE_DETAIL(
      runId || "",
      schema || "",
      table || ""
    ),
    queryFn: () =>
      runId && schema && table
        ? analysisApi.getRunTableDetail(runId, schema, table)
        : Promise.reject("Missing params"),
    enabled: Boolean(runId && schema && table),
  });
};

export const useCreateAnalysisRun = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload?: CreateAnalysisRunRequest) =>
      analysisApi.createRun(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["analysisRuns"] });
    },
  });
};

export const useCancelAnalysisRun = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (runId: string) => analysisApi.cancelRun(runId),
    onSuccess: (_, runId) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.ANALYSIS.RUN_DETAIL(runId),
      });
      queryClient.invalidateQueries({ queryKey: ["analysisRuns", "list"] });
    },
  });
};
