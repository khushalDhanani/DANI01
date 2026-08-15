from abc import ABC, abstractmethod
from typing import Any

from app.modules.person.quality.models import (
    QualityCategory,
    QualityFinding,
    QualityFindingStatus,
    QualitySeverity,
)


class PersonQualityRule(ABC):
    """
    Abstract base class for all PERSON data quality rules.
    """

    rule_code: str
    category: QualityCategory
    severity: QualitySeverity
    title: str
    description: str

    @abstractmethod
    def check_applicability(self, tables_map: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Checks if required tables and columns exist for this rule to execute.
        Returns (True, None) if applicable, or (False, "Reason for skip") if skipped.
        """
        pass

    @abstractmethod
    def evaluate(self) -> QualityFinding:
        """
        Executes read-only aggregate SQL queries on MSSQL and returns a QualityFinding.
        """
        pass

    def skipped_finding(self, reason: str) -> QualityFinding:
        """Helper to construct a skipped QualityFinding."""
        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=0,
            total_evaluated=0,
            affected_percent=0.0,
            exact=True,
            message=f"Rule skipped: {reason}",
            status=QualityFindingStatus.SKIPPED,
            skip_reason=reason,
        )

    def failed_finding(self, error_message: str) -> QualityFinding:
        """Helper to construct a failed QualityFinding when query execution encounters an unexpected error."""
        return QualityFinding(
            rule_code=self.rule_code,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=self.description,
            affected_count=0,
            total_evaluated=0,
            affected_percent=0.0,
            exact=False,
            message=f"Rule evaluation error: {error_message}",
            status=QualityFindingStatus.FAILED,
            skip_reason=error_message,
        )
