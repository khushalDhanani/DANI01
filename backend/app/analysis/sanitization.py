import logging
from typing import Any

from app.classification.taxonomy import SensitivityLevel
from app.schemas.classification import TableClassificationResponse
from app.schemas.profiling import (
    BaseColumnProfile,
    BooleanColumnProfile,
    DateTimeColumnProfile,
    NumericColumnProfile,
    TableProfileResponse,
    TextColumnProfile,
)

logger = logging.getLogger(__name__)


class ProfileSanitizer:
    """
    Centralized privacy sanitization layer.
    Ensures that raw sample values and sensitive PII frequencies
    (e.g., EMAIL, PHONE, NAME, DATE_OF_BIRTH, ADDRESS, STREET, NOTES)
    whose classification has `expose_values = False` are redacted before persistence.
    """

    @staticmethod
    def sanitize_column_profiles(
        profile_response: TableProfileResponse,
        classification_response: TableClassificationResponse,
    ) -> list[dict[str, Any]]:
        """
        Combines and sanitizes column profiles and classification metadata.
        Returns a list of dicts formatted for database persistence.
        """
        # Create map of classification by column name
        class_map = {col.name: col for col in classification_response.columns}

        sanitized_profiles: list[dict[str, Any]] = []

        for col_prof in profile_response.columns:
            classification = class_map.get(col_prof.name)
            expose_values = classification.expose_values if classification else True
            sensitivity = classification.sensitivity if classification else SensitivityLevel.PUBLIC.value

            # If expose_values is False or sensitivity is PII, redact top_values
            if not expose_values or sensitivity == SensitivityLevel.PII.value:
                sanitized_top_values = []
            else:
                sanitized_top_values = [
                    v.model_dump(mode="json") for v in col_prof.top_values
                ]

            # Extract type-specific stats
            stats: dict[str, Any] = {}
            if isinstance(col_prof, TextColumnProfile):
                stats = {
                    "empty_count": col_prof.empty_count,
                    "empty_percent": col_prof.empty_percent,
                    "blank_count": col_prof.blank_count,
                    "blank_percent": col_prof.blank_percent,
                    "min_length": col_prof.min_length,
                    "max_length": col_prof.max_length,
                    "avg_length": col_prof.avg_length,
                }
            elif isinstance(col_prof, NumericColumnProfile):
                stats = {
                    "min": col_prof.min,
                    "max": col_prof.max,
                    "mean": col_prof.mean,
                    "median": col_prof.median,
                    "std_dev": col_prof.std_dev,
                    "zero_count": col_prof.zero_count,
                    "zero_percent": col_prof.zero_percent,
                    "negative_count": col_prof.negative_count,
                    "negative_percent": col_prof.negative_percent,
                }
            elif isinstance(col_prof, DateTimeColumnProfile):
                stats = {
                    "min": col_prof.min,
                    "max": col_prof.max,
                }
            elif isinstance(col_prof, BooleanColumnProfile):
                stats = {
                    "true_count": col_prof.true_count,
                    "false_count": col_prof.false_count,
                    "true_percent": col_prof.true_percent,
                    "false_percent": col_prof.false_percent,
                }

            sanitized_profiles.append(
                {
                    "column_name": col_prof.name,
                    "data_type": col_prof.data_type,
                    "profile_type": getattr(col_prof, "profile_type", "generic"),
                    "null_count": col_prof.null_count,
                    "null_percent": col_prof.null_percent,
                    "distinct_count": col_prof.distinct_count,
                    "distinct_percent": col_prof.distinct_percent,
                    "top_values": sanitized_top_values,
                    "stats": stats,
                }
            )

        return sanitized_profiles
