import logging

from app.classification.rules import classify_column_signals
from app.classification.taxonomy import SEMANTIC_SENSITIVITY_MAP, SensitivityLevel
from app.discovery.metadata import MetadataDiscovery
from app.schemas.classification import (
    ColumnClassification,
    TableClassificationResponse,
)

logger = logging.getLogger(__name__)


class TableClassifier:
    def __init__(self, discovery: MetadataDiscovery | None = None):
        self.discovery = discovery or MetadataDiscovery()

    def classify_table(
        self,
        schema_name: str,
        table_name: str,
    ) -> TableClassificationResponse:
        """
        Classifies all columns of a table into semantic types with confidence scores,
        sensitivity/PII ratings, and signal traces.
        """
        columns = self.discovery.get_columns(schema_name, table_name)
        classified_columns = []

        for col in columns:
            sem_type, confidence, signals = classify_column_signals(col)
            sensitivity, expose_values = SEMANTIC_SENSITIVITY_MAP.get(
                sem_type, (SensitivityLevel.PUBLIC, True)
            )

            classified_columns.append(
                ColumnClassification(
                    name=col.name,
                    sql_type=col.data_type,
                    semantic_type=sem_type.value,
                    sensitivity=sensitivity.value,
                    expose_values=expose_values,
                    confidence=round(confidence, 2),
                    signals=signals,
                )
            )

        return TableClassificationResponse(
            schema_name=schema_name,
            table=table_name,
            columns=classified_columns,
        )
