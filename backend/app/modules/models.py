from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModuleTableRole(StrEnum):
    ROOT = "ROOT"
    DETAIL = "DETAIL"
    LOOKUP = "LOOKUP"
    CHILD = "CHILD"
    LOG = "LOG"
    REFERENCE = "REFERENCE"


class ModuleValidationStatus(StrEnum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"


class ModuleRelationshipDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    parent_table: str = Field(
        ..., description="Full parent table name e.g. 'dbo.DLPerson' or 'DLPerson'"
    )
    child_table: str = Field(..., description="Full child table name e.g. 'dbo.DLPersonAddressDet'")
    parent_key: str = Field(..., description="Parent key column name e.g. 'PersonID'")
    child_key: str = Field(..., description="Child foreign key column name e.g. 'PersonID'")
    relationship_type: str = Field(default="ONE_TO_MANY", description="ONE_TO_ONE or ONE_TO_MANY")
    required: bool = Field(
        default=False, description="Whether this relationship is strictly required"
    )


class ModuleTableDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(default="dbo", alias="schema", serialization_alias="schema")
    table_name: str = Field(..., alias="table", serialization_alias="table")
    role: ModuleTableRole = Field(
        default=ModuleTableRole.DETAIL, description="Role of the table in the module"
    )
    required: bool = Field(
        default=True, description="Whether table must exist for module to be valid"
    )
    key_columns: list[str] = Field(
        default_factory=list, description="Primary or linkage key columns"
    )
    important_columns: list[str] = Field(
        default_factory=list, description="Key domain columns to validate"
    )
    description: str | None = Field(
        default=None, description="Optional explanation of table's role"
    )


class ModuleDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(..., description="Unique module code e.g. 'PERSON', 'COMPANY'")
    name: str = Field(..., description="Human-readable module title e.g. 'Person & Contact'")
    description: str = Field(..., description="Detailed description of what this module inspects")
    root_schema: str = Field(default="dbo", description="Schema of the root entity table")
    root_table: str = Field(..., description="Root table name e.g. 'DLPerson'")
    root_key: str = Field(..., description="Root entity primary key e.g. 'PersonID'")
    tables: list[ModuleTableDefinition] = Field(
        default_factory=list, description="Configured module tables"
    )
    relationships: list[ModuleRelationshipDefinition] = Field(
        default_factory=list, description="Expected relationships"
    )
    enabled: bool = Field(default=True, description="Whether the module is active")
    tags: list[str] = Field(default_factory=list, description="Optional metadata tags")


class ModuleInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    name: str
    description: str
    root_table: str
    root_key: str
    table_count: int
    relationship_count: int
    enabled: bool
    tags: list[str] = Field(default_factory=list)


class ModuleValidationItem(BaseModel):
    level: str = Field(..., description="'ERROR', 'WARNING', or 'INFO'")
    target: str = Field(..., description="Target component e.g. 'root_table', 'table:dbo.DLPerson'")
    message: str = Field(..., description="Detailed validation message")


class ModuleTableValidation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table_name: str = Field(..., alias="table", serialization_alias="table")
    role: ModuleTableRole
    required: bool
    exists: bool
    estimated_rows: int = 0
    column_count: int = 0
    found_columns: list[str] = Field(default_factory=list)
    missing_columns: list[str] = Field(default_factory=list)


class ModuleValidationResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    name: str
    status: ModuleValidationStatus
    is_valid: bool
    root_table: str
    root_table_exists: bool
    root_key_exists: bool
    tables_configured: int
    tables_found: int
    tables_missing: int
    table_validations: list[ModuleTableValidation] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)
    items: list[ModuleValidationItem] = Field(default_factory=list)


class ModuleAnalysisContext(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    definition: ModuleDefinition
    validation: ModuleValidationResult
    table_structures: dict[str, Any] = Field(default_factory=dict)
    table_profiles: dict[str, Any] = Field(default_factory=dict)
    table_classifications: dict[str, Any] = Field(default_factory=dict)


class ModuleAnalysisResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    name: str
    status: ModuleValidationStatus
    validation: ModuleValidationResult
    tables_analyzed: int
    duration_ms: float = 0.0
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    table_summaries: list[dict[str, Any]] = Field(default_factory=list)
