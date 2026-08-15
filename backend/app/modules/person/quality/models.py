from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class QualityCategory(str, Enum):
    COMPLETENESS = "COMPLETENESS"
    VALIDITY = "VALIDITY"
    INTEGRITY = "INTEGRITY"
    CONSISTENCY = "CONSISTENCY"


class QualitySeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class QualityFindingStatus(str, Enum):
    APPLIED = "APPLIED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class QualityFinding(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rule_code: str = Field(..., description="Unique rule code e.g. 'PERSON_MISSING_ADDRESS'")
    category: QualityCategory = Field(..., description="COMPLETENESS, VALIDITY, INTEGRITY, or CONSISTENCY")
    severity: QualitySeverity = Field(..., description="CRITICAL, HIGH, MEDIUM, or LOW")
    title: str = Field(..., description="Human-readable rule title")
    description: str = Field(..., description="Explanation of what this rule tests")
    affected_count: int = Field(default=0, description="Count of invalid/affected records")
    total_evaluated: int = Field(default=0, description="Total scope denominator evaluated")
    affected_percent: float = Field(default=0.0, description="Percentage of affected records (0.0 - 100.0)")
    exact: bool = Field(default=True, description="Whether the metric count is exact")
    message: str = Field(..., description="Detailed explanation of the finding outcome")
    status: QualityFindingStatus = Field(default=QualityFindingStatus.APPLIED, description="APPLIED, SKIPPED, or FAILED")
    skip_reason: str | None = Field(default=None, description="Reason if rule was skipped due to missing optional table/column")


class QualitySeveritySummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    critical: int = Field(default=0, description="Count of findings with CRITICAL severity")
    high: int = Field(default=0, description="Count of findings with HIGH severity")
    medium: int = Field(default=0, description="Count of findings with MEDIUM severity")
    low: int = Field(default=0, description="Count of findings with LOW severity")


class PersonQualityResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    module: str = Field(default="PERSON", description="Module code")
    status: str = Field(default="COMPLETED", description="'COMPLETED', 'DEGRADED', or 'FAILED'")
    rules_evaluated: int = Field(..., description="Total count of applicable evaluated rules")
    rules_skipped: int = Field(default=0, description="Count of skipped rules due to missing optional metadata")
    findings_count: int = Field(..., description="Count of rules where affected_count > 0")
    severity_summary: QualitySeveritySummary
    findings: list[QualityFinding] = Field(default_factory=list)
    duration_ms: float = Field(default=0.0, description="Total quality execution duration in milliseconds")
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Evaluation timestamp")
