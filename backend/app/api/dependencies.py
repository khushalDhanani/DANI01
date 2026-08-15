from typing import Annotated

from fastapi import Depends

from app.analysis.database_analyzer import DatabaseAnalyzer
from app.analysis.planner import AnalysisPlanner
from app.analysis.table_analyzer import TableAnalyzer
from app.classification.classifier import TableClassifier
from app.discovery.metadata import MetadataDiscovery
from app.modules.analyzer import ModuleAnalyzer
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
    table_analyzer: Annotated[TableAnalyzer, Depends(get_table_analyzer)],
) -> ModuleAnalyzer:
    return ModuleAnalyzer(
        discovery=discovery,
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
