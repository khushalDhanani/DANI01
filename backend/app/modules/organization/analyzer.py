from app.modules.organization.service import OrganizationService


class OrganizationModuleAnalyzer:
    """
    Coordinates analytical processing and metrics extraction for the Organization Structure domain.
    """

    def __init__(self, service: OrganizationService | None = None) -> None:
        self.service = service or OrganizationService()

    async def analyze_overview(self):
        return await self.service.get_org_overview()

    async def analyze_hierarchy(self):
        return await self.service.get_org_hierarchy_map()

    async def analyze_quality(self):
        return await self.service.get_org_quality()
