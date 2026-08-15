from app.modules.definitions.person import PersonModuleDefinition
from app.modules.registry import module_registry

# Register built-in domain modules
try:
    module_registry.register(PersonModuleDefinition)
except Exception:
    pass

__all__ = ["PersonModuleDefinition"]
