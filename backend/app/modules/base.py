from abc import ABC, abstractmethod
from typing import Any

from app.modules.models import (
    ModuleAnalysisContext,
    ModuleAnalysisResult,
    ModuleDefinition,
    ModuleValidationResult,
)


class BaseModuleRule(ABC):
    """
    Abstract base for business-specific validation rules (for M2+ extensibility).
    """

    code: str
    name: str
    description: str

    @abstractmethod
    def evaluate(self, context: ModuleAnalysisContext) -> list[dict[str, Any]]:
        """Evaluate rule against the module analysis context and return findings."""


class BaseModuleMetric(ABC):
    """
    Abstract base for business-specific calculated metrics (for M2+ extensibility).
    """

    code: str
    name: str

    @abstractmethod
    def calculate(self, context: ModuleAnalysisContext) -> Any:
        """Compute metric value from module analysis context."""


class BaseModuleAnalyzer(ABC):
    """
    Abstract base interface for module analyzers.
    """

    @abstractmethod
    async def validate(self, definition: ModuleDefinition) -> ModuleValidationResult:
        """Validate module definition against database discovery metadata."""

    @abstractmethod
    async def build_context(
        self, definition: ModuleDefinition, sample_size: int = 1000
    ) -> ModuleAnalysisContext:
        """Collect metadata, profiles, and classifications for module tables."""

    @abstractmethod
    async def analyze(
        self, definition: ModuleDefinition, sample_size: int = 1000
    ) -> ModuleAnalysisResult:
        """Execute framework-level analysis for the module."""
