from datetime import datetime, timezone
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

    # 2. Address Coverage
    persons_with_address: int | None = Field(default=None, description="Distinct persons with at least one physical/postal address")
    persons_without_address: int | None = Field(default=None, description="Persons missing address records")
    address_coverage_percent: float | None = Field(default=None, description="Percentage of persons having an address")
    total_addresses: int | None = Field(default=None, description="Total rows in address detail table")

    # 3. Contact Channel Coverage
    persons_with_contact: int | None = Field(default=None, description="Distinct persons with at least one communication channel")
    persons_without_contact: int | None = Field(default=None, description="Persons missing all contact records")
    contact_coverage_percent: float | None = Field(default=None, description="Percentage of persons having contact info")
    total_contacts: int | None = Field(default=None, description="Total rows in contact detail table")

    # 4. Email Coverage
    persons_with_email: int | None = Field(default=None, description="Distinct persons with at least one email address")
    persons_without_email: int | None = Field(default=None, description="Persons missing email address")
    email_coverage_percent: float | None = Field(default=None, description="Percentage of persons having an email")

    # 5. Phone Coverage
    persons_with_phone: int | None = Field(default=None, description="Distinct persons with at least one telephone/mobile number")
    persons_without_phone: int | None = Field(default=None, description="Persons missing phone number")
    phone_coverage_percent: float | None = Field(default=None, description="Percentage of persons having a phone")

    # 6. Company Affiliation Linkage
    persons_with_company_link: int | None = Field(default=None, description="Distinct persons linked to at least one organization")
    persons_without_company_link: int | None = Field(default=None, description="Persons with no company affiliation")
    company_link_coverage_percent: float | None = Field(default=None, description="Percentage of persons linked to a company")
    total_company_links: int | None = Field(default=None, description="Total rows in company link table")

    # 7. Inter-Personal Relationship Linkage
    persons_with_relationship: int | None = Field(default=None, description="Distinct persons linked via relation table")
    persons_without_relationship: int | None = Field(default=None, description="Persons with no recorded relationships")
    relationship_coverage_percent: float | None = Field(default=None, description="Percentage of persons with relationships")
    total_relationships: int | None = Field(default=None, description="Total rows in relationship table")

    # 8. Document Attachments Coverage
    persons_with_document: int | None = Field(default=None, description="Distinct persons with uploaded document attachments")
    persons_without_document: int | None = Field(default=None, description="Persons without documents")
    document_coverage_percent: float | None = Field(default=None, description="Percentage of persons with documents")
    total_documents: int | None = Field(default=None, description="Total rows in document detail table")

    # 9. Custom Dynamic Extra Fields Coverage
    persons_with_extra_field: int | None = Field(default=None, description="Distinct persons with custom extra field values")
    persons_without_extra_field: int | None = Field(default=None, description="Persons without custom extra field values")
    extra_field_coverage_percent: float | None = Field(default=None, description="Percentage of persons with extra field values")
    total_extra_fields: int | None = Field(default=None, description="Total rows in extra field value detail table")

    # 10. Instant Messaging Handles Coverage
    persons_with_im: int | None = Field(default=None, description="Distinct persons with instant messaging handles")
    persons_without_im: int | None = Field(default=None, description="Persons without IM records")
    im_coverage_percent: float | None = Field(default=None, description="Percentage of persons with IM handles")
    total_ims: int | None = Field(default=None, description="Total rows in IM detail table")

    # 11. Contact Quality & Health Sub-Metrics
    active_contacts: int | None = Field(default=None, description="Total active contact rows (PersonPhoneIsActive = 1)")
    active_contacts_percent: float | None = Field(default=None, description="Percentage of active contacts out of total contact rows")
    verified_contacts: int | None = Field(default=None, description="Total verified contact rows (IsVerified = 1)")
    verified_contacts_percent: float | None = Field(default=None, description="Percentage of verified contacts out of total contact rows")
    primary_contacts: int | None = Field(default=None, description="Total primary contact rows (IsPrimary = 1)")
    primary_contacts_percent: float | None = Field(default=None, description="Percentage of primary contacts out of total contact rows")

    # 12. Address Quality & Health Sub-Metrics
    active_addresses: int | None = Field(default=None, description="Total active address rows (PersonAddIsActive = 1)")
    active_addresses_percent: float | None = Field(default=None, description="Percentage of active addresses out of total address rows")
    geo_addresses: int | None = Field(default=None, description="Total address rows with latitude and longitude")
    geo_addresses_percent: float | None = Field(default=None, description="Percentage of address rows with geo-coordinates")
    formatted_addresses: int | None = Field(default=None, description="Total address rows with GoogleFormattedAddress")
    formatted_addresses_percent: float | None = Field(default=None, description="Percentage of address rows with formatted address")
    postal_addresses: int | None = Field(default=None, description="Total address rows with PostalCode")
    postal_addresses_percent: float | None = Field(default=None, description="Percentage of address rows with postal code")


class PersonModuleMetricsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    module: str = Field(default="PERSON", description="Module code")
    status: str = Field(..., description="'COMPLETED', 'DEGRADED', or 'FAILED'")
    root_entity: str = Field(..., description="Root table name used as denominator")
    metrics: PersonMetricsSummary
    warnings: list[str] = Field(default_factory=list, description="Warnings regarding missing optional tables or columns")
    duration_ms: float = Field(default=0.0, description="Metric calculation execution duration in milliseconds")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of calculation")
