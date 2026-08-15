import datetime
import decimal
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import TableNotFoundError
from app.sampling.sampler import TableSampler, quote_identifier, serialize_value
from app.schemas.database import ColumnInfo, PrimaryKeyColumn, PrimaryKeyInfo, TableInfo


def test_quote_identifier():
    assert quote_identifier("SimpleName") == "[SimpleName]"
    assert quote_identifier("Name]WithBracket") == "[Name]]WithBracket]"
    assert quote_identifier("Table with spaces") == "[Table with spaces]"


def test_serialize_value():
    assert serialize_value(None) is None
    dt = datetime.datetime(2026, 8, 14, 12, 0, 0, tzinfo=datetime.UTC)
    assert serialize_value(dt) == "2026-08-14T12:00:00+00:00"
    dec = decimal.Decimal("123.45")
    assert serialize_value(dec) == 123.45
    dec_int = decimal.Decimal("100.00")
    assert serialize_value(dec_int) == 100
    u = uuid.uuid4()
    assert serialize_value(u) == str(u)
    b = b"hello\x00world"
    assert serialize_value(b) == f"0x{b.hex()}"


def test_sampler_with_primary_key():
    mock_discovery = MagicMock()
    mock_discovery.get_table.return_value = TableInfo(
        schema="dbo", table="DLPerson", estimated_rows=100, column_count=2
    )
    mock_discovery.get_columns.return_value = [
        ColumnInfo(
            ordinal=1,
            name="PersonID",
            data_type="bigint",
            nullable=False,
            identity=True,
            computed=False,
            has_default=False,
            primary_key=True,
        ),
        ColumnInfo(
            ordinal=2,
            name="FullName",
            data_type="nvarchar",
            nullable=True,
            identity=False,
            computed=False,
            has_default=False,
        ),
    ]
    mock_discovery.get_primary_key.return_value = PrimaryKeyInfo(
        name="PK_Person",
        columns=[PrimaryKeyColumn(name="PersonID", ordinal=1)],
    )

    mock_db_rows = [
        {"PersonID": 1, "FullName": "Alice"},
        {"PersonID": 2, "FullName": "Bob"},
    ]

    with patch(
        "app.sampling.sampler.execute_readonly_query", return_value=mock_db_rows
    ) as mock_exec:
        sampler = TableSampler(discovery=mock_discovery)
        res = sampler.sample("dbo", "DLPerson", limit=50)

        assert res.schema_name == "dbo"
        assert res.table == "DLPerson"
        assert res.requested_rows == 50
        assert res.returned_rows == 2
        assert res.columns == ["PersonID", "FullName"]
        assert len(res.rows) == 2
        assert res.rows[0] == {"PersonID": 1, "FullName": "Alice"}

        # Verify SQL has TOP (50) and ORDER BY [PersonID] ASC
        called_query = mock_exec.call_args[0][0]
        assert "TOP (50)" in called_query
        assert "[dbo].[DLPerson]" in called_query
        assert "ORDER BY [PersonID] ASC" in called_query


def test_sampler_without_primary_key():
    mock_discovery = MagicMock()
    mock_discovery.get_table.return_value = TableInfo(
        schema="dbo", table="DLHeap", estimated_rows=50, column_count=1
    )
    mock_discovery.get_columns.return_value = [
        ColumnInfo(
            ordinal=1,
            name="LogMessage",
            data_type="varchar",
            nullable=True,
            identity=False,
            computed=False,
            has_default=False,
        ),
    ]
    mock_discovery.get_primary_key.return_value = None

    mock_db_rows = [{"LogMessage": "Test Log"}]

    with patch(
        "app.sampling.sampler.execute_readonly_query", return_value=mock_db_rows
    ) as mock_exec:
        sampler = TableSampler(discovery=mock_discovery)
        res = sampler.sample("dbo", "DLHeap", limit=10)

        assert res.returned_rows == 1
        called_query = mock_exec.call_args[0][0]
        assert "TOP (10)" in called_query
        assert "ORDER BY" not in called_query


def test_sampler_table_not_found():
    mock_discovery = MagicMock()
    mock_discovery.get_table.side_effect = TableNotFoundError("dbo", "Missing")

    sampler = TableSampler(discovery=mock_discovery)
    with pytest.raises(TableNotFoundError):
        sampler.sample("dbo", "Missing", limit=10)
