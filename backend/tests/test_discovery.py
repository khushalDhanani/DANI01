from unittest.mock import patch

import pytest

from app.core.exceptions import (
    InvalidSortFieldError,
    TableNotFoundError,
)
from app.discovery.metadata import MetadataDiscovery


def test_get_database_summary():
    mock_row = {
        "schema_count": 12,
        "table_count": 934,
        "column_count": 14682,
        "estimated_rows": 284021923,
    }
    with patch(
        "app.discovery.metadata.execute_readonly_query", return_value=[mock_row]
    ):
        service = MetadataDiscovery(db_name="AIRIS_TEST")
        summary = service.get_database_summary()
        assert summary.database == "AIRIS_TEST"
        assert summary.schema_count == 12
        assert summary.table_count == 934
        assert summary.column_count == 14682
        assert summary.estimated_rows == 284021923


def test_get_schemas():
    mock_rows = [
        {"name": "dbo", "table_count": 842},
        {"name": "audit", "table_count": 41},
    ]
    with patch("app.discovery.metadata.execute_readonly_query", return_value=mock_rows):
        service = MetadataDiscovery()
        res = service.get_schemas()
        assert res.total == 2
        assert res.items[0].name == "dbo"
        assert res.items[0].table_count == 842
        assert res.items[1].name == "audit"
        assert res.items[1].table_count == 41


def test_get_tables_pagination_and_filter():
    mock_count = [{"total": 2}]
    mock_data = [
        {
            "schema": "dbo",
            "table": "DLPerson",
            "estimated_rows": 8242921,
            "column_count": 42,
        },
        {
            "schema": "dbo",
            "table": "DLCompany",
            "estimated_rows": 650231,
            "column_count": 37,
        },
    ]
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_count, mock_data],
    ):
        service = MetadataDiscovery()
        res = service.get_tables(
            schema="dbo",
            search="DL",
            limit=10,
            offset=0,
            sort_by="table",
            sort_order="asc",
        )
        assert res.total == 2
        assert len(res.items) == 2
        assert res.items[0].table == "DLPerson"
        assert res.items[0].schema_name == "dbo"
        assert res.items[0].estimated_rows == 8242921
        assert res.items[0].column_count == 42
        assert res.limit == 10
        assert res.offset == 0


def test_get_tables_invalid_sort():
    service = MetadataDiscovery()
    with pytest.raises(InvalidSortFieldError):
        service.get_tables(sort_by="malicious_column; DROP TABLE users;--")


def test_get_table_success():
    mock_row = [
        {
            "schema": "dbo",
            "table": "DLPerson",
            "estimated_rows": 8242921,
            "column_count": 42,
        }
    ]
    with patch("app.discovery.metadata.execute_readonly_query", return_value=mock_row):
        service = MetadataDiscovery()
        table = service.get_table("dbo", "DLPerson")
        assert table.schema_name == "dbo"
        assert table.table == "DLPerson"
        assert table.estimated_rows == 8242921
        assert table.column_count == 42


def test_get_table_not_found():
    with patch("app.discovery.metadata.execute_readonly_query", return_value=[]):
        service = MetadataDiscovery()
        with pytest.raises(TableNotFoundError):
            service.get_table("dbo", "NonExistentTable")


def test_get_columns_success():
    mock_exists = [{"exists_flag": 1}]
    mock_columns = [
        {
            "ordinal": 1,
            "name": "PersonID",
            "data_type": "bigint",
            "max_length": 8,
            "precision": 19,
            "scale": 0,
            "nullable": 0,
            "identity": 1,
            "computed": 0,
            "has_default": 0,
            "default_definition": None,
            "primary_key": 1,
            "foreign_key": 0,
        },
        {
            "ordinal": 2,
            "name": "PersonName",
            "data_type": "nvarchar",
            "max_length": 100,  # 200 bytes in MSSQL / 2 = 100
            "precision": 0,
            "scale": 0,
            "nullable": 1,
            "identity": 0,
            "computed": 0,
            "has_default": 1,
            "default_definition": "('N/A')",
            "primary_key": 0,
            "foreign_key": 0,
        },
    ]
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_exists, mock_columns],
    ):
        service = MetadataDiscovery()
        cols = service.get_columns("dbo", "DLPerson")
        assert len(cols) == 2
        assert cols[0].name == "PersonID"
        assert cols[0].identity is True
        assert cols[0].primary_key is True
        assert cols[1].name == "PersonName"
        assert cols[1].data_type == "nvarchar"
        assert cols[1].max_length == 100
        assert cols[1].has_default is True
        assert cols[1].default_definition == "('N/A')"


def test_get_primary_key_composite():
    mock_exists = [{"exists_flag": 1}]
    mock_pk_rows = [
        {"constraint_name": "PK_Comp", "column_name": "OrgID", "ordinal": 1},
        {"constraint_name": "PK_Comp", "column_name": "DeptID", "ordinal": 2},
    ]
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_exists, mock_pk_rows],
    ):
        service = MetadataDiscovery()
        pk = service.get_primary_key("dbo", "DLDept")
        assert pk is not None
        assert pk.name == "PK_Comp"
        assert len(pk.columns) == 2
        assert pk.columns[0].name == "OrgID"
        assert pk.columns[1].name == "DeptID"


def test_get_primary_key_none():
    mock_exists = [{"exists_flag": 1}]
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_exists, []],
    ):
        service = MetadataDiscovery()
        pk = service.get_primary_key("dbo", "DLHeap")
        assert pk is None


def test_get_foreign_keys_multiple():
    mock_exists = [{"exists_flag": 1}]
    mock_fk_rows = [
        {
            "fk_name": "FK_Person_Org",
            "on_delete": "CASCADE",
            "on_update": "NO_ACTION",
            "referenced_schema": "dbo",
            "referenced_table": "DLOrg",
            "column_name": "OrgID",
            "referenced_column_name": "ID",
            "ordinal": 1,
        }
    ]
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_exists, mock_fk_rows],
    ):
        service = MetadataDiscovery()
        fks = service.get_foreign_keys("dbo", "DLPerson")
        assert len(fks) == 1
        assert fks[0].name == "FK_Person_Org"
        assert fks[0].on_delete == "CASCADE"
        assert fks[0].references.schema_name == "dbo"
        assert fks[0].references.table == "DLOrg"
        assert fks[0].columns[0].column == "OrgID"
        assert fks[0].columns[0].referenced_column == "ID"


def test_get_indexes_with_included_columns():
    mock_exists = [{"exists_flag": 1}]
    mock_idx_rows = [
        {
            "index_name": "IX_DLPerson_Name",
            "type_desc": "NONCLUSTERED",
            "is_unique": 0,
            "is_primary_key": 0,
            "is_unique_constraint": 0,
            "is_disabled": 0,
            "column_name": "LastName",
            "key_ordinal": 1,
            "is_descending_key": 0,
            "is_included_column": 0,
        },
        {
            "index_name": "IX_DLPerson_Name",
            "type_desc": "NONCLUSTERED",
            "is_unique": 0,
            "is_primary_key": 0,
            "is_unique_constraint": 0,
            "is_disabled": 0,
            "column_name": "Email",
            "key_ordinal": 0,
            "is_descending_key": 0,
            "is_included_column": 1,
        },
    ]
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_exists, mock_idx_rows],
    ):
        service = MetadataDiscovery()
        indexes = service.get_indexes("dbo", "DLPerson")
        assert len(indexes) == 1
        assert indexes[0].name == "IX_DLPerson_Name"
        assert len(indexes[0].key_columns) == 1
        assert indexes[0].key_columns[0].name == "LastName"
        assert indexes[0].included_columns == ["Email"]
