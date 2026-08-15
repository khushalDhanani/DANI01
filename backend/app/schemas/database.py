from pydantic import BaseModel, ConfigDict, Field


class DatabaseSummary(BaseModel):
    database: str
    schema_count: int
    table_count: int
    column_count: int
    estimated_rows: int


class SchemaInfo(BaseModel):
    name: str
    table_count: int


class SchemaListResponse(BaseModel):
    items: list[SchemaInfo]
    total: int


class TableInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    estimated_rows: int
    column_count: int


class TableListResponse(BaseModel):
    items: list[TableInfo]
    total: int
    limit: int
    offset: int


class ColumnInfo(BaseModel):
    ordinal: int
    name: str
    data_type: str
    max_length: int | None = None
    precision: int | None = None
    scale: int | None = None
    nullable: bool
    identity: bool
    computed: bool
    has_default: bool
    default_definition: str | None = None
    primary_key: bool = False
    foreign_key: bool = False


class ColumnListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    columns: list[ColumnInfo]


class PrimaryKeyColumn(BaseModel):
    name: str
    ordinal: int


class PrimaryKeyInfo(BaseModel):
    name: str
    columns: list[PrimaryKeyColumn]


class ForeignKeyColumn(BaseModel):
    column: str
    referenced_column: str
    ordinal: int


class ForeignKeyReference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str


class ForeignKeyInfo(BaseModel):
    name: str
    columns: list[ForeignKeyColumn]
    references: ForeignKeyReference
    on_delete: str = "NO_ACTION"
    on_update: str = "NO_ACTION"


class TableKeysResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    primary_key: PrimaryKeyInfo | None = None
    foreign_keys: list[ForeignKeyInfo] = Field(default_factory=list)


class IndexColumn(BaseModel):
    name: str
    ordinal: int
    descending: bool = False


class IndexInfo(BaseModel):
    name: str
    type: str
    unique: bool = False
    primary_key: bool = False
    unique_constraint: bool = False
    disabled: bool = False
    key_columns: list[IndexColumn] = Field(default_factory=list)
    included_columns: list[str] = Field(default_factory=list)


class IndexListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    indexes: list[IndexInfo] = Field(default_factory=list)


class TableStructureResponse(BaseModel):
    table: TableInfo
    columns: list[ColumnInfo] = Field(default_factory=list)
    primary_key: PrimaryKeyInfo | None = None
    foreign_keys: list[ForeignKeyInfo] = Field(default_factory=list)
    indexes: list[IndexInfo] = Field(default_factory=list)
