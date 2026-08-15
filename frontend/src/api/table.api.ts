import { apiClient } from "@/api/client";
import type {
  ColumnInfo,
  ColumnListResponse,
  TableIndexesResponse,
  TableInfo,
  TableKeysResponse,
  TableSampleResponse,
  TableStructureResponse,
} from "@/types/database.types";
import type { TableProfileResponse } from "@/types/profiling.types";
import type { TableClassificationResponse } from "@/types/classification.types";

export const tableApi = {
  // GET /api/v1/database/tables/{schema}/{table}
  getTableSummary: async (
    schema: string,
    tableName: string
  ): Promise<TableInfo> => {
    const { data } = await apiClient.get<TableInfo>(
      `/database/tables/${encodeURIComponent(schema)}/${encodeURIComponent(
        tableName
      )}`
    );
    return data;
  },

  // GET /api/v1/database/tables/{schema}/{table}/columns
  getColumns: async (
    schema: string,
    tableName: string
  ): Promise<ColumnInfo[]> => {
    const { data } = await apiClient.get<ColumnListResponse>(
      `/database/tables/${encodeURIComponent(schema)}/${encodeURIComponent(
        tableName
      )}/columns`
    );
    return data.columns;
  },

  // GET /api/v1/database/tables/{schema}/{table}/keys
  getKeys: async (
    schema: string,
    tableName: string
  ): Promise<TableKeysResponse> => {
    const { data } = await apiClient.get<TableKeysResponse>(
      `/database/tables/${encodeURIComponent(schema)}/${encodeURIComponent(
        tableName
      )}/keys`
    );
    return data;
  },

  // GET /api/v1/database/tables/{schema}/{table}/indexes
  getIndexes: async (
    schema: string,
    tableName: string
  ): Promise<TableIndexesResponse> => {
    const { data } = await apiClient.get<TableIndexesResponse>(
      `/database/tables/${encodeURIComponent(schema)}/${encodeURIComponent(
        tableName
      )}/indexes`
    );
    return data;
  },

  // GET /api/v1/database/tables/{schema}/{table}/sample
  getSample: async (
    schema: string,
    tableName: string,
    limit: number = 50
  ): Promise<TableSampleResponse> => {
    const { data } = await apiClient.get<TableSampleResponse>(
      `/database/tables/${encodeURIComponent(schema)}/${encodeURIComponent(
        tableName
      )}/sample`,
      { params: { limit } }
    );
    return data;
  },

  // GET /api/v1/database/tables/{schema}/{table}/profile
  getProfile: async (
    schema: string,
    tableName: string
  ): Promise<TableProfileResponse> => {
    const { data } = await apiClient.get<TableProfileResponse>(
      `/database/tables/${encodeURIComponent(schema)}/${encodeURIComponent(
        tableName
      )}/profile`
    );
    return data;
  },

  // GET /api/v1/database/tables/{schema}/{table}/classification
  getClassification: async (
    schema: string,
    tableName: string
  ): Promise<TableClassificationResponse> => {
    const { data } = await apiClient.get<TableClassificationResponse>(
      `/database/tables/${encodeURIComponent(schema)}/${encodeURIComponent(
        tableName
      )}/classification`
    );
    return data;
  },

  // GET /api/v1/database/tables/{schema}/{table}/structure
  getStructure: async (
    schema: string,
    tableName: string
  ): Promise<TableStructureResponse> => {
    const { data } = await apiClient.get<TableStructureResponse>(
      `/database/tables/${encodeURIComponent(schema)}/${encodeURIComponent(
        tableName
      )}/structure`
    );
    return data;
  },
};
