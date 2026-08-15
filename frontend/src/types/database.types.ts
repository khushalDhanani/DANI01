/**
 * Database domain TypeScript interfaces.
 * All shapes verified against live FastAPI responses.
 */

// GET /api/v1/database/summary
export interface DatabaseSummary {
  database: string;
  schema_count: number;
  table_count: number;
  column_count: number;
  estimated_rows: number;
}

// GET /api/v1/database/schemas — items array
export interface SchemaInfo {
  name: string;
  table_count: number;
}

// GET /api/v1/database/schemas — top-level response
export interface SchemaListResponse {
  items: SchemaInfo[];
  total: number;
}

// GET /api/v1/database/tables — single table row
export interface TableInfo {
  schema: string;
  table: string;
  estimated_rows: number;
  column_count: number;
  table_type?: string;
}

// GET /api/v1/database/tables — top-level response
export interface TableListResponse {
  items: TableInfo[];
  total: number;
  limit: number;
  offset: number;
}

// GET /api/v1/database/tables/{schema}/{table}/sample
export interface TableSampleResponse {
  schema: string;
  table: string;
  requested_rows: number;
  returned_rows: number;
  columns: string[];
  rows: Record<string, unknown>[];
}

// GET /api/v1/database/tables/{schema}/{table}/columns — single column
export interface ColumnInfo {
  ordinal: number;
  name: string;
  data_type: string;
  max_length?: number | null;
  precision?: number | null;
  scale?: number | null;
  nullable: boolean;
  identity: boolean;
  computed: boolean;
  has_default?: boolean;
  default_definition?: string | null;
  primary_key?: boolean;
  foreign_key?: boolean;
}

// GET /api/v1/database/tables/{schema}/{table}/columns
export interface ColumnListResponse {
  schema: string;
  table: string;
  columns: ColumnInfo[];
}

export interface PrimaryKeyColumn {
  name: string;
  ordinal: number;
}

export interface PrimaryKeyInfo {
  name: string;
  columns: PrimaryKeyColumn[];
}

export interface ForeignKeyColumn {
  column: string;
  referenced_column: string;
  ordinal: number;
}

export interface ForeignKeyInfo {
  name: string;
  columns: ForeignKeyColumn[];
  references: {
    schema: string;
    table: string;
  };
  on_delete?: string;
  on_update?: string;
}

// GET /api/v1/database/tables/{schema}/{table}/keys
export interface TableKeysResponse {
  schema: string;
  table: string;
  primary_key?: PrimaryKeyInfo | null;
  foreign_keys: ForeignKeyInfo[];
}

export interface IndexKeyColumn {
  name: string;
  ordinal: number;
  descending: boolean;
}

export interface IndexInfo {
  name: string;
  type: string;
  unique: boolean;
  primary_key: boolean;
  unique_constraint?: boolean;
  disabled?: boolean;
  key_columns: IndexKeyColumn[];
  included_columns: string[];
}

// GET /api/v1/database/tables/{schema}/{table}/indexes
export interface TableIndexesResponse {
  schema: string;
  table: string;
  indexes: IndexInfo[];
}

// GET /api/v1/database/tables/{schema}/{table}/structure
export interface TableStructureResponse {
  schema: string;
  table: string;
  estimated_rows: number;
  columns: ColumnInfo[];
  primary_key?: PrimaryKeyInfo | null;
  foreign_keys: ForeignKeyInfo[];
  indexes: IndexInfo[];
}
