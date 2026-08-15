import logging
import re

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Compile a regex to detect any modification keywords in SQL statements
# This is a safety net; the database user itself should also be strictly read-only.
# Using word boundaries \b to ensure we match whole words and case insensitive
MODIFICATION_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|CREATE|TRUNCATE)\b", re.IGNORECASE
)

from app.core.exceptions import DatabaseConnectionError, ReadOnlyViolationError


def create_mssql_engine() -> Engine | None:
    """Creates and configures the MSSQL SQLAlchemy engine."""
    if not settings.mssql_url:
        return None

    engine = create_engine(
        settings.mssql_url,
        pool_size=settings.MSSQL_POOL_SIZE,
        max_overflow=settings.MSSQL_MAX_OVERFLOW,
        # pool_timeout logic would go here if needed
        # We rely on query timeout within pyodbc connect args if necessary
        # connect_args={'timeout': settings.MSSQL_QUERY_TIMEOUT}
    )
    return engine


# Global engine instance
engine = create_mssql_engine()


def guard_read_only(query_str: str) -> None:
    """
    Checks a SQL query string against a list of blocked modification keywords.
    Ignores identifiers enclosed in brackets (e.g. [Update]) and string literals.
    Raises ReadOnlyViolationError if a violation is detected.
    """
    # Strip string literals and bracketed identifiers to prevent false positives on column names like [Update]
    sanitized = re.sub(r"'(?:''|[^'])*'", "", query_str)
    sanitized = re.sub(r"\[(?:\]\]|[^\]])*\]", "", sanitized)

    if MODIFICATION_KEYWORDS.search(sanitized):
        logger.error(f"Blocked destructive query attempt: {query_str[:100]}...")
        raise ReadOnlyViolationError(
            "Attempted to execute a modification query against the read-only MSSQL database."
        )


def test_connection() -> bool:
    """
    Tests the connection to the MSSQL database by executing a simple SELECT 1.
    """
    if engine is None:
        return False

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            row = result.fetchone()
            return row and row[0] == 1
    except SQLAlchemyError as e:
        logger.error(f"Failed to connect to MSSQL: {e}")
        return False


def execute_readonly_query(query: str, params: dict | None = None):
    """
    Executes a read-only query safely.
    """
    if engine is None:
        raise DatabaseConnectionError("MSSQL engine is not initialized.")

    guard_read_only(query)

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result.mappings().all()
    except SQLAlchemyError as e:
        logger.error(f"Query execution failed: {e}")
        raise


def dispose_engine() -> None:
    """Disposes the engine connection pool cleanly."""
    if engine:
        engine.dispose()
