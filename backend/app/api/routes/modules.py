import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.dependencies import (
    get_attendance_service,
    get_contact_quality_service,
    get_contact_service,
    get_cross_domain_service,
    get_employee_service,
    get_module_analyzer,
    get_module_registry,
    get_organization_service,
    get_payroll_service,
    get_person_analyzer,
    get_person_quality_engine,
    get_person_records_service,
    get_procedure_logic_service,
    get_security_service,
)
from app.modules.analyzer import ModuleAnalyzer
from app.modules.attendance.schemas import (
    AttendanceDataQualityResponse,
    AttendanceDirectoryResponse,
    AttendanceOrgHierarchyResponse,
    AttendanceOverviewResponse,
    AttendanceQualityIssuesListResponse,
    DepartmentDetailResponse,
    EmployeeLifetimeAttendanceResponse,
    LeaveApplicationsListResponse,
    LeaveBalancesListResponse,
    LeaveOverviewResponse,
)
from app.modules.attendance.service import AttendanceService
from app.modules.contact.schemas import (
    ContactDataQualityResponse,
    ContactDirectoryListResponse,
    ContactOverviewResponse,
    ContactQualityIssuesListResponse,
)
from app.modules.contact.service import ContactService
from app.modules.employee.cross_domain_schemas import (
    CrossDomainIssuesListResponse,
    CrossDomainOverviewResponse,
)
from app.modules.employee.cross_domain_service import CrossDomainQualityService
from app.modules.employee.schemas import (
    EmployeeDataQualityResponse,
    EmployeeDetailResponse,
    EmployeeListResponse,
    EmployeeOverviewResponse,
    EmployeeStructureResponse,
    QualityIssuesListResponse,
)
from app.modules.employee.service import EmployeeService
from app.modules.models import ModuleDefinition, ModuleInfo, ModuleValidationResult
from app.modules.organization.schemas import (
    OrgDataQualityResponse,
    OrgHierarchyResponse,
    OrgOverviewResponse,
    OrgQualityIssuesListResponse,
    OrgReportingTreeResponse,
    OrgUnitListResponse,
    OrgUnitType,
)
from app.modules.organization.service import OrganizationService
from app.modules.payroll.payroll_service import PayrollService
from app.modules.payroll.schemas import (
    EmployeePayrollHistoryResponse,
    PayrollDataQualityResponse,
    PayrollMetadataResponse,
    PayrollOverviewResponse,
    PayrollQualityIssuesListResponse,
    PayrollRegisterListResponse,
)
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
from app.modules.procedure_logic.procedure_logic_schemas import (
    LogicInconsistenciesListResponse,
    ProcedureLogicOverviewResponse,
    SqlObjectDetailResponse,
    SqlObjectListResponse,
)
from app.modules.procedure_logic.procedure_logic_service import ProcedureLogicService
from app.modules.registry import ModuleRegistry
from app.modules.security.schemas import (
    SecurityDataQualityResponse,
    SecurityOverviewResponse,
    SecurityQualityIssuesListResponse,
    SecurityRoleDetailResponse,
    SecurityRoleListResponse,
    SecurityUserListResponse,
)
from app.modules.security.service import SecurityService

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
    search: str | None = Query(
        default=None, description="Search term across name, title, email, phone, city, company"
    ),
    status_filter: str = Query(
        default="ALL",
        alias="status",
        description="Status filter (ALL, ACTIVE, INACTIVE, DELETED, TEMP, BLACKLIST)",
    ),
    has_email: bool | None = Query(default=None, description="Filter for presence of email"),
    has_phone: bool | None = Query(default=None, description="Filter for presence of phone"),
    has_address: bool | None = Query(default=None, description="Filter for presence of address"),
    has_company: bool | None = Query(
        default=None, description="Filter for presence of company link"
    ),
    has_owner: bool | None = Query(
        default=None, description="Filter for presence of assigned contact owner"
    ),
    visitor_contact: int | None = Query(
        default=None, description="Filter classification: 1=Visitor, 2=Contact"
    ),
    share_contact: int | None = Query(
        default=None, description="Filter visibility: 0=Private, 1=Public"
    ),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
    sort_by: str = Query(
        default="PersonID",
        description="Sort column (PersonID, PersonFirstName, PersonLastName, PersonEntDt)",
    ),
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
    issue: str = Query(
        default="INVALID_EMAIL",
        description="Issue code (e.g. INVALID_EMAIL, DUPLICATE_EMAIL_CROSS, MISSING_PHONE)",
    ),
    search: str | None = Query(
        default=None, description="Filter issues by Person name, ID, or value"
    ),
    sort_by: str = Query(
        default="PersonID", description="Sort column (PersonID, PersonName, CurrentValue)"
    ),
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


# ══════════════════════════════════════════════════════════════════════════════════
# EMPLOYEE MODULE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════════


@router.get(
    "/EMPLOYEE/overview",
    response_model=EmployeeOverviewResponse,
    summary="Get EMPLOYEE workforce overview metrics",
    description="Calculates and returns live headcount, active/inactive/resigned status breakdown, and demographic distributions.",
)
async def get_employee_overview(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    comp_id: int | None = Query(default=None, description="Filter by company ID"),
) -> EmployeeOverviewResponse:
    return await employee_service.get_employee_overview(comp_id=comp_id)


@router.get(
    "/EMPLOYEE/structure",
    response_model=EmployeeStructureResponse,
    summary="Get EMPLOYEE data graph and table structures",
    description="Returns the complete master-detail relationships, lookup tables, and confidence ratings for the Employee domain.",
)
async def get_employee_structure(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> EmployeeStructureResponse:
    return await employee_service.get_employee_structure()


@router.get(
    "/EMPLOYEE/quality",
    response_model=EmployeeDataQualityResponse,
    summary="Get EMPLOYEE data quality assessment",
    description="Evaluates all critical, warning, and informational data quality rules across the employee database.",
)
async def get_employee_quality(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> EmployeeDataQualityResponse:
    return await employee_service.get_employee_quality()


@router.get(
    "/EMPLOYEE/quality/issues",
    response_model=QualityIssuesListResponse,
    summary="Get paginated EMPLOYEE quality issue records",
    description="Drilldown into specific employee records flagged with a quality issue code.",
)
async def get_employee_quality_issues(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    issue: str = Query(
        default="DUP_EMP_CODE",
        description="Issue rule code (e.g. DUP_EMP_CODE, ACTIVE_PAST_RESIGN, MISSING_OFFICIAL_RECORD, MISSING_EMAIL)",
    ),
    search: str | None = Query(default=None, description="Search by name, code, or email"),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
) -> QualityIssuesListResponse:
    return await employee_service.get_quality_issues_drilldown(
        issue_code=issue,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/EMPLOYEE/quality/export",
    summary="Export EMPLOYEE quality issue records",
    description="Exports flagged quality issue records as CSV.",
)
async def export_employee_quality_issues(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    issue: str = Query(default="DUP_EMP_CODE", description="Issue rule code to export"),
    format: str = Query(default="csv", description="File format ('csv')"),
    search: str | None = Query(default=None, description="Search filter term"),
) -> Response:
    content, media_type, filename = await employee_service.export_quality_issues(
        issue_code=issue,
        format=format,
        search=search,
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
    "/EMPLOYEE/records",
    response_model=EmployeeListResponse,
    summary="List paginated Employee records",
    description="Returns a paginated list of employees with current position, department, managers, and status.",
)
async def get_employee_records(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    search: str | None = Query(default=None, description="Search term across name, code, email"),
    status_filter: str = Query(
        default="ACTIVE",
        alias="status",
        description="Status filter (ACTIVE, INACTIVE, RESIGNED, DELETED, ALL)",
    ),
    dept_id: int | None = Query(default=None, description="Filter by department ID"),
    desig_id: int | None = Query(default=None, description="Filter by designation ID"),
    loc_id: int | None = Query(default=None, description="Filter by location ID"),
    comp_id: int | None = Query(default=None, description="Filter by company ID"),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
    sort_by: str = Query(default="EmpID", description="Sort column"),
    sort_order: str = Query(default="asc", description="Sort direction (asc, desc)"),
) -> EmployeeListResponse:
    return await employee_service.get_employee_records(
        search=search,
        status_filter=status_filter,
        dept_id=dept_id,
        desig_id=desig_id,
        loc_id=loc_id,
        comp_id=comp_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )



@router.get(
    "/EMPLOYEE/records/export",
    summary="Export EMPLOYEE roster records",
    description="Exports matching employee records as CSV.",
)
async def export_employee_records(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    status_filter: str = Query(default="ACTIVE", alias="status", description="Status filter"),
    search: str | None = Query(default=None, description="Search filter"),
    format: str = Query(default="csv", description="File format ('csv')"),
) -> Response:
    content, media_type, filename = await employee_service.export_employee_records(
        format=format,
        status_filter=status_filter,
        search=search,
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
    "/EMPLOYEE/records/{emp_id}",
    response_model=EmployeeDetailResponse,
    summary="Get 360° Employee Detail dossier",
    description="Retrieves complete personal profile, official posting history, reporting hierarchy, family, and qualifications for an EmpID.",
)
async def get_employee_record_detail(
    emp_id: int,
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> EmployeeDetailResponse:
    record = await employee_service.get_employee_detail(emp_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with EmpID {emp_id} was not found.",
        )
    return record


# ══════════════════════════════════════════════════════════════════════════════
# ORGANIZATION MODULE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════


@router.get(
    "/ORGANIZATION/overview",
    response_model=OrgOverviewResponse,
    summary="Get ORGANIZATION scale & headcount overview",
    description="Returns live scale counts across corporate companies, locations, divisions, departments, designations, and grades.",
)
async def get_org_overview(
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrgOverviewResponse:
    return await organization_service.get_org_overview()


@router.get(
    "/ORGANIZATION/hierarchy",
    response_model=OrgHierarchyResponse,
    summary="Get ORGANIZATION multi-tier hierarchy tree",
    description="Returns full Company -> Location -> Department -> Designation recursive tree with employee headcounts and leadership mappings.",
)
async def get_org_hierarchy(
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrgHierarchyResponse:
    return await organization_service.get_org_hierarchy_map()


@router.get(
    "/ORGANIZATION/units",
    response_model=OrgUnitListResponse,
    summary="Get unified organizational units catalog",
    description="Retrieves a paginated list of organizational units (Companies, Locations, Main Depts, Depts, Designations, Grades) with HOD and Site Head details.",
)
async def get_org_units(
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    unit_type: OrgUnitType | None = Query(default=None, description="Filter by unit type"),
    search: str | None = Query(default=None, description="Search by unit name, code, or parent"),
    comp_id: int | None = Query(default=None, description="Filter by company ID"),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
) -> OrgUnitListResponse:
    return await organization_service.get_org_units(
        unit_type=unit_type,
        search=search,
        comp_id=comp_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/ORGANIZATION/units/export",
    summary="Export organizational units catalog",
    description="Exports matching organizational units to CSV.",
)
async def export_org_units(
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    unit_type: OrgUnitType | None = Query(default=None, description="Filter by unit type"),
    search: str | None = Query(default=None, description="Search filter"),
    format: str = Query(default="csv", description="File format ('csv')"),
) -> Response:
    content, media_type, filename = await organization_service.export_org_units(
        unit_type=unit_type,
        search=search,
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
    "/ORGANIZATION/reporting",
    response_model=OrgReportingTreeResponse,
    summary="Get executive reporting hierarchy tree",
    description="Returns leadership hierarchy tree starting from MD and Directors down to functional team leads and members.",
)
async def get_org_reporting_tree(
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrgReportingTreeResponse:
    return await organization_service.get_reporting_hierarchy()


@router.get(
    "/ORGANIZATION/quality",
    response_model=OrgDataQualityResponse,
    summary="Get ORGANIZATION data quality audit",
    description="Evaluates 14 data quality rules across companies, locations, departments, designations, and position mappings.",
)
async def get_org_quality(
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrgDataQualityResponse:
    return await organization_service.get_org_quality()


@router.get(
    "/ORGANIZATION/quality/issues",
    response_model=OrgQualityIssuesListResponse,
    summary="Get paginated ORGANIZATION quality issue records",
    description="Drilldown into specific organization units or employee records flagged with a quality issue code.",
)
async def get_org_quality_issues(
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    issue: str = Query(
        default="MISSING_OFFICIAL_RECORD",
        description="Issue rule code (e.g. MISSING_OFFICIAL_RECORD, MULTIPLE_ACTIVE_POSITIONS, EMPTY_LOCATIONS, EMPTY_DEPARTMENTS)",
    ),
    search: str | None = Query(default=None, description="Search filter"),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
) -> OrgQualityIssuesListResponse:
    return await organization_service.get_org_quality_issues(
        issue_code=issue,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/ORGANIZATION/quality/export",
    summary="Export ORGANIZATION quality issue records",
    description="Exports flagged quality issue records as CSV.",
)
async def export_org_quality_issues(
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    issue: str = Query(default="MISSING_OFFICIAL_RECORD", description="Issue rule code to export"),
    format: str = Query(default="csv", description="File format ('csv')"),
    search: str | None = Query(default=None, description="Search filter term"),
) -> Response:
    content, media_type, filename = await organization_service.export_org_quality_issues(
        issue_code=issue,
        search=search,
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


# ══════════════════════════════════════════════════════════════════════════════
# CONTACT & COMMUNICATION INTELLIGENCE MODULE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════


@router.get(
    "/CONTACT/overview",
    response_model=ContactOverviewResponse,
    summary="Get workforce contact overview metrics",
    description="Returns aggregate metrics on company emails, personal emails, phones, postal addresses, and domain distribution.",
)
async def get_contact_overview(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
) -> ContactOverviewResponse:
    return await contact_service.get_contact_overview()


@router.get(
    "/CONTACT/directory",
    response_model=ContactDirectoryListResponse,
    summary="Get workforce contact directory",
    description="Returns paginated workforce roster with communication channels and verification flags.",
)
async def get_contact_directory(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    email_filter: str | None = Query(
        default=None,
        description="Filter: 'WITH_COMPANY_EMAIL', 'WITH_PERSONAL_EMAIL', 'WITHOUT_ANY_EMAIL', 'WITH_ANY_EMAIL'",
    ),
    phone_filter: str | None = Query(
        default=None,
        description="Filter: 'WITH_PRIMARY_PHONE', 'MISSING_PRIMARY_PHONE', 'UNVERIFIED_PHONE', 'WITH_ICE_CONTACT'",
    ),
    search: str | None = Query(
        default=None, description="Search term across name, code, emails, phone"
    ),
    limit: int = Query(default=25, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> ContactDirectoryListResponse:
    return await contact_service.get_contact_directory(
        email_filter=email_filter,
        phone_filter=phone_filter,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/CONTACT/directory/export",
    summary="Export contact directory",
    description="Exports filtered contact directory as CSV.",
)
async def export_contact_directory(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    email_filter: str | None = Query(
        default=None,
        description="Filter: 'WITH_COMPANY_EMAIL', 'WITH_PERSONAL_EMAIL', 'WITHOUT_ANY_EMAIL'",
    ),
    phone_filter: str | None = Query(
        default=None,
        description="Filter: 'WITH_PRIMARY_PHONE', 'MISSING_PRIMARY_PHONE', 'UNVERIFIED_PHONE'",
    ),
    search: str | None = Query(default=None, description="Search term"),
    format: str = Query(default="csv", description="File format ('csv')"),
) -> Response:
    content, media_type, filename = await contact_service.export_contact_directory(
        email_filter=email_filter,
        phone_filter=phone_filter,
        search=search,
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
    "/CONTACT/quality",
    response_model=ContactDataQualityResponse,
    summary="Get contact & email data quality audit",
    description="Evaluates 16 communication data-quality rules across the workforce.",
)
async def get_contact_quality(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
) -> ContactDataQualityResponse:
    return await contact_service.get_contact_quality()


@router.get(
    "/CONTACT/quality/issues",
    response_model=ContactQualityIssuesListResponse,
    summary="Get contact quality issue drilldown records",
    description="Returns paginated records flagged by a specific contact quality rule.",
)
async def get_workforce_contact_quality_issues(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    issue: str = Query(default="MISSING_ALL_PHONES", description="Issue rule code"),
    search: str | None = Query(default=None, description="Search term"),
    limit: int = Query(default=25, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> ContactQualityIssuesListResponse:
    return await contact_service.get_contact_quality_issues(
        issue_code=issue,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/CONTACT/quality/export",
    summary="Export contact quality issue records",
    description="Exports flagged contact quality records as CSV.",
)
async def export_workforce_contact_quality_issues(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    issue: str = Query(default="MISSING_ALL_PHONES", description="Issue rule code to export"),
    format: str = Query(default="csv", description="File format ('csv')"),
    search: str | None = Query(default=None, description="Search filter term"),
) -> Response:
    content, media_type, filename = await contact_service.export_contact_quality_issues(
        issue_code=issue,
        search=search,
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


# ══════════════════════════════════════════════════════════════════════════════
# USER / LOGIN & SECURITY INTELLIGENCE MODULE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════


@router.get(
    "/SECURITY/overview",
    response_model=SecurityOverviewResponse,
    summary="Get user and security overview metrics",
    description="Returns aggregate metrics on user accounts, employee mapping, security posture (MFA, Admins, Devices), and role distribution.",
)
async def get_security_overview(
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> SecurityOverviewResponse:
    return await security_service.get_security_overview()


@router.get(
    "/SECURITY/users",
    response_model=SecurityUserListResponse,
    summary="Get user accounts directory",
    description="Returns paginated user login accounts with role, employee link status, admin privileges, and registered device counts.",
)
async def get_security_users(
    security_service: Annotated[SecurityService, Depends(get_security_service)],
    role_id: int | None = Query(default=None, description="Filter by Role ID"),
    status_filter: str | None = Query(
        default=None,
        description="Filter: 'ACTIVE', 'INACTIVE', 'DELETED', 'ADMIN', 'MFA', 'LINKED', 'UNLINKED'",
    ),
    search: str | None = Query(
        default=None, description="Search across username, email, mobile, emp code, emp name"
    ),
    limit: int = Query(default=25, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> SecurityUserListResponse:
    return await security_service.get_user_directory(
        role_id=role_id,
        status_filter=status_filter,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/SECURITY/users/export",
    summary="Export user accounts directory to CSV",
    description="Streams a CSV export of user accounts with role, employee linkage, and security flags.",
)
async def export_security_users(
    security_service: Annotated[SecurityService, Depends(get_security_service)],
    role_id: int | None = Query(default=None, description="Filter by Role ID"),
    status_filter: str | None = Query(default=None, description="Status filter"),
    search: str | None = Query(default=None, description="Search term"),
) -> Response:
    content = await security_service.export_user_directory(
        role_id=role_id,
        status_filter=status_filter,
        search=search,
    )
    filename = f"user_security_directory_{status_filter.lower() if status_filter else 'all'}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/SECURITY/roles",
    response_model=SecurityRoleListResponse,
    summary="Get security roles catalog",
    description="Returns security roles with assigned user counts and CRUD permission totals across system menus.",
)
async def get_security_roles(
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> SecurityRoleListResponse:
    return await security_service.get_roles_catalog()


@router.get(
    "/SECURITY/roles/{role_id}/permissions",
    response_model=SecurityRoleDetailResponse,
    summary="Get role permission matrix",
    description="Returns menu-by-menu granular CRUD permissions (Insert, Update, Delete, View) for a specific security role.",
)
async def get_security_role_permissions(
    role_id: int,
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> SecurityRoleDetailResponse:
    return await security_service.get_role_permissions(role_id=role_id)


@router.get(
    "/SECURITY/quality",
    response_model=SecurityDataQualityResponse,
    summary="Get security & access data quality audit",
    description="Evaluates 14 SSoT security rules (broken employee references, inactive employee access risks, duplicate accounts, missing roles, unverified logins).",
)
async def get_security_quality(
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> SecurityDataQualityResponse:
    return await security_service.get_security_quality()


@router.get(
    "/SECURITY/quality/issues",
    response_model=SecurityQualityIssuesListResponse,
    summary="Drilldown specific security quality rule issues",
    description="Returns paginated records violating a specific security or data quality rule.",
)
async def get_security_quality_issues(
    security_service: Annotated[SecurityService, Depends(get_security_service)],
    issue: str = Query(description="Security rule code (e.g. 'ACTIVE_USER_INACTIVE_EMP')"),
    search: str | None = Query(default=None, description="Search filter term"),
    limit: int = Query(default=25, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> SecurityQualityIssuesListResponse:
    return await security_service.get_security_quality_issues(
        issue_code=issue,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/SECURITY/quality/export",
    summary="Export security quality issues to CSV",
    description="Streams a CSV export of records violating a specific security rule.",
)
async def export_security_quality_issues(
    security_service: Annotated[SecurityService, Depends(get_security_service)],
    issue: str = Query(description="Security rule code (e.g. 'ACTIVE_USER_INACTIVE_EMP')"),
    search: str | None = Query(default=None, description="Search filter term"),
) -> Response:
    content = await security_service.export_security_quality_issues(
        issue_code=issue,
        search=search,
    )
    filename = f"security_issue_{issue.lower()}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


# ══════════════════════════════════════════════════════════════════════════════
# ATTENDANCE & LEAVE MODULE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════


@router.get(
    "/ATTENDANCE/overview",
    response_model=AttendanceOverviewResponse,
    summary="Get ATTENDANCE overview metrics",
    description="Returns workforce attendance metrics, punch logs, and active shift distributions.",
)
async def get_attendance_overview(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
    dept_id: int | None = Query(default=None, description="Department ID filter"),
    comp_id: int | None = Query(default=None, description="Company ID filter"),
) -> AttendanceOverviewResponse:
    return attendance_service.get_attendance_overview(dept_id=dept_id, comp_id=comp_id)


@router.get(
    "/ATTENDANCE/org-hierarchy",
    response_model=AttendanceOrgHierarchyResponse,
    summary="Get ATTENDANCE organizational hierarchy breakdown",
    description="Returns attendance metrics grouped by Company, Location/Site, and Department.",
)
async def get_attendance_org_hierarchy(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> AttendanceOrgHierarchyResponse:
    return attendance_service.get_attendance_org_hierarchy()


@router.get(
    "/ATTENDANCE/department/{dept_id}",
    response_model=DepartmentDetailResponse,
    summary="Get department-specific attendance & leave summary KPIs",
    description="Returns headcount, attendance volume, present/absent ratios, and active/pending leave counts for a department.",
)
async def get_department_attendance_detail(
    dept_id: int,
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> DepartmentDetailResponse:
    return attendance_service.get_department_attendance_detail(dept_id=dept_id)


@router.get(
    "/ATTENDANCE/directory",
    response_model=AttendanceDirectoryResponse,
    summary="Get paginated ATTENDANCE directory logs",
    description="Returns paginated daily attendance records with status filters and search.",
)
async def get_attendance_directory(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
    status: str | None = Query(
        default=None, description="Status filter (PRESENT, ABSENT, LATE, EARLY, OT, LEAVE)"
    ),
    search: str | None = Query(default=None, description="Search keyword"),
    dept_id: int | None = Query(default=None, description="Department ID filter"),
    comp_id: int | None = Query(default=None, description="Company ID filter"),
    emp_id: int | None = Query(default=None, description="Employee ID filter"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AttendanceDirectoryResponse:
    return attendance_service.get_attendance_directory(
        status_filter=status,
        search=search,
        dept_id=dept_id,
        comp_id=comp_id,
        emp_id=emp_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/ATTENDANCE/directory/export",
    summary="Export ATTENDANCE directory as CSV",
    description="Exports filtered attendance logs as CSV.",
)
async def export_attendance_directory(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
    status: str | None = Query(default=None, description="Status filter"),
    search: str | None = Query(default=None, description="Search keyword"),
) -> Response:
    content = attendance_service.export_attendance_directory(status_filter=status, search=search)
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="attendance_directory.csv"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/ATTENDANCE/leave/overview",
    response_model=LeaveOverviewResponse,
    summary="Get LEAVE overview metrics",
    description="Returns leave request pipelines, status breakdowns, and active staff on leave.",
)
async def get_leave_overview(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> LeaveOverviewResponse:
    return attendance_service.get_leave_overview()


@router.get(
    "/ATTENDANCE/leave/applications",
    response_model=LeaveApplicationsListResponse,
    summary="Get paginated LEAVE applications",
    description="Returns paginated leave applications with status filter and search.",
)
async def get_leave_applications(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
    status: str | None = Query(
        default=None, description="Status filter (APPROVED, PENDING, REJECTED, CANCELLED)"
    ),
    search: str | None = Query(default=None, description="Search keyword"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> LeaveApplicationsListResponse:
    return attendance_service.get_leave_applications(
        status_filter=status,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/ATTENDANCE/leave/applications/export",
    summary="Export LEAVE applications as CSV",
    description="Exports filtered leave applications as CSV.",
)
async def export_leave_applications(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
    status: str | None = Query(default=None, description="Status filter"),
    search: str | None = Query(default=None, description="Search keyword"),
) -> Response:
    content = attendance_service.export_leave_applications(status_filter=status, search=search)
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="leave_applications.csv"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/ATTENDANCE/leave/balances",
    response_model=LeaveBalancesListResponse,
    summary="Get paginated LEAVE balances ledger",
    description="Returns paginated monthly leave balance ledger with net balances.",
)
async def get_leave_balances(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
    year_month: str | None = Query(default=None, description="YearMonth filter (e.g. 202607)"),
    search: str | None = Query(default=None, description="Search keyword"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> LeaveBalancesListResponse:
    return attendance_service.get_leave_balances(
        year_month=year_month,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/ATTENDANCE/quality",
    response_model=AttendanceDataQualityResponse,
    summary="Get ATTENDANCE data quality audit",
    description="Evaluates 14 SSoT data quality rules across attendance, punch logs, shifts, and leave balances.",
)
async def get_attendance_quality(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> AttendanceDataQualityResponse:
    return attendance_service.get_attendance_quality()


@router.get(
    "/ATTENDANCE/quality/issues",
    response_model=AttendanceQualityIssuesListResponse,
    summary="Drilldown ATTENDANCE quality issues",
    description="Returns paginated violating records for a specific quality rule.",
)
async def get_attendance_quality_issues(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
    issue: str = Query(..., description="Issue rule code"),
    search: str | None = Query(default=None, description="Search keyword"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AttendanceQualityIssuesListResponse:
    return attendance_service.get_attendance_quality_issues(
        issue_code=issue,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/ATTENDANCE/quality/issues/export",
    summary="Export ATTENDANCE quality issues as CSV",
    description="Exports drilldown violating records for a specific quality rule as CSV.",
)
async def export_attendance_quality_issues(
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
    issue: str = Query(..., description="Issue rule code"),
    search: str | None = Query(default=None, description="Search keyword"),
) -> Response:
    content = attendance_service.export_attendance_quality_issues(issue_code=issue, search=search)
    filename = f"attendance_issue_{issue.lower()}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/ATTENDANCE/employee/{emp_id}/analytics",
    response_model=EmployeeLifetimeAttendanceResponse,
    summary="Get 360 lifetime attendance & leave analytics for an employee",
    description="Fetches lifetime attendance totals, present/absent days, late/early minutes, OT hours, leave breakdown, and HR risk signals for an employee.",
)
async def get_employee_lifetime_attendance_analytics(
    emp_id: int,
    attendance_service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> EmployeeLifetimeAttendanceResponse:
    return attendance_service.get_employee_lifetime_attendance_analytics(emp_id)


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


# ==============================================================================
# PAYROLL MODULE ROUTES
# ==============================================================================


@router.get(
    "/PAYROLL/metadata",
    response_model=PayrollMetadataResponse,
    summary="Get PAYROLL module metadata",
    description="Returns discovered table schemas and relationship mappings for the Payroll module.",
)
async def get_payroll_metadata(
    payroll_service: Annotated[PayrollService, Depends(get_payroll_service)],
) -> PayrollMetadataResponse:
    return payroll_service.get_payroll_metadata()


@router.get(
    "/PAYROLL/overview",
    response_model=PayrollOverviewResponse,
    summary="Get PAYROLL overview statistics",
    description="Returns high-level payroll KPIs, latest period totals, and monthly trends.",
)
async def get_payroll_overview(
    payroll_service: Annotated[PayrollService, Depends(get_payroll_service)],
    comp_id: int | None = Query(default=None, description="Company ID filter"),
) -> PayrollOverviewResponse:
    return payroll_service.get_payroll_overview(comp_id=comp_id)



@router.get(
    "/PAYROLL/directory",
    response_model=PayrollRegisterListResponse,
    summary="Get PAYROLL monthly register",
    description="Returns paginated list of monthly salary register records.",
)
async def get_payroll_directory(
    payroll_service: Annotated[PayrollService, Depends(get_payroll_service)],
    status: str | None = Query(
        default=None, description="Status filter (CORRUPTED, NEGATIVE, ACTIVE)"
    ),
    search: str | None = Query(default=None, description="Search keyword"),
    dept_id: int | None = Query(default=None, description="Department ID filter"),
    comp_id: int | None = Query(default=None, description="Company ID filter"),
    month: str | None = Query(default=None, description="Salary month filter (e.g. 202606)"),
    emp_id: int | None = Query(default=None, description="Employee ID filter"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PayrollRegisterListResponse:
    return payroll_service.get_payroll_directory(
        status_filter=status,
        search=search,
        dept_id=dept_id,
        comp_id=comp_id,
        month=month,
        emp_id=emp_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/PAYROLL/directory/export",
    summary="Export PAYROLL directory as CSV",
    description="Exports filtered monthly salary register records as CSV.",
)
async def export_payroll_directory(
    payroll_service: Annotated[PayrollService, Depends(get_payroll_service)],
    status: str | None = Query(default=None, description="Status filter"),
    search: str | None = Query(default=None, description="Search keyword"),
) -> Response:
    content = payroll_service.export_payroll_directory(status_filter=status, search=search)
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="payroll_directory.csv"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/PAYROLL/quality",
    response_model=PayrollDataQualityResponse,
    summary="Get PAYROLL data quality audit",
    description="Returns data quality rules and health score for Payroll data.",
)
async def get_payroll_quality(
    payroll_service: Annotated[PayrollService, Depends(get_payroll_service)],
) -> PayrollDataQualityResponse:
    return payroll_service.get_payroll_quality()


@router.get(
    "/PAYROLL/quality/issues",
    response_model=PayrollQualityIssuesListResponse,
    summary="Get PAYROLL data quality issue records",
    description="Returns paginated violating records for a specific payroll data quality rule.",
)
async def get_payroll_quality_issues(
    payroll_service: Annotated[PayrollService, Depends(get_payroll_service)],
    issue: str = Query(default="CORRUPTED_NET_PAY", description="Quality rule code"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PayrollQualityIssuesListResponse:
    return payroll_service.get_payroll_quality_issues(issue_code=issue, limit=limit, offset=offset)


@router.get(
    "/PAYROLL/quality/export",
    summary="Export PAYROLL data quality issues as CSV",
    description="Exports violating payroll records as CSV.",
)
async def export_payroll_quality_issues(
    payroll_service: Annotated[PayrollService, Depends(get_payroll_service)],
    issue: str = Query(default="CORRUPTED_NET_PAY", description="Quality rule code to export"),
) -> Response:
    content = payroll_service.export_payroll_quality_issues(issue_code=issue)
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="payroll_issues_{issue.lower()}.csv"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/PAYROLL/employee/{emp_id}/history",
    response_model=EmployeePayrollHistoryResponse,
    summary="Get employee lifetime salary & payslip history",
    description="Returns complete career payslip history for an employee.",
)
async def get_employee_payroll_history(
    emp_id: int,
    payroll_service: Annotated[PayrollService, Depends(get_payroll_service)],
) -> EmployeePayrollHistoryResponse:
    return payroll_service.get_employee_payroll_history(emp_id=emp_id)


# ── CROSS-DOMAIN EMPLOYEE DATA QUALITY ENDPOINTS ─────────────────────────


@router.get(
    "/CROSS_DOMAIN_DQ/overview",
    response_model=CrossDomainOverviewResponse,
    summary="Get cross-domain employee data quality overview",
    description="Returns cross-domain quality health score, severity breakdown, category summaries, and rule matrix.",
)
async def get_cross_domain_overview(
    cd_service: Annotated[CrossDomainQualityService, Depends(get_cross_domain_service)],
    comp_id: int | None = Query(default=None, description="Company ID filter"),
) -> CrossDomainOverviewResponse:
    return cd_service.get_cross_domain_overview(comp_id=comp_id)


@router.get(
    "/CROSS_DOMAIN_DQ/issues",
    response_model=CrossDomainIssuesListResponse,
    summary="Get cross-domain quality evidence issues list",
    description="Returns paginated evidence records for cross-domain rule failures.",
)
async def get_cross_domain_issues(
    cd_service: Annotated[CrossDomainQualityService, Depends(get_cross_domain_service)],
    rule_code: str | None = Query(default=None, description="Rule code filter"),
    category: str | None = Query(default=None, description="Category filter"),
    search: str | None = Query(default=None, description="Search term across employee, detail, or table"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    comp_id: int | None = Query(default=None, description="Company ID filter"),
) -> CrossDomainIssuesListResponse:
    return cd_service.get_cross_domain_issues(
        rule_code=rule_code,
        category=category,
        search=search,
        limit=limit,
        offset=offset,
        comp_id=comp_id,
    )


@router.get(
    "/CROSS_DOMAIN_DQ/export",
    summary="Export cross-domain data quality evidence CSV",
    description="Downloads CSV export of cross-domain rule violation evidence records.",
)
async def export_cross_domain_issues(
    cd_service: Annotated[CrossDomainQualityService, Depends(get_cross_domain_service)],
    rule_code: str | None = Query(default=None, description="Rule code filter"),
    category: str | None = Query(default=None, description="Category filter"),
    search: str | None = Query(default=None, description="Search term"),
    comp_id: int | None = Query(default=None, description="Company ID filter"),
) -> Response:
    csv_bytes = cd_service.download_cross_domain_export(
        rule_code=rule_code,
        category=category,
        search=search,
        comp_id=comp_id,
    )
    filename = f"cross_domain_dq_{(rule_code or category or 'all').lower()}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


# ── STORED PROCEDURE & BUSINESS LOGIC ANALYZER ENDPOINTS ─────────────────


@router.get(
    "/PROCEDURE_LOGIC/overview",
    response_model=ProcedureLogicOverviewResponse,
    summary="Get SQL Stored Procedure & Business Logic Overview",
    description="Returns high-level overview metrics, scanned SQL object types, module distribution, and inconsistency counts.",
)
async def get_procedure_logic_overview(
    pl_service: Annotated[ProcedureLogicService, Depends(get_procedure_logic_service)],
) -> ProcedureLogicOverviewResponse:
    return pl_service.get_procedure_logic_overview()


@router.get(
    "/PROCEDURE_LOGIC/objects",
    response_model=SqlObjectListResponse,
    summary="Get paginated SQL objects catalog",
    description="Returns paginated catalog of scanned Stored Procedures, Functions, Views, and Triggers.",
)
async def get_sql_objects_catalog(
    pl_service: Annotated[ProcedureLogicService, Depends(get_procedure_logic_service)],
    object_type: str | None = Query(default=None, description="Object type filter e.g. PROCEDURE, FUNCTION, VIEW, TRIGGER"),
    module: str | None = Query(default=None, description="Workforce module filter"),
    search: str | None = Query(default=None, description="Search term across object name or table"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> SqlObjectListResponse:
    return pl_service.get_sql_objects_catalog(
        object_type=object_type,
        module=module,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/PROCEDURE_LOGIC/inconsistencies",
    response_model=LogicInconsistenciesListResponse,
    summary="Get logic inconsistencies and rule conflicts list",
    description="Returns paginated business logic inconsistencies with affected objects, predicates, differences, and recommendations.",
)
async def get_logic_inconsistencies(
    pl_service: Annotated[ProcedureLogicService, Depends(get_procedure_logic_service)],
    severity: str | None = Query(default=None, description="Severity filter: CRITICAL, WARNING, INFO"),
    rule_code: str | None = Query(default=None, description="Rule concept code filter"),
    search: str | None = Query(default=None, description="Search term"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> LogicInconsistenciesListResponse:
    return pl_service.get_inconsistencies(
        severity=severity,
        rule_code=rule_code,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/PROCEDURE_LOGIC/objects/{object_id}",
    response_model=SqlObjectDetailResponse,
    summary="Get SQL object definition & detail",
    description="Retrieves full SQL definition code and associated inconsistency findings for an object ID.",
)
async def get_sql_object_detail(
    object_id: int,
    pl_service: Annotated[ProcedureLogicService, Depends(get_procedure_logic_service)],
) -> SqlObjectDetailResponse:
    detail = pl_service.get_sql_object_detail(object_id=object_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SQL Object with ID {object_id} was not found.",
        )
    return detail


@router.get(
    "/PROCEDURE_LOGIC/export",
    summary="Export logic inconsistencies CSV",
    description="Downloads CSV export of detected business logic inconsistencies across SQL procedures.",
)
async def export_logic_inconsistencies(
    pl_service: Annotated[ProcedureLogicService, Depends(get_procedure_logic_service)],
    severity: str | None = Query(default=None, description="Severity filter"),
    rule_code: str | None = Query(default=None, description="Rule code filter"),
    search: str | None = Query(default=None, description="Search term"),
) -> Response:
    csv_bytes = pl_service.download_inconsistencies_export(
        severity=severity,
        rule_code=rule_code,
        search=search,
    )
    filename = f"sql_logic_inconsistencies_{(severity or rule_code or 'all').lower()}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )



