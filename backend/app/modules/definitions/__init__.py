from app.modules.definitions.attendance import AttendanceModuleDefinition
from app.modules.definitions.contact import ContactModuleDefinition
from app.modules.definitions.employee import EmployeeModuleDefinition
from app.modules.definitions.organization import OrganizationModuleDefinition
from app.modules.definitions.person import PersonModuleDefinition
from app.modules.definitions.security import SecurityModuleDefinition
from app.modules.registry import module_registry

# Register built-in domain modules
for module_def in (
    PersonModuleDefinition,
    EmployeeModuleDefinition,
    OrganizationModuleDefinition,
    ContactModuleDefinition,
    SecurityModuleDefinition,
    AttendanceModuleDefinition,
):
    try:
        module_registry.register(module_def)
    except Exception:
        pass

__all__ = [
    "PersonModuleDefinition",
    "EmployeeModuleDefinition",
    "OrganizationModuleDefinition",
    "ContactModuleDefinition",
    "SecurityModuleDefinition",
    "AttendanceModuleDefinition",
]
