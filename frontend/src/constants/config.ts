/**
 * Centralized Application & Environment Configuration
 */

const getApiBaseUrl = (): string => {
  const envUrl = process.env.EXPO_PUBLIC_API_URL;
  if (envUrl && envUrl.trim() !== "") {
    // Strip trailing slashes
    return envUrl.trim().replace(/\/+$/, "");
  }
  return "http://localhost:8000/api/v1";
};

export const ENV = {
  API_URL: getApiBaseUrl(),
  IS_DEV: process.env.NODE_ENV !== "production",
};

export const API_CONFIG = {
  BASE_URL: ENV.API_URL,
  TIMEOUT_MS: 30000,
  POLL_INTERVAL_MS: 2000,
  DEFAULT_PAGE_SIZE: 25,
};

export const QUERY_KEYS = {
  HEALTH: {
    API: ["health", "api"] as const,
    DATABASE: ["health", "database"] as const,
  },
  DATABASE: {
    SUMMARY: ["database", "summary"] as const,
    SCHEMAS: ["database", "schemas"] as const,
    TABLES: (params?: unknown) => ["database", "tables", params] as const,
    TABLE_SUMMARY: (schema: string, table: string) =>
      ["database", "tableSummary", schema, table] as const,
    COLUMNS: (schema: string, table: string) =>
      ["database", "columns", schema, table] as const,
    KEYS: (schema: string, table: string) =>
      ["database", "keys", schema, table] as const,
    INDEXES: (schema: string, table: string) =>
      ["database", "indexes", schema, table] as const,
    SAMPLE: (schema: string, table: string, limit?: number) =>
      ["database", "sample", schema, table, limit] as const,
    PROFILE: (schema: string, table: string) =>
      ["database", "profile", schema, table] as const,
    CLASSIFICATION: (schema: string, table: string) =>
      ["database", "classification", schema, table] as const,
  },
  ANALYSIS: {
    RUNS_LIST: (params?: unknown) => ["analysisRuns", "list", params] as const,
    RUN_DETAIL: (runId: string) => ["analysisRuns", "detail", runId] as const,
    RUN_TABLES: (runId: string, params?: unknown) =>
      ["analysisRuns", "tables", runId, params] as const,
    RUN_TABLE_DETAIL: (runId: string, schema: string, table: string) =>
      ["analysisRuns", "tableDetail", runId, schema, table] as const,
  },
};
