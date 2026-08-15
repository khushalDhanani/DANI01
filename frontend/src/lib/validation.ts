/**
 * Zod - Runtime schema validation
 *
 * Re-exported here as the canonical import path for validation schemas.
 * Use this instead of importing directly from "zod" throughout the app.
 *
 * Schemas will be added to src/types/*.schema.ts in future milestones:
 *   - DatabaseSummarySchema
 *   - TableListSchema
 *   - AnalysisRunSchema
 *   - etc.
 */
export { z } from "zod";
export type { ZodSchema, ZodType, infer as ZodInfer } from "zod";
