export type SensitivityLevel =
  | "PUBLIC"
  | "INTERNAL"
  | "CONFIDENTIAL"
  | "PII"
  | "RESTRICTED"
  | "SENSITIVE"
  | string;

export interface ColumnClassification {
  name: string;
  column_name?: string;
  sql_type: string;
  semantic_type: string;
  sensitivity: SensitivityLevel;
  expose_values: boolean;
  confidence: number;
  signals?: string[];
}

export interface TableClassificationResponse {
  schema: string;
  table: string;
  columns: ColumnClassification[];
}
