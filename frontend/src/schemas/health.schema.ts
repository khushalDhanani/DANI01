import { z } from "zod";

export const HealthResponseSchema = z.object({
  status: z.string(),
  service: z.string().optional(),
});

export const DatabaseHealthResponseSchema = z.object({
  status: z.string(),
  database: z.string(),
});

export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export type DatabaseHealthResponse = z.infer<typeof DatabaseHealthResponseSchema>;
