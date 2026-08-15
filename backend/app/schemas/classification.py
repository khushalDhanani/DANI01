from pydantic import BaseModel, ConfigDict, Field


class ColumnClassification(BaseModel):
    name: str
    sql_type: str
    semantic_type: str
    sensitivity: str
    expose_values: bool
    confidence: float
    signals: list[str] = Field(default_factory=list)


class TableClassificationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(..., alias="schema", serialization_alias="schema")
    table: str
    columns: list[ColumnClassification]
