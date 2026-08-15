import { apiClient } from "@/api/client";
import type {
  AnalysisRunCreatedResponse,
  AnalysisRunDetail,
  AnalysisRunListResponse,
  AnalysisRunTableDetail,
  AnalysisRunTableListResponse,
  CreateAnalysisRunRequest,
  DatabaseAnalysisResponse,
  QuickAnalysisRequest,
} from "@/types/analysis.types";

export const analysisApi = {
  // POST /api/v1/analysis/quick
  runQuickAnalysis: async (
    payload?: QuickAnalysisRequest,
    signal?: AbortSignal
  ): Promise<DatabaseAnalysisResponse> => {
    const { data } = await apiClient.post<DatabaseAnalysisResponse>(
      "/analysis/quick",
      payload || {},
      {
        timeout: 10 * 60 * 1000, // 10 minutes timeout specifically configured for this synchronous run
        signal,
      }
    );
    return data;
  },

  // POST /api/v1/analysis-runs/
  createRun: async (
    payload?: CreateAnalysisRunRequest
  ): Promise<AnalysisRunCreatedResponse> => {
    const { data } = await apiClient.post<AnalysisRunCreatedResponse>(
      "/analysis-runs/",
      payload || {}
    );
    return data;
  },

  // GET /api/v1/analysis-runs/
  listRuns: async (params?: {
    limit?: number;
    offset?: number;
  }): Promise<AnalysisRunListResponse> => {
    const { data } = await apiClient.get<AnalysisRunListResponse>(
      "/analysis-runs/",
      { params }
    );
    return data;
  },

  // GET /api/v1/analysis-runs/{run_id}
  getRun: async (runId: string): Promise<AnalysisRunDetail> => {
    const { data } = await apiClient.get<AnalysisRunDetail>(
      `/analysis-runs/${encodeURIComponent(runId)}`
    );
    return data;
  },

  // GET /api/v1/analysis-runs/{run_id}/tables
  getRunTables: async (
    runId: string,
    params?: {
      schema?: string;
      status?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<AnalysisRunTableListResponse> => {
    const { data } = await apiClient.get<AnalysisRunTableListResponse>(
      `/analysis-runs/${encodeURIComponent(runId)}/tables`,
      { params }
    );
    return data;
  },

  // GET /api/v1/analysis-runs/{run_id}/tables/{schema}/{table}
  getRunTableDetail: async (
    runId: string,
    schema: string,
    table: string
  ): Promise<AnalysisRunTableDetail> => {
    const { data } = await apiClient.get<AnalysisRunTableDetail>(
      `/analysis-runs/${encodeURIComponent(runId)}/tables/${encodeURIComponent(
        schema
      )}/${encodeURIComponent(table)}`
    );
    return data;
  },

  // POST /api/v1/analysis-runs/{run_id}/cancel
  cancelRun: async (
    runId: string
  ): Promise<{ run_id: string; status: string; message: string }> => {
    const { data } = await apiClient.post(
      `/analysis-runs/${encodeURIComponent(runId)}/cancel`
    );
    return data;
  },
};
