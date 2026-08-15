import { useQuery } from "@tanstack/react-query";
import { databaseApi } from "@/api/database.api";
import { QUERY_KEYS } from "@/constants/config";

export const useDatabaseSummary = () => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.SUMMARY,
    queryFn: databaseApi.getSummary,
    staleTime: 60 * 1000,
  });
};

export const useDatabaseSchemas = () => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.SCHEMAS,
    queryFn: databaseApi.getSchemas,
    staleTime: 60 * 1000,
  });
};

export const useSchemas = useDatabaseSchemas;

export const useDatabaseTables = (params?: {
  schema?: string;
  search?: string;
  limit?: number;
  offset?: number;
  sort_by?: "schema" | "table" | "estimated_rows" | "column_count";
  sort_order?: "asc" | "desc";
}) => {
  return useQuery({
    queryKey: QUERY_KEYS.DATABASE.TABLES(params),
    queryFn: () => databaseApi.getTables(params),
    staleTime: 30 * 1000,
    placeholderData: (previousData) => previousData,
  });
};
