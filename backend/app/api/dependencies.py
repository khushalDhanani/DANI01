from typing import Annotated

from fastapi import Depends

from app.analysis.database_analyzer import DatabaseAnalyzer
from app.analysis.planner import AnalysisPlanner
from app.analysis.table_analyzer import TableAnalyzer
from app.classification.classifier import TableClassifier
from app.discovery.metadata import MetadataDiscovery
from app.modules.analyzer import ModuleAnalyzer
from app.modules.contact.analyzer import ContactAnalyzer
from app.modules.contact.service import ContactService
from app.modules.employee.analyzer import EmployeeModuleAnalyzer
from app.modules.employee.service import EmployeeService
from app.modules.organization.analyzer import OrganizationModuleAnalyzer
from app.modules.organization.service import OrganizationService
from app.modules.person.analyzer import PersonModuleAnalyzer
from app.modules.person.contact_quality_service import ContactQualityService
from app.modules.person.metrics import PersonMetricsService
from app.modules.person.quality.engine import PersonQualityEngine
from app.modules.person.quality.registry import (
    person_quality_rule_registry,
)
from app.modules.person.records_service import PersonRecordsService
from app.modules.registry import ModuleRegistry, module_registry
from app.profiling.profiler import TableProfiler
from app.sampling.sampler import TableSampler


def get_discovery_service() -> MetadataDiscovery:
    return MetadataDiscovery()


def get_sampling_service() -> TableSampler:
    return TableSampler()


def get_profiling_service() -> TableProfiler:
    return TableProfiler()


def get_classification_service() -> TableClassifier:
    return TableClassifier()


def get_analysis_planner() -> AnalysisPlanner:
    return AnalysisPlanner()


def get_table_analyzer(
    discovery: Annotated[MetadataDiscovery, Depends(get_discovery_service)],
    sampler: Annotated[TableSampler, Depends(get_sampling_service)],
    profiler: Annotated[TableProfiler, Depends(get_profiling_service)],
    classifier: Annotated[TableClassifier, Depends(get_classification_service)],
) -> TableAnalyzer:
    return TableAnalyzer(
        discovery=discovery,
        sampler=sampler,
        profiler=profiler,
        classifier=classifier,
    )


def get_database_analyzer(
    discovery: Annotated[MetadataDiscovery, Depends(get_discovery_service)],
    planner: Annotated[AnalysisPlanner, Depends(get_analysis_planner)],
    table_analyzer: Annotated[TableAnalyzer, Depends(get_table_analyzer)],
) -> DatabaseAnalyzer:
    return DatabaseAnalyzer(
        discovery=discovery,
        planner=planner,
        table_analyzer=table_analyzer,
    )


def get_module_registry() -> ModuleRegistry:
    return module_registry


def get_module_analyzer(
    discovery: Annotated[MetadataDiscovery, Depends(get_discovery_service)],
    sampler: Annotated[TableSampler, Depends(get_sampling_service)],
    profiler: Annotated[TableProfiler, Depends(get_profiling_service)],
    classifier: Annotated[TableClassifier, Depends(get_classification_service)],
    table_analyzer: Annotated[TableAnalyzer, Depends(get_table_analyzer)],
) -> ModuleAnalyzer:
    return ModuleAnalyzer(
        discovery=discovery,
        sampler=sampler,
        profiler=profiler,
        classifier=classifier,
        table_analyzer=table_analyzer,
    )


def get_person_analyzer(
    discovery: Annotated[MetadataDiscovery, Depends(get_discovery_service)],
    module_analyzer: Annotated[ModuleAnalyzer, Depends(get_module_analyzer)],
) -> PersonModuleAnalyzer:
    metrics_service = PersonMetricsService(discovery=discovery)
    return PersonModuleAnalyzer(
        discovery=discovery,
        module_analyzer=module_analyzer,
        metrics_service=metrics_service,
    )


def get_person_quality_engine(
    discovery: Annotated[MetadataDiscovery, Depends(get_discovery_service)],
) -> PersonQualityEngine:
    return PersonQualityEngine(
        discovery=discovery,
        registry=person_quality_rule_registry,
    )


def get_person_records_service() -> PersonRecordsService:
    return PersonRecordsService()


def get_contact_quality_service() -> ContactQualityService:
    return ContactQualityService()


def get_employee_service() -> EmployeeService:
    return EmployeeService()


def get_employee_analyzer() -> EmployeeModuleAnalyzer:
    return EmployeeModuleAnalyzer()


def get_organization_service() -> OrganizationService:
    return OrganizationService()


def get_organization_analyzer() -> OrganizationModuleAnalyzer:
    return OrganizationModuleAnalyzer()


from app.modules.attendance.analyzer import AttendanceAnalyzer
from app.modules.attendance.service import AttendanceService
from app.modules.security.analyzer import SecurityAnalyzer
from app.modules.security.service import SecurityService


def get_contact_service() -> ContactService:
    return ContactService()


def get_contact_analyzer() -> ContactAnalyzer:
    return ContactAnalyzer()


def get_security_service() -> SecurityService:
    return SecurityService()


def get_security_analyzer() -> SecurityAnalyzer:
    return SecurityAnalyzer()


def get_attendance_service() -> AttendanceService:
    return AttendanceService()


def get_attendance_analyzer(
    service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> AttendanceAnalyzer:
    return AttendanceAnalyzer(service=service)


from app.modules.payroll.payroll_service import PayrollService


def get_payroll_service() -> PayrollService:
    return PayrollService()


from app.modules.employee.cross_domain_service import CrossDomainQualityService


def get_cross_domain_service() -> CrossDomainQualityService:
    return CrossDomainQualityService()


from app.modules.procedure_logic.procedure_logic_service import ProcedureLogicService


def get_procedure_logic_service() -> ProcedureLogicService:
    return ProcedureLogicService()




