import logging

from app.discovery.metadata import MetadataDiscovery
from app.modules.analyzer import ModuleAnalyzer
from app.modules.definitions.person import PersonModuleDefinition
from app.modules.models import ModuleValidationStatus
from app.modules.person.metrics import PersonMetricsService
from app.modules.person.schemas import (
    PersonMetricsSummary,
    PersonModuleMetricsResponse,
)

logger = logging.getLogger(__name__)


class PersonModuleAnalyzer:
    """
    Business-level analyzer for the PERSON module.
    Validates module configuration and executes set-based aggregate domain metrics.
    """

    def __init__(
        self,
        discovery: MetadataDiscovery | None = None,
        module_analyzer: ModuleAnalyzer | None = None,
        metrics_service: PersonMetricsService | None = None,
    ) -> None:
        self.discovery = discovery or MetadataDiscovery()
        self.module_analyzer = module_analyzer or ModuleAnalyzer(discovery=self.discovery)
        self.metrics_service = metrics_service or PersonMetricsService(discovery=self.discovery)

    async def analyze_metrics(self) -> PersonModuleMetricsResponse:
        """
        Validates the PERSON module against the database catalog and calculates
        domain coverage and volume metrics.
        """
        definition = PersonModuleDefinition

        # 1. Run M1 generic validation
        validation = await self.module_analyzer.validate(definition)
        if validation.status == ModuleValidationStatus.INVALID:
            return PersonModuleMetricsResponse(
                module="PERSON",
                status="FAILED",
                root_entity=f"{definition.root_schema}.{definition.root_table}",
                metrics=PersonMetricsSummary(total_persons=0),
                warnings=[
                    f"PERSON module validation failed: {'; '.join(validation.validation_errors)}"
                ],
                duration_ms=0.0,
            )

        # 2. Execute Metrics Calculation
        response = await self.metrics_service.calculate_metrics()

        # Merge validation warnings if any
        if validation.validation_warnings:
            response.warnings.extend(validation.validation_warnings)
            if response.status == "COMPLETED":
                response.status = "DEGRADED"

        return response
