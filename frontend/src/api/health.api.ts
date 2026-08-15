import { apiClient } from "@/api/client";
import type {
  DatabaseHealthResponse,
  HealthResponse} from "@/schemas/health.schema";
import {
  DatabaseHealthResponseSchema,
  HealthResponseSchema,
} from "@/schemas/health.schema";

export const healthApi = {
  // GET /api/v1/health
  getHealth: async (): Promise<HealthResponse> => {
    const { data } = await apiClient.get("/health");
    return HealthResponseSchema.parse(data);
  },

  // GET /api/v1/health/database
  getDatabaseHealth: async (): Promise<DatabaseHealthResponse> => {
    const { data } = await apiClient.get("/health/database");
    return DatabaseHealthResponseSchema.parse(data);
  },
};
