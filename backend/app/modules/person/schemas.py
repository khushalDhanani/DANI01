from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class PersonMetricsSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # 1. Total & Status Counts
    total_persons: int = Field(..., description="Total count of person entities in the root table")
    active_persons: int | None = Field(default=None, description="Persons marked as active (PersonIsActive = 1)")
    inactive_persons: int | None = Field(default=None, description="Persons marked as inactive or NULL")
    active_percent: float | None = Field(default=None, description="Percentage of active persons")
    inactive_percent: float | None = Field(default=None, description="Percentage of inactive persons")
    deleted_persons: int | None = Field(default=None, description="Persons marked as deleted (PersonIsDeleted = 1)")
    deleted_percent: float | None = Field(default=None, description="Percentage of deleted persons")
    temp_persons: int | None = Field(default=None, description="Temporary/unverified persons (PersonIsTemp = 1)")
    temp_percent: float | None = Field(default=None, description="Percentage of temporary persons")
    blacklist_persons: int | None = Field(default=None, description="Blacklisted persons (PersonIsBlackList = 1)")
    blacklist_percent: float | None = Field(default=None, description="Percentage of blacklisted persons")

    # Business Mappings: PersonIsVisitor_Contact (1=Visitor, 2=Contact)
    visitor_count: int | None = Field(default=None, description="Visitors (PersonIsVisitor_Contact = 1)")
    visitor_percent: float | None = Field(default=None, description="Percentage of Visitors")
    contact_entity_count: int | None = Field(default=None, description="Contacts (PersonIsVisitor_Contact = 2)")
    contact_entity_percent: float | None = Field(default=None, description="Percentage of Contacts")

    # Business Mappings: PersonIsShareContact (0=Private, 1=Public)
    public_count: int | None = Field(default=None, description="Public contacts (PersonIsShareContact = 1)")
    public_percent: float | None = Field(default=None, description="Percentage of Public contacts")
    private_count: int | None = Field(default=None, description="Private contacts (PersonIsShareContact = 0 or NULL)")
    private_percent: float | None = Field(default=None, description="Percentage of Private contacts")





class PersonModuleMetricsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    module: str = Field(default="PERSON", description="Module code")
    status: str = Field(..., description="'COMPLETED', 'DEGRADED', or 'FAILED'")
    root_entity: str = Field(..., description="Root table name used as denominator")
    metrics: PersonMetricsSummary
    warnings: list[str] = Field(default_factory=list, description="Warnings regarding missing optional tables or columns")
    duration_ms: float = Field(default=0.0, description="Metric calculation execution duration in milliseconds")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Timestamp of calculation")
