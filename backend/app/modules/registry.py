import logging

from app.modules.models import ModuleDefinition, ModuleInfo

logger = logging.getLogger(__name__)


class DuplicateModuleError(ValueError):
    """Raised when registering a module with an existing code."""


class ModuleRegistry:
    """
    In-memory registry for pluggable business module definitions.
    Enforces uniqueness of module codes and provides thread-safe access.
    """

    def __init__(self) -> None:
        self._modules: dict[str, ModuleDefinition] = {}

    def register(self, definition: ModuleDefinition) -> None:
        """
        Registers a new module definition.
        Raises DuplicateModuleError if module code is already registered.
        """
        normalized_code = definition.code.strip().upper()
        if normalized_code in self._modules:
            raise DuplicateModuleError(
                f"Module with code '{normalized_code}' is already registered: '{self._modules[normalized_code].name}'"
            )

        self._modules[normalized_code] = definition
        logger.info(
            f"Registered module '{definition.name}' [{normalized_code}] with {len(definition.tables)} configured tables"
        )

    def get(self, code: str) -> ModuleDefinition | None:
        """
        Retrieves a module definition by code (case-insensitive).
        """
        normalized_code = code.strip().upper()
        return self._modules.get(normalized_code)

    def list_all(self) -> list[ModuleDefinition]:
        """
        Returns all registered module definitions.
        """
        return list(self._modules.values())

    def list_info(self) -> list[ModuleInfo]:
        """
        Returns compact ModuleInfo summaries for all registered modules.
        """
        return [
            ModuleInfo(
                code=m.code,
                name=m.name,
                description=m.description,
                root_table=f"{m.root_schema}.{m.root_table}",
                root_key=m.root_key,
                table_count=len(m.tables),
                relationship_count=len(m.relationships),
                enabled=m.enabled,
                tags=m.tags,
            )
            for m in self._modules.values()
        ]

    def unregister(self, code: str) -> bool:
        """
        Unregisters a module by code. Returns True if removed, False otherwise.
        """
        normalized_code = code.strip().upper()
        if normalized_code in self._modules:
            del self._modules[normalized_code]
            return True
        return False

    def clear(self) -> None:
        """
        Clears all registered modules (used primarily for test isolation).
        """
        self._modules.clear()


# Global Singleton Registry
module_registry = ModuleRegistry()
