import type { BaseColumnProfile } from "./profiling.types";
import type { ColumnClassification } from "./classification.types";

export type AnalysisStatus =
  | "PENDING"
  | "RUNNING"
  | "COMPLETED"
  | "COMPLETED_WITH_ERRORS"
  | "FAILED";

export type TableAnalysisStatus =
  | "PENDING"
  | "RUNNING"
  | "COMPLETED"
  | "SKIPPED"
  | "FAILED";

export interface QuickAnalysisRequest {
  schema?: string | null;
  max_concurrent?: number | null;
}

export interface TableAnalysisTimings {
  structure_duration_ms: number;
  sampling_duration_ms: number;
  profiling_duration_ms: number;
  classification_duration_ms: number;
  total_duration_ms: number;
}

export interface TableAnalysisSummary {
  schema: string;
  table: string;
  estimated_rows: number;
  status: TableAnalysisStatus;
  skip_reason?: string | null;
  sample_size: number;
  returned_rows: number;
  column_count: number;
  profiled_columns: number;
  classified_columns: number;
  duration_ms: number;
  timings?: TableAnalysisTimings | null;
  error_code?: string | null;
  error_message?: string | null;
}

export interface DatabaseAnalysisResponse {
  database: string;
  status: AnalysisStatus;
  tables_total: number;
  tables_analyzed: number;
  tables_skipped: number;
  tables_failed: number;
  columns_discovered: number;
  columns_profiled: number;
  columns_classified: number;
  started_at: string;
  completed_at: string;
  duration_ms: number;
  tables: TableAnalysisSummary[];
}

export type AnalysisRunStatus =
  | "QUEUED"
  | "RUNNING"
  | "COMPLETED"
  | "COMPLETED_WITH_ERRORS"
  | "FAILED"
  | "CANCELLING"
  | "CANCELLED";

export interface CreateAnalysisRunRequest {
  analysis_type?: string;
  schema?: string;
  max_concurrent?: number;
}

export interface AnalysisRunCreatedResponse {
  run_id: string;
  database: string;
  analysis_type: string;
  status: AnalysisRunStatus;
  created_at: string;
}

export interface AnalysisRunDetail {
  run_id: string;
  database: string;
  analysis_type: string;
  schema_filter?: string | null;
  status: AnalysisRunStatus;
  tables_total: number;
  tables_completed: number;
  tables_skipped: number;
  tables_failed: number;
  columns_discovered: number;
  columns_profiled: number;
  columns_classified: number;
  progress_percent: number;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  duration_ms?: number | null;
  error_code?: string | null;
  error_message?: string | null;
}

export interface AnalysisRunListResponse {
  items: AnalysisRunDetail[];
  total: number;
  limit: number;
  offset: number;
}

export interface AnalysisRunTableItem {
  schema: string;
  table: string;
  estimated_rows: number;
  sample_size: number;
  returned_rows: number;
  column_count: number;
  profiled_columns: number;
  classified_columns: number;
  status: "COMPLETED" | "SKIPPED" | "FAILED";
  skip_reason?: string | null;
  error_code?: string | null;
  error_message?: string | null;
  duration_ms: number;
}

export interface AnalysisRunTableListResponse {
  run_id: string;
  items: AnalysisRunTableItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface TableTimings {
  structure_duration_ms: number;
  sampling_duration_ms: number;
  profiling_duration_ms: number;
  classification_duration_ms: number;
  total_duration_ms: number;
}

export interface AnalysisRunTableDetail {
  schema: string;
  table: string;
  estimated_rows: number;
  sample_size: number;
  returned_rows: number;
  column_count: number;
  status: "COMPLETED" | "SKIPPED" | "FAILED";
  skip_reason?: string | null;
  error_code?: string | null;
  error_message?: string | null;
  duration_ms: number;
  timings?: TableTimings;
  column_profiles: BaseColumnProfile[];
  column_classifications: ColumnClassification[];
}
