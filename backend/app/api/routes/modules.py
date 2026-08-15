import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.dependencies import (
    get_contact_quality_service,
    get_module_analyzer,
    get_module_registry,
    get_person_analyzer,
    get_person_quality_engine,
    get_person_records_service,
)
from app.modules.analyzer import ModuleAnalyzer
from app.modules.models import ModuleDefinition, ModuleInfo, ModuleValidationResult
from app.modules.person.analyzer import PersonModuleAnalyzer
from app.modules.person.contact_quality_schemas import (
    RULE_METADATA,
    ContactQualityIssuesResponse,
    ContactQualitySummaryResponse,
    QualityRuleMeta,
)
from app.modules.person.contact_quality_service import ContactQualityService
from app.modules.person.quality.engine import PersonQualityEngine
from app.modules.person.quality.models import PersonQualityResponse
from app.modules.person.records_schemas import (
    PersonListResponse,
    PersonRecordDetailResponse,
)
from app.modules.person.records_service import PersonRecordsService
from app.modules.person.schemas import PersonModuleMetricsResponse
from app.modules.registry import ModuleRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/modules", tags=["Modules"])


@router.get(
    "",
    response_model=list[ModuleInfo],
    summary="List all registered domain modules",
    description="Returns metadata for all available predefined domain modules (e.g. PERSON, FINANCE).",
)
async def list_modules(
    registry: Annotated[ModuleRegistry, Depends(get_module_registry)],
) -> list[ModuleInfo]:
    return registry.list_info()


@router.get(
    "/PERSON/metrics",
    response_model=PersonModuleMetricsResponse,
    summary="Get dedicated PERSON KPI metrics",
    description="Calculates and returns specialized Person domain KPIs from live MSSQL tables.",
)
async def get_person_metrics(
    analyzer: Annotated[PersonModuleAnalyzer, Depends(get_person_analyzer)],
) -> PersonModuleMetricsResponse:
    return await analyzer.analyze_metrics()


@router.get(
    "/PERSON/quality",
    response_model=PersonQualityResponse,
    summary="Run PERSON data quality rule assessment",
    description="Executes deterministic data quality validation rules across PERSON tables and returns scores.",
)
async def get_person_quality(
    engine: Annotated[PersonQualityEngine, Depends(get_person_quality_engine)],
) -> PersonQualityResponse:
    return await engine.evaluate_quality()


@router.get(
    "/PERSON/records",
    response_model=PersonListResponse,
    summary="List paginated Person master records",
    description="Returns a paginated list of Person records from dbo.DLPersonMst with multi-table search, status filtering, and linked indicators.",
)
async def get_person_records_list(
    records_service: Annotated[PersonRecordsService, Depends(get_person_records_service)],
    search: str | None = Query(default=None, description="Search term across name, title, email, phone, city, company"),
    status_filter: str = Query(default="ALL", alias="status", description="Status filter (ALL, ACTIVE, INACTIVE, DELETED, TEMP, BLACKLIST)"),
    has_email: bool | None = Query(default=None, description="Filter for presence of email"),
    has_phone: bool | None = Query(default=None, description="Filter for presence of phone"),
    has_address: bool | None = Query(default=None, description="Filter for presence of address"),
    has_company: bool | None = Query(default=None, description="Filter for presence of company link"),
    has_owner: bool | None = Query(default=None, description="Filter for presence of assigned contact owner"),
    visitor_contact: int | None = Query(default=None, description="Filter classification: 1=Visitor, 2=Contact"),
    share_contact: int | None = Query(default=None, description="Filter visibility: 0=Private, 1=Public"),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
    sort_by: str = Query(default="PersonID", description="Sort column (PersonID, PersonFirstName, PersonLastName, PersonEntDt)"),
    sort_order: str = Query(default="desc", description="Sort direction (asc, desc)"),
) -> PersonListResponse:
    return await records_service.get_persons_list(
        search=search,
        status=status_filter,
        has_email=has_email,
        has_phone=has_phone,
        has_address=has_address,
        has_company=has_company,
        has_owner=has_owner,
        visitor_contact=visitor_contact,
        share_contact=share_contact,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/PERSON/records/{person_id}",
    response_model=PersonRecordDetailResponse,
    summary="Get single Person entity with all child relations",
    description="Retrieves complete master details, linked addresses, phones, emails, company links, and relationships for a specific PersonID.",
)
async def get_person_record(
    person_id: int,
    records_service: Annotated[PersonRecordsService, Depends(get_person_records_service)],
) -> PersonRecordDetailResponse:
    record = await records_service.get_person_detail(person_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Person entity with PersonID {person_id} was not found.",
        )
    return record


@router.get(
    "/PERSON/contact-quality/rules",
    response_model=list[QualityRuleMeta],
    summary="Get all 37 declarative PERSON contact quality rules",
    description="Returns the canonical declarative rule catalog with metadata, count units, severities, and descriptions.",
)
async def get_contact_quality_rules() -> list[QualityRuleMeta]:
    return list(RULE_METADATA.values())


@router.get(
    "/PERSON/contact-quality",
    response_model=ContactQualitySummaryResponse,
    summary="Get PERSON Contact Quality KPI summary",
    description="Returns aggregate contact quality KPIs including missing, invalid, duplicate, and unverified contacts.",
)
async def get_contact_quality_summary(
    quality_service: Annotated[ContactQualityService, Depends(get_contact_quality_service)],
) -> ContactQualitySummaryResponse:
    return await quality_service.get_contact_quality_summary()


@router.get(
    "/PERSON/contact-quality/issues",
    response_model=ContactQualityIssuesResponse,
    summary="Get paginated PERSON contact quality issues drilldown",
    description="Returns a paginated list of Person records flagged with a specific contact quality issue with privacy masking.",
)
async def get_contact_quality_issues(
    quality_service: Annotated[ContactQualityService, Depends(get_contact_quality_service)],
    issue: str = Query(default="INVALID_EMAIL", description="Issue code (e.g. INVALID_EMAIL, DUPLICATE_EMAIL_CROSS, MISSING_PHONE)"),
    search: str | None = Query(default=None, description="Filter issues by Person name, ID, or value"),
    sort_by: str = Query(default="PersonID", description="Sort column (PersonID, PersonName, CurrentValue)"),
    sort_order: str = Query(default="desc", description="Sort direction (asc, desc)"),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
) -> ContactQualityIssuesResponse:
    return await quality_service.get_contact_quality_issues(
        issue=issue,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/PERSON/contact-quality/export",
    summary="Export PERSON contact quality issue records",
    description="Exports all matching records for a quality issue as CSV or Excel (.xlsx) with PersonID and context.",
)
async def export_contact_quality_issues(
    quality_service: Annotated[ContactQualityService, Depends(get_contact_quality_service)],
    issue: str = Query(default="INVALID_EMAIL", description="Issue code to export"),
    format: str = Query(default="xlsx", description="File format: 'xlsx' or 'csv'"),
    search: str | None = Query(default=None, description="Search filter term"),
    sort_by: str = Query(default="PersonID", description="Sort column"),
    sort_order: str = Query(default="desc", description="Sort direction"),
) -> Response:
    content, media_type, filename = await quality_service.export_contact_quality_issues(
        issue=issue,
        format=format,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/PERSON/contact-quality/summary/export",
    summary="Export PERSON contact quality 37-KPI summary report",
    description="Exports the comprehensive 37-KPI quality assessment report as CSV or Excel (.xlsx).",
)
async def export_contact_quality_summary(
    quality_service: Annotated[ContactQualityService, Depends(get_contact_quality_service)],
    format: str = Query(default="xlsx", description="File format: 'xlsx' or 'csv'"),
) -> Response:
    content, media_type, filename = await quality_service.export_contact_quality_summary(
        format=format,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/{module_code}",
    response_model=ModuleDefinition,
    summary="Get module definition",
    description="Retrieves the detailed configuration and table mappings for a specific module code.",
)
async def get_module(
    module_code: str,
    registry: Annotated[ModuleRegistry, Depends(get_module_registry)],
) -> ModuleDefinition:
    module = registry.get(module_code)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with code '{module_code.upper()}' was not found in registry.",
        )
    return module


@router.get(
    "/{module_code}/validate",
    response_model=ModuleValidationResult,
    summary="Validate module table structure",
    description="Checks the database catalog against the expected table definitions for the module.",
)
async def validate_module(
    module_code: str,
    registry: Annotated[ModuleRegistry, Depends(get_module_registry)],
    analyzer: Annotated[ModuleAnalyzer, Depends(get_module_analyzer)],
) -> ModuleValidationResult:
    module = registry.get(module_code)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with code '{module_code.upper()}' was not found in registry.",
        )
    return await analyzer.validate(module)
