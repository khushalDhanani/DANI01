import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.exceptions import (
    DatabaseConnectionError,
    DiscoveryError,
    InvalidSortFieldError,
    TableNotFoundError,
)
from app.db.mssql import execute_readonly_query
from app.schemas.database import (
    ColumnInfo,
    ColumnListResponse,
    DatabaseSummary,
    ForeignKeyColumn,
    ForeignKeyInfo,
    ForeignKeyReference,
    IndexColumn,
    IndexInfo,
    IndexListResponse,
    PrimaryKeyColumn,
    PrimaryKeyInfo,
    SchemaInfo,
    SchemaListResponse,
    TableInfo,
    TableKeysResponse,
    TableListResponse,
    TableStructureResponse,
)

logger = logging.getLogger(__name__)

SYSTEM_SCHEMAS = (
    "'sys', 'INFORMATION_SCHEMA', 'guest', 'db_owner', 'db_accessadmin', "
    "'db_securityadmin', 'db_ddladmin', 'db_backupoperator', 'db_datareader', "
    "'db_datawriter', 'db_denydatareader', 'db_denydatawriter'"
)

ALLOWED_SORT_FIELDS = {
    "schema": "[schema]",
    "table": "[table]",
    "estimated_rows": "estimated_rows",
    "column_count": "column_count",
}


class MetadataDiscovery:
    def __init__(self, db_name: str | None = None):
        self.db_name = db_name or settings.MSSQL_DATABASE

    def _verify_table_exists(self, schema_name: str, table_name: str) -> None:
        """Helper to verify that a table exists, raising TableNotFoundError if not."""
        query = """
        SELECT 1 AS exists_flag
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name = :schema_name AND t.name = :table_name;
        """
        params = {"schema_name": schema_name, "table_name": table_name}
        try:
            rows = execute_readonly_query(query, params)
            if not rows:
                raise TableNotFoundError(schema_name, table_name)
        except (TableNotFoundError, DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to check table existence '{schema_name}.{table_name}': {e}"
            )
            raise DiscoveryError(
                f"Error checking table existence '{schema_name}.{table_name}': {e}"
            ) from e

    def get_database_summary(self) -> DatabaseSummary:
        """Fetches high-level metadata summary of the MSSQL database."""
        query = f"""
        SELECT 
            (SELECT COUNT(DISTINCT s.schema_id)
             FROM sys.schemas s
             JOIN sys.tables t ON t.schema_id = s.schema_id
             WHERE s.name NOT IN ({SYSTEM_SCHEMAS})
               AND t.is_ms_shipped = 0) AS schema_count,
               
            (SELECT COUNT(t.object_id)
             FROM sys.tables t
             JOIN sys.schemas s ON t.schema_id = s.schema_id
             WHERE s.name NOT IN ({SYSTEM_SCHEMAS})
               AND t.is_ms_shipped = 0) AS table_count,
               
            (SELECT COUNT(c.column_id)
             FROM sys.columns c
             JOIN sys.tables t ON c.object_id = t.object_id
             JOIN sys.schemas s ON t.schema_id = s.schema_id
             WHERE s.name NOT IN ({SYSTEM_SCHEMAS})
               AND t.is_ms_shipped = 0) AS column_count,
               
            (SELECT ISNULL(SUM(p.rows), 0)
             FROM sys.partitions p
             JOIN sys.tables t ON p.object_id = t.object_id
             JOIN sys.schemas s ON t.schema_id = s.schema_id
             WHERE p.index_id IN (0, 1)
               AND s.name NOT IN ({SYSTEM_SCHEMAS})
               AND t.is_ms_shipped = 0) AS estimated_rows;
        """
        try:
            results = execute_readonly_query(query)
            if not results:
                raise DiscoveryError("No database summary returned.")
            row = results[0]
            return DatabaseSummary(
                database=self.db_name,
                schema_count=row["schema_count"] or 0,
                table_count=row["table_count"] or 0,
                column_count=row["column_count"] or 0,
                estimated_rows=int(row["estimated_rows"] or 0),
            )
        except (DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch database summary: {e}")
            raise DiscoveryError(f"Error fetching database summary: {e}") from e

    def get_schemas(self) -> SchemaListResponse:
        """Discovers non-system schemas and their associated table counts."""
        query = f"""
        SELECT 
            s.name AS name,
            COUNT(t.object_id) AS table_count
        FROM sys.schemas s
        JOIN sys.tables t ON s.schema_id = t.schema_id
        WHERE s.name NOT IN ({SYSTEM_SCHEMAS})
          AND t.is_ms_shipped = 0
        GROUP BY s.name
        ORDER BY table_count DESC, s.name ASC;
        """
        try:
            rows = execute_readonly_query(query)
            items = [
                SchemaInfo(name=r["name"], table_count=r["table_count"] or 0)
                for r in rows
            ]
            return SchemaListResponse(items=items, total=len(items))
        except (DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch schemas: {e}")
            raise DiscoveryError(f"Error fetching schemas: {e}") from e

    def get_tables(
        self,
        schema: str | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "table",
        sort_order: str = "asc",
    ) -> TableListResponse:
        """Discovers tables with estimated row counts and column counts, with pagination and filtering."""
        sort_by_lower = sort_by.lower()
        if sort_by_lower not in ALLOWED_SORT_FIELDS:
            raise InvalidSortFieldError(sort_by, list(ALLOWED_SORT_FIELDS.keys()))

        sort_order_clean = "DESC" if sort_order.lower() == "desc" else "ASC"
        sort_col = ALLOWED_SORT_FIELDS[sort_by_lower]

        search_pattern = f"%{search}%" if search else None

        count_query = f"""
        SELECT COUNT(t.object_id) AS total
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name NOT IN ({SYSTEM_SCHEMAS})
          AND t.is_ms_shipped = 0
          AND (:schema IS NULL OR s.name = :schema)
          AND (:search_pattern IS NULL OR t.name LIKE :search_pattern);
        """

        data_query = f"""
        WITH TableData AS (
            SELECT 
                s.name AS [schema],
                t.name AS [table],
                ISNULL(part.estimated_rows, 0) AS estimated_rows,
                ISNULL(col.column_count, 0) AS column_count
            FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            LEFT JOIN (
                SELECT object_id, SUM(rows) AS estimated_rows
                FROM sys.partitions
                WHERE index_id IN (0, 1)
                GROUP BY object_id
            ) part ON t.object_id = part.object_id
            LEFT JOIN (
                SELECT object_id, COUNT(column_id) AS column_count
                FROM sys.columns
                GROUP BY object_id
            ) col ON t.object_id = col.object_id
            WHERE s.name NOT IN ({SYSTEM_SCHEMAS})
              AND t.is_ms_shipped = 0
              AND (:schema IS NULL OR s.name = :schema)
              AND (:search_pattern IS NULL OR t.name LIKE :search_pattern)
        )
        SELECT [schema], [table], estimated_rows, column_count
        FROM TableData
        ORDER BY {sort_col} {sort_order_clean}
        OFFSET :offset ROWS
        FETCH NEXT :limit ROWS ONLY;
        """

        params = {
            "schema": schema,
            "search_pattern": search_pattern,
            "offset": offset,
            "limit": limit,
        }

        try:
            count_rows = execute_readonly_query(count_query, params)
            total = count_rows[0]["total"] if count_rows else 0

            data_rows = execute_readonly_query(data_query, params)
            items = [
                TableInfo(
                    schema=r["schema"],
                    table=r["table"],
                    estimated_rows=int(r["estimated_rows"] or 0),
                    column_count=int(r["column_count"] or 0),
                )
                for r in data_rows
            ]

            return TableListResponse(
                items=items, total=total, limit=limit, offset=offset
            )
        except (DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch tables: {e}")
            raise DiscoveryError(f"Error fetching tables: {e}") from e

    def get_table(self, schema_name: str, table_name: str) -> TableInfo:
        """Fetches metadata for a single specific table."""
        query = """
        SELECT 
            s.name AS [schema],
            t.name AS [table],
            ISNULL(part.estimated_rows, 0) AS estimated_rows,
            ISNULL(col.column_count, 0) AS column_count
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        LEFT JOIN (
            SELECT object_id, SUM(rows) AS estimated_rows
            FROM sys.partitions
            WHERE index_id IN (0, 1)
            GROUP BY object_id
        ) part ON t.object_id = part.object_id
        LEFT JOIN (
            SELECT object_id, COUNT(column_id) AS column_count
            FROM sys.columns
            GROUP BY object_id
        ) col ON t.object_id = col.object_id
        WHERE s.name = :schema_name
          AND t.name = :table_name;
        """
        params = {"schema_name": schema_name, "table_name": table_name}

        try:
            rows = execute_readonly_query(query, params)
            if not rows:
                raise TableNotFoundError(schema_name, table_name)
            r = rows[0]
            return TableInfo(
                schema=r["schema"],
                table=r["table"],
                estimated_rows=int(r["estimated_rows"] or 0),
                column_count=int(r["column_count"] or 0),
            )
        except (TableNotFoundError, DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch table '{schema_name}.{table_name}': {e}")
            raise DiscoveryError(
                f"Error fetching table '{schema_name}.{table_name}': {e}"
            ) from e

    def get_columns(self, schema_name: str, table_name: str) -> list[ColumnInfo]:
        """Discovers column specifications for a specific table."""
        self._verify_table_exists(schema_name, table_name)

        query = """
        SELECT 
            c.column_id AS ordinal,
            c.name AS name,
            tp.name AS data_type,
            CASE 
                WHEN tp.name IN ('nchar', 'nvarchar') AND c.max_length > 0 THEN c.max_length / 2
                WHEN tp.name IN ('nchar', 'nvarchar') AND c.max_length = -1 THEN -1
                WHEN tp.name IN ('char', 'varchar', 'binary', 'varbinary') AND c.max_length = -1 THEN -1
                WHEN tp.name IN ('char', 'varchar', 'binary', 'varbinary') THEN c.max_length
                ELSE c.max_length
            END AS max_length,
            c.precision,
            c.scale,
            c.is_nullable AS nullable,
            c.is_identity AS [identity],
            c.is_computed AS computed,
            CASE WHEN c.default_object_id != 0 THEN 1 ELSE 0 END AS has_default,
            dc.definition AS default_definition,
            CASE WHEN pk_cols.column_id IS NOT NULL THEN 1 ELSE 0 END AS primary_key,
            CASE WHEN fk_cols.column_id IS NOT NULL THEN 1 ELSE 0 END AS foreign_key
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.columns c ON t.object_id = c.object_id
        JOIN sys.types tp ON c.user_type_id = tp.user_type_id
        LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
        LEFT JOIN (
            SELECT ic.object_id, ic.column_id
            FROM sys.indexes i
            JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            WHERE i.is_primary_key = 1
        ) pk_cols ON c.object_id = pk_cols.object_id AND c.column_id = pk_cols.column_id
        LEFT JOIN (
            SELECT DISTINCT fkc.parent_object_id AS object_id, fkc.parent_column_id AS column_id
            FROM sys.foreign_key_columns fkc
        ) fk_cols ON c.object_id = fk_cols.object_id AND c.column_id = fk_cols.column_id
        WHERE s.name = :schema_name AND t.name = :table_name
        ORDER BY c.column_id ASC;
        """
        params = {"schema_name": schema_name, "table_name": table_name}

        try:
            rows = execute_readonly_query(query, params)
            return [
                ColumnInfo(
                    ordinal=r["ordinal"],
                    name=r["name"],
                    data_type=r["data_type"],
                    max_length=int(r["max_length"])
                    if r["max_length"] is not None
                    else None,
                    precision=int(r["precision"])
                    if r["precision"] is not None
                    else None,
                    scale=int(r["scale"]) if r["scale"] is not None else None,
                    nullable=bool(r["nullable"]),
                    identity=bool(r["identity"]),
                    computed=bool(r["computed"]),
                    has_default=bool(r["has_default"]),
                    default_definition=r["default_definition"],
                    primary_key=bool(r["primary_key"]),
                    foreign_key=bool(r["foreign_key"]),
                )
                for r in rows
            ]
        except (TableNotFoundError, DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to fetch columns for '{schema_name}.{table_name}': {e}"
            )
            raise DiscoveryError(
                f"Error fetching columns for '{schema_name}.{table_name}': {e}"
            ) from e

    def get_column_list_response(
        self, schema_name: str, table_name: str
    ) -> ColumnListResponse:
        """Returns the full ColumnListResponse model for a table."""
        columns = self.get_columns(schema_name, table_name)
        return ColumnListResponse(
            schema_name=schema_name,
            table=table_name,
            columns=columns,
        )

    def get_primary_key(
        self, schema_name: str, table_name: str
    ) -> PrimaryKeyInfo | None:
        """Discovers primary key constraint and key columns for a specific table."""
        self._verify_table_exists(schema_name, table_name)

        query = """
        SELECT 
            i.name AS constraint_name,
            c.name AS column_name,
            ic.key_ordinal AS ordinal
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.indexes i ON t.object_id = i.object_id AND i.is_primary_key = 1
        JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id AND ic.is_included_column = 0
        JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE s.name = :schema_name AND t.name = :table_name
        ORDER BY ic.key_ordinal ASC;
        """
        params = {"schema_name": schema_name, "table_name": table_name}

        try:
            rows = execute_readonly_query(query, params)
            if not rows:
                return None

            constraint_name = rows[0]["constraint_name"]
            columns = [
                PrimaryKeyColumn(name=r["column_name"], ordinal=r["ordinal"])
                for r in rows
            ]
            return PrimaryKeyInfo(name=constraint_name, columns=columns)
        except (TableNotFoundError, DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to fetch primary key for '{schema_name}.{table_name}': {e}"
            )
            raise DiscoveryError(
                f"Error fetching primary key for '{schema_name}.{table_name}': {e}"
            ) from e

    def get_foreign_keys(
        self, schema_name: str, table_name: str
    ) -> list[ForeignKeyInfo]:
        """Discovers foreign key constraints for a specific table."""
        self._verify_table_exists(schema_name, table_name)

        query = """
        SELECT 
            fk.name AS fk_name,
            fk.delete_referential_action_desc AS on_delete,
            fk.update_referential_action_desc AS on_update,
            ref_s.name AS referenced_schema,
            ref_t.name AS referenced_table,
            c_parent.name AS column_name,
            c_ref.name AS referenced_column_name,
            fkc.constraint_column_id AS ordinal
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.foreign_keys fk ON t.object_id = fk.parent_object_id
        JOIN sys.tables ref_t ON fk.referenced_object_id = ref_t.object_id
        JOIN sys.schemas ref_s ON ref_t.schema_id = ref_s.schema_id
        JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        JOIN sys.columns c_parent ON fkc.parent_object_id = c_parent.object_id AND fkc.parent_column_id = c_parent.column_id
        JOIN sys.columns c_ref ON fkc.referenced_object_id = c_ref.object_id AND fkc.referenced_column_id = c_ref.column_id
        WHERE s.name = :schema_name AND t.name = :table_name
        ORDER BY fk.name, fkc.constraint_column_id;
        """
        params = {"schema_name": schema_name, "table_name": table_name}

        try:
            rows = execute_readonly_query(query, params)
            fk_map: dict[str, dict] = {}
            for r in rows:
                fk_name = r["fk_name"]
                if fk_name not in fk_map:
                    fk_map[fk_name] = {
                        "name": fk_name,
                        "on_delete": r["on_delete"] or "NO_ACTION",
                        "on_update": r["on_update"] or "NO_ACTION",
                        "references": ForeignKeyReference(
                            schema_name=r["referenced_schema"],
                            table=r["referenced_table"],
                        ),
                        "columns": [],
                    }
                fk_map[fk_name]["columns"].append(
                    ForeignKeyColumn(
                        column=r["column_name"],
                        referenced_column=r["referenced_column_name"],
                        ordinal=r["ordinal"],
                    )
                )

            return [ForeignKeyInfo(**v) for v in fk_map.values()]
        except (TableNotFoundError, DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to fetch foreign keys for '{schema_name}.{table_name}': {e}"
            )
            raise DiscoveryError(
                f"Error fetching foreign keys for '{schema_name}.{table_name}': {e}"
            ) from e

    def get_indexes(self, schema_name: str, table_name: str) -> list[IndexInfo]:
        """Discovers clustered/nonclustered indexes and included columns for a specific table."""
        self._verify_table_exists(schema_name, table_name)

        query = """
        SELECT 
            i.name AS index_name,
            i.type_desc AS type_desc,
            i.is_unique,
            i.is_primary_key,
            i.is_unique_constraint,
            i.is_disabled,
            c.name AS column_name,
            ic.key_ordinal,
            ic.is_descending_key,
            ic.is_included_column
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.indexes i ON t.object_id = i.object_id
        JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE s.name = :schema_name 
          AND t.name = :table_name
          AND i.type > 0
        ORDER BY i.name, ic.is_included_column, ic.key_ordinal, c.name;
        """
        params = {"schema_name": schema_name, "table_name": table_name}

        try:
            rows = execute_readonly_query(query, params)
            index_map: dict[str, dict] = {}
            for r in rows:
                idx_name = r["index_name"]
                if idx_name not in index_map:
                    index_map[idx_name] = {
                        "name": idx_name,
                        "type": r["type_desc"],
                        "unique": bool(r["is_unique"]),
                        "primary_key": bool(r["is_primary_key"]),
                        "unique_constraint": bool(r["is_unique_constraint"]),
                        "disabled": bool(r["is_disabled"]),
                        "key_columns": [],
                        "included_columns": [],
                    }

                if r["is_included_column"]:
                    index_map[idx_name]["included_columns"].append(r["column_name"])
                else:
                    index_map[idx_name]["key_columns"].append(
                        IndexColumn(
                            name=r["column_name"],
                            ordinal=r["key_ordinal"],
                            descending=bool(r["is_descending_key"]),
                        )
                    )

            return [IndexInfo(**v) for v in index_map.values()]
        except (TableNotFoundError, DatabaseConnectionError, DiscoveryError):
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to fetch indexes for '{schema_name}.{table_name}': {e}"
            )
            raise DiscoveryError(
                f"Error fetching indexes for '{schema_name}.{table_name}': {e}"
            ) from e

    def get_index_list_response(
        self, schema_name: str, table_name: str
    ) -> IndexListResponse:
        """Returns the full IndexListResponse model for a table."""
        indexes = self.get_indexes(schema_name, table_name)
        return IndexListResponse(
            schema_name=schema_name,
            table=table_name,
            indexes=indexes,
        )

    def get_table_keys(self, schema_name: str, table_name: str) -> TableKeysResponse:
        """Discovers both Primary Key and Foreign Keys for a specific table."""
        pk = self.get_primary_key(schema_name, table_name)
        fks = self.get_foreign_keys(schema_name, table_name)
        return TableKeysResponse(
            schema_name=schema_name,
            table=table_name,
            primary_key=pk,
            foreign_keys=fks,
        )

    def get_table_structure(
        self, schema_name: str, table_name: str
    ) -> TableStructureResponse:
        """Discovers full table structure (table metadata, columns, PK, FKs, and indexes)."""
        table_info = self.get_table(schema_name, table_name)
        columns = self.get_columns(schema_name, table_name)
        pk = self.get_primary_key(schema_name, table_name)
        fks = self.get_foreign_keys(schema_name, table_name)
        indexes = self.get_indexes(schema_name, table_name)

        return TableStructureResponse(
            table=table_info,
            columns=columns,
            primary_key=pk,
            foreign_keys=fks,
            indexes=indexes,
        )
