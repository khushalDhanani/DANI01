import { apiClient } from "@/api/client";
import type {
  DatabaseSummary,
  SchemaInfo,
  SchemaListResponse,
  TableListResponse,
} from "@/types/database.types";

export const databaseApi = {
  // GET /api/v1/database/summary
  getSummary: async (): Promise<DatabaseSummary> => {
    const { data } = await apiClient.get<DatabaseSummary>("/database/summary");
    return data;
  },

  // GET /api/v1/database/schemas
  getSchemas: async (): Promise<SchemaInfo[]> => {
    const { data } = await apiClient.get<SchemaListResponse>("/database/schemas");
    return data.items;
  },

  // GET /api/v1/database/tables
  getTables: async (params?: {
    schema?: string;
    search?: string;
    limit?: number;
    offset?: number;
    sort_by?: "schema" | "table" | "estimated_rows" | "column_count";
    sort_order?: "asc" | "desc";
  }): Promise<TableListResponse> => {
    const { data } = await apiClient.get<TableListResponse>("/database/tables", {
      params,
    });
    return data;
  },
};
