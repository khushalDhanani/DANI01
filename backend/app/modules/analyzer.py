import logging
import time
from typing import Any

from app.analysis.table_analyzer import TableAnalyzer
from app.classification.classifier import TableClassifier
from app.core.exceptions import TableNotFoundError
from app.discovery.metadata import MetadataDiscovery
from app.modules.base import BaseModuleAnalyzer
from app.modules.models import (
    ModuleAnalysisContext,
    ModuleAnalysisResult,
    ModuleDefinition,
    ModuleTableRole,
    ModuleTableValidation,
    ModuleValidationItem,
    ModuleValidationResult,
    ModuleValidationStatus,
)
from app.profiling.profiler import TableProfiler
from app.sampling.sampler import TableSampler

logger = logging.getLogger(__name__)


class ModuleAnalyzer(BaseModuleAnalyzer):
    """
    Generic module analysis orchestrator.
    Validates module definitions against MSSQL catalog metadata,
    and resolves structural, profiling, and semantic contexts across module tables.
    """

    def __init__(
        self,
        discovery: MetadataDiscovery | None = None,
        sampler: TableSampler | None = None,
        profiler: TableProfiler | None = None,
        classifier: TableClassifier | None = None,
        table_analyzer: TableAnalyzer | None = None,
    ) -> None:
        self.discovery = discovery or MetadataDiscovery()
        self.sampler = sampler or TableSampler()
        self.profiler = profiler or TableProfiler()
        self.classifier = classifier or TableClassifier()
        self.table_analyzer = table_analyzer or TableAnalyzer(
            discovery=self.discovery,
            sampler=self.sampler,
            profiler=self.profiler,
            classifier=self.classifier,
        )

    async def validate(self, definition: ModuleDefinition) -> ModuleValidationResult:
        """
        Validates module definition against database discovery metadata without
        querying business data rows.
        """
        items: list[ModuleValidationItem] = []
        validation_errors: list[str] = []
        validation_warnings: list[str] = []
        table_validations: list[ModuleTableValidation] = []

        # 1. Validate Root Table
        root_schema = definition.root_schema
        root_table = definition.root_table
        root_table_exists = False
        root_key_exists = False

        try:
            root_structure = self.discovery.get_table_structure(root_schema, root_table)
            root_table_exists = True
            root_cols = {c.name.lower() for c in root_structure.columns}

            # Check root key
            if definition.root_key.lower() in root_cols:
                root_key_exists = True
            else:
                err = f"Root key '{definition.root_key}' not found in root table '{root_schema}.{root_table}'"
                validation_errors.append(err)
                items.append(ModuleValidationItem(level="ERROR", target="root_key", message=err))
        except (TableNotFoundError, Exception) as e:
            err = f"Root table '{root_schema}.{root_table}' does not exist in catalog: {str(e)}"
            validation_errors.append(err)
            items.append(ModuleValidationItem(level="ERROR", target="root_table", message=err))

        # 2. Validate All Configured Tables
        tables_configured = len(definition.tables)
        tables_found = 0
        tables_missing = 0

        # Ensure root table is represented in table validations if not explicitly listed
        has_explicit_root = any(
            t.table_name.lower() == root_table.lower() and t.schema_name.lower() == root_schema.lower()
            for t in definition.tables
        )

        all_tables_to_check = list(definition.tables)
        if not has_explicit_root:
            from app.modules.models import ModuleTableDefinition
            all_tables_to_check.insert(
                0,
                ModuleTableDefinition(
                    schema=root_schema,
                    table=root_table,
                    role=ModuleTableRole.ROOT,
                    required=True,
                    key_columns=[definition.root_key],
                ),
            )

        for t_def in all_tables_to_check:
            s_name = t_def.schema_name
            t_name = t_def.table_name
            t_required = t_def.required

            try:
                t_struct = self.discovery.get_table_structure(s_name, t_name)
                tables_found += 1
                cols_dict = {c.name.lower(): c.name for c in t_struct.columns}

                found_cols: list[str] = []
                missing_cols: list[str] = []

                # Validate key and important columns
                cols_to_check = set(t_def.key_columns + t_def.important_columns)
                for col in cols_to_check:
                    if col.lower() in cols_dict:
                        found_cols.append(cols_dict[col.lower()])
                    else:
                        missing_cols.append(col)
                        if t_required:
                            err = f"Configured column '{col}' missing from table '{s_name}.{t_name}'"
                            validation_errors.append(err)
                            items.append(
                                ModuleValidationItem(
                                    level="ERROR",
                                    target=f"table:{s_name}.{t_name}:col:{col}",
                                    message=err,
                                )
                            )
                        else:
                            warn = f"Optional column '{col}' missing from optional table '{s_name}.{t_name}'"
                            validation_warnings.append(warn)
                            items.append(
                                ModuleValidationItem(
                                    level="WARNING",
                                    target=f"table:{s_name}.{t_name}:col:{col}",
                                    message=warn,
                                )
                            )

                table_validations.append(
                    ModuleTableValidation(
                        schema=s_name,
                        table=t_name,
                        role=t_def.role,
                        required=t_required,
                        exists=True,
                        estimated_rows=t_struct.table.estimated_rows,
                        column_count=t_struct.table.column_count,
                        found_columns=found_cols,
                        missing_columns=missing_cols,
                    )
                )

            except (TableNotFoundError, Exception):
                tables_missing += 1
                if t_required:
                    err = f"Required module table '{s_name}.{t_name}' not found in catalog"
                    validation_errors.append(err)
                    items.append(
                        ModuleValidationItem(
                            level="ERROR",
                            target=f"table:{s_name}.{t_name}",
                            message=err,
                        )
                    )
                else:
                    warn = f"Optional module table '{s_name}.{t_name}' not found in catalog"
                    validation_warnings.append(warn)
                    items.append(
                        ModuleValidationItem(
                            level="WARNING",
                            target=f"table:{s_name}.{t_name}",
                            message=warn,
                        )
                    )

                table_validations.append(
                    ModuleTableValidation(
                        schema=s_name,
                        table=t_name,
                        role=t_def.role,
                        required=t_required,
                        exists=False,
                        estimated_rows=0,
                        column_count=0,
                        found_columns=[],
                        missing_columns=t_def.key_columns + t_def.important_columns,
                    )
                )

        # 3. Validate Relationships
        for rel in definition.relationships:
            # Check if parent and child exist in validations
            parent_ok = any(
                tv.exists and (tv.table_name.lower() in rel.parent_table.lower() or f"{tv.schema_name}.{tv.table_name}".lower() == rel.parent_table.lower())
                for tv in table_validations
            )
            child_ok = any(
                tv.exists and (tv.table_name.lower() in rel.child_table.lower() or f"{tv.schema_name}.{tv.table_name}".lower() == rel.child_table.lower())
                for tv in table_validations
            )

            if not parent_ok or not child_ok:
                msg = f"Relationship {rel.parent_table}.{rel.parent_key} -> {rel.child_table}.{rel.child_key} is degraded: entity missing"
                if rel.required:
                    validation_errors.append(msg)
                    items.append(ModuleValidationItem(level="ERROR", target=f"rel:{rel.parent_table}->{rel.child_table}", message=msg))
                else:
                    validation_warnings.append(msg)
                    items.append(ModuleValidationItem(level="WARNING", target=f"rel:{rel.parent_table}->{rel.child_table}", message=msg))

        # 4. Determine Overall Status
        if not root_table_exists or not root_key_exists or len(validation_errors) > 0:
            status = ModuleValidationStatus.INVALID
            is_valid = False
        elif len(validation_warnings) > 0 or tables_missing > 0:
            status = ModuleValidationStatus.DEGRADED
            is_valid = True
        else:
            status = ModuleValidationStatus.READY
            is_valid = True

        return ModuleValidationResult(
            code=definition.code,
            name=definition.name,
            status=status,
            is_valid=is_valid,
            root_table=f"{root_schema}.{root_table}",
            root_table_exists=root_table_exists,
            root_key_exists=root_key_exists,
            tables_configured=tables_configured,
            tables_found=tables_found,
            tables_missing=tables_missing,
            table_validations=table_validations,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings,
            items=items,
        )

    async def build_context(
        self, definition: ModuleDefinition, sample_size: int = 1000
    ) -> ModuleAnalysisContext:
        """
        Builds the ModuleAnalysisContext by resolving structure, profile,
        and classification data for all found module tables.
        """
        validation = await self.validate(definition)

        table_structures: dict[str, Any] = {}
        table_profiles: dict[str, Any] = {}
        table_classifications: dict[str, Any] = {}

        # Resolve context for all valid and existing tables
        for tv in validation.table_validations:
            if not tv.exists:
                continue

            full_key = f"{tv.schema_name}.{tv.table_name}"
            try:
                struct = self.discovery.get_table_structure(tv.schema_name, tv.table_name)
                table_structures[full_key] = struct.model_dump()
            except Exception as e:
                logger.warning(f"Could not load structure for {full_key}: {e}")

            try:
                # Reuse TableAnalyzer for sampling + profiling + classification
                t_analysis = await self.table_analyzer.analyze_table(
                    schema_name=tv.schema_name,
                    table_name=tv.table_name,
                    sample_size=sample_size,
                )
                if t_analysis.profile:
                    table_profiles[full_key] = t_analysis.profile.model_dump()
                if t_analysis.classification:
                    table_classifications[full_key] = t_analysis.classification.model_dump()
            except Exception as e:
                logger.warning(f"Could not profile/classify {full_key}: {e}")

        return ModuleAnalysisContext(
            definition=definition,
            validation=validation,
            table_structures=table_structures,
            table_profiles=table_profiles,
            table_classifications=table_classifications,
        )

    async def analyze(
        self, definition: ModuleDefinition, sample_size: int = 1000
    ) -> ModuleAnalysisResult:
        """
        Executes framework-level module analysis.
        Collects context and produces a structured ModuleAnalysisResult.
        """
        start_time = time.perf_counter()
        context = await self.build_context(definition, sample_size=sample_size)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Summarize tables
        table_summaries: list[dict[str, Any]] = []
        for tv in context.validation.table_validations:
            full_key = f"{tv.schema_name}.{tv.table_name}"
            table_summaries.append(
                {
                    "schema": tv.schema_name,
                    "table": tv.table_name,
                    "role": tv.role,
                    "exists": tv.exists,
                    "estimated_rows": tv.estimated_rows,
                    "column_count": tv.column_count,
                    "has_profile": full_key in context.table_profiles,
                    "has_classification": full_key in context.table_classifications,
                }
            )

        return ModuleAnalysisResult(
            code=definition.code,
            name=definition.name,
            status=context.validation.status,
            validation=context.validation,
            tables_analyzed=len(context.table_structures),
            duration_ms=round(duration_ms, 2),
            table_summaries=table_summaries,
        )
