from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TableSampleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    requested_rows: int
    returned_rows: int
    columns: list[str]
    rows: list[dict[str, Any]]
