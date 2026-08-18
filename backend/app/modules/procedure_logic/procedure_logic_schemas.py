from pydantic import BaseModel, Field


class SqlObjectMetadata(BaseModel):
    object_id: int = Field(..., description="MSSQL system object_id")
    object_name: str = Field(
        ..., description="Name of the stored procedure, function, view, or trigger"
    )
    object_type: str = Field(
        ...,
        description="Object type e.g. SQL_STORED_PROCEDURE, SQL_SCALAR_FUNCTION, VIEW, SQL_TRIGGER",
    )
    related_module: str = Field(
        ...,
        description="Workforce module e.g. EMPLOYEE, ORGANIZATION, ATTENDANCE, LEAVE, PAYROLL, SECURITY",
    )
    used_tables: list[str] = Field(
        default_factory=list, description="Target database tables referenced in SQL definition"
    )
    dml_operations: list[str] = Field(
        default_factory=list,
        description="Operations detected: SELECT, INSERT, UPDATE, DELETE, MERGE",
    )
    joins_count: int = Field(..., description="Count of SQL JOIN clauses")
    has_active_emp_logic: bool = Field(
        ..., description="Whether active employee filtering logic is present"
    )
    has_active_deleted_logic: bool = Field(
        ..., description="Whether soft-delete filtering logic is present"
    )
    has_resign_logic: bool = Field(
        ..., description="Whether resignation date filtering logic is present"
    )
    def_snippet: str = Field(..., description="Brief code snippet preview of the SQL definition")


class BusinessRuleConceptInfo(BaseModel):
    rule_code: str = Field(..., description="Unique rule concept identifier e.g. ACTIVE_EMPLOYEE")
    rule_name: str = Field(..., description="Human-readable business rule name")
    category: str = Field(..., description="Target domain category")
    description: str = Field(..., description="Description of the business rule concept")
    canonical_recommendation: str = Field(
        ..., description="Recommended single canonical SQL predicate"
    )
    objects_count: int = Field(
        ..., description="Total SQL objects implementing logic for this rule"
    )
    inconsistency_variants_count: int = Field(
        ..., description="Number of conflicting predicate variants detected"
    )


class LogicInconsistencyItem(BaseModel):
    inconsistency_id: str = Field(
        ..., description="Unique identifier for the inconsistency finding"
    )
    rule_code: str = Field(..., description="Target business rule concept code")
    rule_name: str = Field(..., description="Human-readable business rule name")
    severity: str = Field(..., description="Severity level: CRITICAL, WARNING, INFO")
    confidence: str = Field(..., description="Confidence rating: CONFIRMED, LIKELY")
    affected_objects_count: int = Field(
        ..., description="Number of SQL objects using this conflicting predicate"
    )
    sample_objects: list[str] = Field(
        default_factory=list,
        description="Sample SQL stored procedures or functions using this predicate",
    )
    predicate_used: str = Field(
        ..., description="The actual SQL predicate extracted from definitions"
    )
    difference_analysis: str = Field(
        ..., description="Explanation of how this predicate differs from canonical standards"
    )
    business_risk: str = Field(..., description="Business risk of results discrepancy")
    canonical_recommendation: str = Field(
        ..., description="Recommended standardized replacement SQL predicate"
    )


class ProcedureLogicOverviewResponse(BaseModel):
    total_sql_objects: int = Field(..., description="Total employee/workforce SQL objects analyzed")
    total_stored_procedures: int = Field(..., description="Stored procedures count")
    total_functions: int = Field(..., description="Scalar and table-valued functions count")
    total_views: int = Field(..., description="Views count")
    total_triggers: int = Field(..., description="Triggers count")
    total_inconsistencies: int = Field(
        ..., description="Total logic inconsistency findings detected"
    )
    critical_inconsistencies_count: int = Field(
        ..., description="Critical logic inconsistencies count"
    )
    warning_inconsistencies_count: int = Field(
        ..., description="Warning logic inconsistencies count"
    )
    info_inconsistencies_count: int = Field(..., description="Info logic inconsistencies count")
    business_rules: list[BusinessRuleConceptInfo] = Field(
        default_factory=list, description="Business rule concepts catalog"
    )
    object_type_distribution: dict[str, int] = Field(
        default_factory=dict, description="Counts by SQL object type"
    )
    module_distribution: dict[str, int] = Field(
        default_factory=dict, description="Counts by workforce module"
    )


class SqlObjectListResponse(BaseModel):
    items: list[SqlObjectMetadata] = Field(
        default_factory=list, description="Paginated SQL object metadata items"
    )
    total: int = Field(..., description="Total matching SQL objects")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")
    object_type: str | None = Field(default=None, description="Active object type filter")
    module: str | None = Field(default=None, description="Active module filter")
    search: str | None = Field(default=None, description="Active search filter")


class LogicInconsistenciesListResponse(BaseModel):
    items: list[LogicInconsistencyItem] = Field(
        default_factory=list, description="Paginated inconsistency items"
    )
    total: int = Field(..., description="Total matching inconsistencies")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")
    severity: str | None = Field(default=None, description="Active severity filter")
    rule_code: str | None = Field(default=None, description="Active rule code filter")
    search: str | None = Field(default=None, description="Active search filter")


class SqlObjectDetailResponse(BaseModel):
    object_id: int = Field(..., description="Object ID")
    object_name: str = Field(..., description="Object Name")
    object_type: str = Field(..., description="Object Type")
    definition: str = Field(..., description="Full SQL definition code")
    used_tables: list[str] = Field(default_factory=list)
    dml_operations: list[str] = Field(default_factory=list)
    inconsistencies: list[LogicInconsistencyItem] = Field(default_factory=list)
