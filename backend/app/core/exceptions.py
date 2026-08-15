"""Domain exceptions for AIRIS Insights."""


class DBInsightsError(Exception):
    """Base exception for all DB Insights errors."""


class DatabaseConnectionError(DBInsightsError):
    """Raised when connecting to a database fails."""


class ReadOnlyViolationError(DBInsightsError):
    """Raised when an attempt is made to execute modifying SQL."""


class DiscoveryError(DBInsightsError):
    """Raised when metadata discovery operations fail."""


class TableNotFoundError(DiscoveryError):
    """Raised when a requested table or schema is not found."""

    def __init__(self, schema: str, table: str):
        super().__init__(f"Table '{schema}.{table}' not found.")
        self.schema = schema
        self.table = table


class InvalidSortFieldError(DiscoveryError):
    """Raised when an invalid sort field is requested."""

    def __init__(self, field: str, allowed: list[str]):
        super().__init__(
            f"Invalid sort field '{field}'. Allowed fields: {', '.join(allowed)}"
        )
        self.field = field
        self.allowed = allowed
