from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ValueFrequency(BaseModel):
    value: Any
    count: int
    percent: float


class BaseColumnProfile(BaseModel):
    name: str
    data_type: str
    profile_type: str = "generic"
    null_count: int
    null_percent: float
    distinct_count: int
    distinct_percent: float
    top_values: list[ValueFrequency] = Field(default_factory=list)


class TextColumnProfile(BaseColumnProfile):
    profile_type: Literal["text"] = "text"
    empty_count: int = 0
    empty_percent: float = 0.0
    blank_count: int = 0
    blank_percent: float = 0.0
    min_length: int | None = None
    max_length: int | None = None
    avg_length: float | None = None


class NumericColumnProfile(BaseColumnProfile):
    profile_type: Literal["numeric"] = "numeric"
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    median: float | None = None
    std_dev: float | None = None
    zero_count: int = 0
    zero_percent: float = 0.0
    negative_count: int = 0
    negative_percent: float = 0.0


class DateTimeColumnProfile(BaseColumnProfile):
    profile_type: Literal["datetime"] = "datetime"
    min: str | None = None
    max: str | None = None


class BooleanColumnProfile(BaseColumnProfile):
    profile_type: Literal["boolean"] = "boolean"
    true_count: int = 0
    false_count: int = 0
    true_percent: float = 0.0
    false_percent: float = 0.0


class TableProfileResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    sample_size: int
    returned_rows: int
    columns: list[
        TextColumnProfile
        | NumericColumnProfile
        | DateTimeColumnProfile
        | BooleanColumnProfile
        | BaseColumnProfile
    ]
