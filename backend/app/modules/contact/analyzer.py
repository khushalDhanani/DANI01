"""
Contact & Email Module Analyzer Coordinator.
"""

from typing import Any

from app.modules.contact.service import ContactService


class ContactAnalyzer:
    """Coordinates analysis for the Contact & Communication module."""

    def __init__(self, service: ContactService | None = None) -> None:
        self.service = service or ContactService()

    async def analyze(self) -> dict[str, Any]:
        """
        Executes full contact overview and quality audit.
        """
        overview = await self.service.get_contact_overview()
        quality = await self.service.get_contact_quality()

        return {
            "module": "CONTACT",
            "overview": overview.model_dump(),
            "quality": quality.model_dump(),
        }
