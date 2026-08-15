from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TableAnalysisStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class AnalysisStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"
    FAILED = "FAILED"


class TableSkipReason(str, Enum):
    EMPTY_TABLE = "EMPTY_TABLE"
    FILTERED = "FILTERED"


class QuickAnalysisRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str | None = Field(
        default=None,
        alias="schema",
        serialization_alias="schema",
        description="Optional schema filter (e.g. 'dbo')",
    )
    max_concurrent: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Optional override for max concurrent table analyses",
    )


class TableAnalysisPlan(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    estimated_rows: int
    column_count: int
    should_analyze: bool
    sample_size: int
    priority: int = 1
    skip_reason: str | None = None


class AnalysisPlan(BaseModel):
    database: str
    total_tables: int
    planned_tables: int
    skipped_tables: int
    table_plans: list[TableAnalysisPlan] = Field(default_factory=list)


class TableAnalysisTimings(BaseModel):
    structure_duration_ms: float = 0.0
    sampling_duration_ms: float = 0.0
    profiling_duration_ms: float = 0.0
    classification_duration_ms: float = 0.0
    total_duration_ms: float = 0.0


class TableAnalysisSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    estimated_rows: int
    status: TableAnalysisStatus
    skip_reason: str | None = None
    sample_size: int = 0
    returned_rows: int = 0
    column_count: int = 0
    profiled_columns: int = 0
    classified_columns: int = 0
    duration_ms: float = 0.0
    timings: TableAnalysisTimings | None = None
    error_code: str | None = None
    error_message: str | None = None
    profile_response: Any | None = Field(default=None, exclude=True)
    classification_response: Any | None = Field(default=None, exclude=True)


class TableAnalysisError(BaseModel):
    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    error_code: str
    error_message: str


class AnalysisProgress(BaseModel):
    tables_total: int
    tables_completed: int
    tables_failed: int
    tables_skipped: int
    progress_percent: float


class DatabaseAnalysisResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    database: str
    status: AnalysisStatus
    tables_total: int
    tables_analyzed: int
    tables_skipped: int
    tables_failed: int
    columns_discovered: int
    columns_profiled: int
    columns_classified: int
    started_at: datetime
    completed_at: datetime
    duration_ms: float
    tables: list[TableAnalysisSummary] = Field(default_factory=list)


# Alias for backward/forward naming compatibility
DatabaseAnalysisSummary = DatabaseAnalysisResponse
