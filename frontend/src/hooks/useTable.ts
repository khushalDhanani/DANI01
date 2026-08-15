import { useQuery } from "@tanstack/react-query";
import { tableApi } from "@/api/table.api";
import { QUERY_KEYS } from "@/constants/config";

export const useTableSummary = (schema: string, tableName: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.TABLE_SUMMARY(schema, tableName),
    queryFn: () => tableApi.getTableSummary(schema, tableName),
    enabled: Boolean(schema && tableName),
    staleTime: 60 * 1000,
  });
};

export const useTableColumns = (
  schema: string,
  tableName: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.COLUMNS(schema, tableName),
    queryFn: () => tableApi.getColumns(schema, tableName),
    enabled: Boolean(schema && tableName) && (options?.enabled ?? true),
    staleTime: 60 * 1000,
  });
};

export const useTableKeys = (
  schema: string,
  tableName: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.KEYS(schema, tableName),
    queryFn: () => tableApi.getKeys(schema, tableName),
    enabled: Boolean(schema && tableName) && (options?.enabled ?? true),
    staleTime: 60 * 1000,
  });
};

export const useTableIndexes = (
  schema: string,
  tableName: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.INDEXES(schema, tableName),
    queryFn: () => tableApi.getIndexes(schema, tableName),
    enabled: Boolean(schema && tableName) && (options?.enabled ?? true),
    staleTime: 60 * 1000,
  });
};

export const useTableSample = (
  schema: string,
  tableName: string,
  limit: number = 50,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.SAMPLE(schema, tableName, limit),
    queryFn: () => tableApi.getSample(schema, tableName, limit),
    enabled: Boolean(schema && tableName) && (options?.enabled ?? true),
    staleTime: 60 * 1000,
  });
};

export const useTableProfile = (
  schema: string,
  tableName: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.PROFILE(schema, tableName),
    queryFn: () => tableApi.getProfile(schema, tableName),
    enabled: Boolean(schema && tableName) && (options?.enabled ?? true),
    staleTime: 60 * 1000,
  });
};

export const useTableClassification = (
  schema: string,
  tableName: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.CLASSIFICATION(schema, tableName),
    queryFn: () => tableApi.getClassification(schema, tableName),
    enabled: Boolean(schema && tableName) && (options?.enabled ?? true),
    staleTime: 60 * 1000,
  });
};

export const useTableStructure = (
  schema: string,
  tableName: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: ["database", "structure", schema, tableName],
    queryFn: () => tableApi.getStructure(schema, tableName),
    enabled: Boolean(schema && tableName) && (options?.enabled ?? true),
    staleTime: 60 * 1000,
  });
};
