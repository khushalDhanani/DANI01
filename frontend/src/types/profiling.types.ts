export interface ValueFrequency {
  value: string | number | boolean | null;
  count: number;
  percent: number;
}

export interface ColumnProfile {
  name: string;
  column_name?: string;
  data_type: string;
  profile_type: "text" | "numeric" | "datetime" | "boolean" | string;
  null_count: number;
  null_percent: number;
  distinct_count: number;
  distinct_percent: number;
  top_values?: ValueFrequency[];
  // text metrics
  min_length?: number | null;
  max_length?: number | null;
  avg_length?: number | null;
  empty_count?: number | null;
  empty_percent?: number | null;
  blank_count?: number | null;
  blank_percent?: number | null;
  // numeric metrics
  min?: number | null;
  max?: number | null;
  mean?: number | null;
  median?: number | null;
  std_dev?: number | null;
  zero_count?: number | null;
  zero_percent?: number | null;
  negative_count?: number | null;
  negative_percent?: number | null;
  // datetime metrics
  earliest?: string | null;
  latest?: string | null;
  // boolean metrics
  true_count?: number | null;
  true_percent?: number | null;
  false_count?: number | null;
  false_percent?: number | null;
  stats?: Record<string, unknown>;
}

export type BaseColumnProfile = ColumnProfile;

export interface TableProfileResponse {
  schema: string;
  table: string;
  sample_size: number;
  returned_rows: number;
  columns: ColumnProfile[];
}
