"""
User / Login & Security Module Analyzer Coordinator.
"""

from typing import Any

from app.modules.security.service import SecurityService


class SecurityAnalyzer:
    """Coordinates analysis for the User / Login & Security Intelligence module."""

    def __init__(self, service: SecurityService | None = None) -> None:
        self.service = service or SecurityService()

    async def analyze(self) -> dict[str, Any]:
        """
        Executes full security overview, roles catalog, and data quality audit.
        """
        overview = await self.service.get_security_overview()
        roles = await self.service.get_roles_catalog()
        quality = await self.service.get_security_quality()

        return {
            "module": "SECURITY",
            "overview": overview.model_dump(),
            "roles": roles.model_dump(),
            "quality": quality.model_dump(),
        }
