import datetime
import decimal
import logging
import uuid
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.exceptions import (
    DatabaseConnectionError,
    DiscoveryError,
    TableNotFoundError,
)
from app.db.mssql import execute_readonly_query
from app.discovery.metadata import MetadataDiscovery
from app.schemas.sampling import TableSampleResponse

logger = logging.getLogger(__name__)


def quote_identifier(name: str) -> str:
    """Safely escapes and quotes an identifier for SQL Server."""
    return f"[{name.replace(']', ']]')}]"


def serialize_value(val: Any) -> Any:
    """Serializes SQL/Python values into JSON-compatible types."""
    if val is None:
        return None
    if isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
        return val.isoformat()
    if isinstance(val, decimal.Decimal):
        return float(val) if val % 1 else int(val)
    if isinstance(val, (bytes, bytearray, memoryview)):
        return f"0x{bytes(val).hex()}"
    if isinstance(val, uuid.UUID):
        return str(val)
    return val


class TableSampler:
    def __init__(self, discovery: MetadataDiscovery | None = None):
        self.discovery = discovery or MetadataDiscovery()

    def sample(
        self,
        schema_name: str,
        table_name: str,
        limit: int = 100,
    ) -> TableSampleResponse:
        """
        Safely samples up to `limit` rows from a table using structural metadata.
        Never performs full table scans or executes unconstrained queries.
        """
        # 1. Validate table and fetch structural metadata
        table_info = self.discovery.get_table(schema_name, table_name)
        columns_info = self.discovery.get_columns(schema_name, table_name)
        pk_info = self.discovery.get_primary_key(schema_name, table_name)

        if not columns_info:
            raise DiscoveryError(f"No columns discovered for table '{schema_name}.{table_name}'.")

        # 2. Clamp sample size safely
        requested_rows = limit
        clamped_limit = max(1, min(limit, settings.PROFILE_MAX_SAMPLE_SIZE))

        # 3. Build safe quoted column selection list
        safe_schema = quote_identifier(table_info.schema_name)
        safe_table = quote_identifier(table_info.table)
        column_names = [col.name for col in columns_info]
        cols_str = ", ".join([quote_identifier(name) for name in column_names])

        # 4. Formulate query (deterministic PK order if PK exists, plain TOP if no PK)
        if pk_info and pk_info.columns:
            order_by_clause = ", ".join(
                [f"{quote_identifier(pk_col.name)} ASC" for pk_col in pk_info.columns]
            )
            query = (
                f"SELECT TOP ({clamped_limit}) {cols_str} "
                f"FROM {safe_schema}.{safe_table} "
                f"ORDER BY {order_by_clause};"
            )
        else:
            query = f"SELECT TOP ({clamped_limit}) {cols_str} FROM {safe_schema}.{safe_table};"

        # 5. Execute query safely with read-only protections
        try:
            raw_rows = execute_readonly_query(query)
            serialized_rows = [{k: serialize_value(v) for k, v in row.items()} for row in raw_rows]

            return TableSampleResponse(
                schema_name=table_info.schema_name,
                table=table_info.table,
                requested_rows=requested_rows,
                returned_rows=len(serialized_rows),
                columns=column_names,
                rows=serialized_rows,
            )
        except (TableNotFoundError, DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Failed to sample table '{schema_name}.{table_name}': {e}")
            raise DiscoveryError(f"Error sampling table '{schema_name}.{table_name}': {e}") from e
