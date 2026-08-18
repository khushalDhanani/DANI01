export interface SqlObjectMetadata {
  object_id: number;
  object_name: string;
  object_type: string;
  related_module: string;
  used_tables: string[];
  dml_operations: string[];
  joins_count: number;
  has_active_emp_logic: boolean;
  has_active_deleted_logic: boolean;
  has_resign_logic: boolean;
  def_snippet: string;
}

export interface BusinessRuleConceptInfo {
  rule_code: string;
  rule_name: string;
  category: string;
  description: string;
  canonical_recommendation: string;
  objects_count: number;
  inconsistency_variants_count: number;
}

export interface LogicInconsistencyItem {
  inconsistency_id: string;
  rule_code: string;
  rule_name: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  confidence: "CONFIRMED" | "LIKELY";
  affected_objects_count: number;
  sample_objects: string[];
  predicate_used: string;
  difference_analysis: string;
  business_risk: string;
  canonical_recommendation: string;
}

export interface ProcedureLogicOverviewResponse {
  total_sql_objects: number;
  total_stored_procedures: number;
  total_functions: number;
  total_views: number;
  total_triggers: number;
  total_inconsistencies: number;
  critical_inconsistencies_count: number;
  warning_inconsistencies_count: number;
  info_inconsistencies_count: number;
  business_rules: BusinessRuleConceptInfo[];
  object_type_distribution: Record<string, number>;
  module_distribution: Record<string, number>;
}

export interface SqlObjectListResponse {
  items: SqlObjectMetadata[];
  total: number;
  limit: number;
  offset: number;
  object_type?: string | null;
  module?: string | null;
  search?: string | null;
}

export interface LogicInconsistenciesListResponse {
  items: LogicInconsistencyItem[];
  total: number;
  limit: number;
  offset: number;
  severity?: string | null;
  rule_code?: string | null;
  search?: string | null;
}

export interface SqlObjectDetailResponse {
  object_id: number;
  object_name: string;
  object_type: string;
  definition: string;
  used_tables: string[];
  dml_operations: string[];
  inconsistencies: LogicInconsistencyItem[];
}
