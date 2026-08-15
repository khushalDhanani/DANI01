from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.analysis import TableAnalysisTimings


class CreateAnalysisRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    analysis_type: str = Field(
        default="QUICK", description="Type of analysis (e.g. 'QUICK')"
    )
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
        description="Optional override for max concurrent table workers",
    )


class AnalysisRunCreatedResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    run_id: str
    database: str
    analysis_type: str
    status: str
    created_at: datetime


class AnalysisRunDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    run_id: str
    database: str
    analysis_type: str
    schema_filter: str | None = None
    status: str
    tables_total: int = 0
    tables_completed: int = 0
    tables_skipped: int = 0
    tables_failed: int = 0
    columns_discovered: int = 0
    columns_profiled: int = 0
    columns_classified: int = 0
    progress_percent: float = 0.0
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: float | None = None
    error_code: str | None = None
    error_message: str | None = None


class AnalysisRunListResponse(BaseModel):
    items: list[AnalysisRunDetailResponse]
    total: int
    limit: int
    offset: int


class AnalysisRunTableResultItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    estimated_rows: int
    sample_size: int
    returned_rows: int
    column_count: int
    profiled_columns: int
    classified_columns: int
    status: str
    skip_reason: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    duration_ms: float


class AnalysisRunTableListResponse(BaseModel):
    run_id: str
    items: list[AnalysisRunTableResultItem]
    total: int
    limit: int
    offset: int


class AnalysisRunTableDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    estimated_rows: int
    sample_size: int
    returned_rows: int
    column_count: int
    status: str
    skip_reason: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    duration_ms: float
    timings: TableAnalysisTimings | None = None
    column_profiles: list[dict[str, Any]] = Field(default_factory=list)
    column_classifications: list[dict[str, Any]] = Field(default_factory=list)


class CancelAnalysisRunResponse(BaseModel):
    run_id: str
    status: str
    message: str
