from app.modules.employee.service import EmployeeService


class EmployeeModuleAnalyzer:
    """
    Coordinates metrics analysis for the Employee & Workforce domain module.
    """

    def __init__(self, service: EmployeeService | None = None) -> None:
        self.service = service or EmployeeService()

    async def analyze_overview(self):
        return await self.service.get_employee_overview()

    async def analyze_structure(self):
        return await self.service.get_employee_structure()

    async def analyze_quality(self):
        return await self.service.get_employee_quality()
