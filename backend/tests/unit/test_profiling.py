from unittest.mock import MagicMock

import polars as pl

from app.profiling.boolean_profiler import profile_boolean_column
from app.profiling.datetime_profiler import profile_datetime_column
from app.profiling.numeric_profiler import profile_numeric_column
from app.profiling.profiler import TableProfiler
from app.profiling.text_profiler import profile_text_column
from app.schemas.database import ColumnInfo
from app.schemas.sampling import TableSampleResponse


def test_text_profiler_whitespace_and_stats():
    # 6 rows: "Hello", "" (empty), "   " (blank), None (null), "World", "Hello"
    data = ["Hello", "", "   ", None, "World", "Hello"]
    series = pl.Series("CityName", data)

    profile = profile_text_column(
        series=series,
        col_name="CityName",
        data_type="nvarchar",
        total_rows=6,
    )

    assert profile.name == "CityName"
    assert profile.profile_type == "text"
    assert profile.null_count == 1
    assert profile.null_percent == 16.67
    assert profile.empty_count == 1
    assert profile.empty_percent == 16.67
    assert profile.blank_count == 1
    assert profile.blank_percent == 16.67
    assert profile.distinct_count == 5  # {"Hello", "", "   ", None, "World"}
    assert profile.min_length == 0
    assert profile.max_length == 5
    assert len(profile.top_values) > 0
    assert profile.top_values[0].value == "Hello"
    assert profile.top_values[0].count == 2


def test_numeric_profiler_stats():
    # 6 rows: 10, 20, 0, -5, None, 15
    data = [10, 20, 0, -5, None, 15]
    series = pl.Series("Amount", data)

    profile = profile_numeric_column(
        series=series,
        col_name="Amount",
        data_type="decimal",
        total_rows=6,
    )

    assert profile.name == "Amount"
    assert profile.profile_type == "numeric"
    assert profile.null_count == 1
    assert profile.null_percent == 16.67
    assert profile.zero_count == 1
    assert profile.zero_percent == 16.67
    assert profile.negative_count == 1
    assert profile.negative_percent == 16.67
    assert profile.min == -5.0
    assert profile.max == 20.0
    assert profile.mean == 8.0
    assert profile.median == 10.0


def test_datetime_profiler_stats():
    data = ["2026-01-01T00:00:00", "2026-08-14T12:00:00", None]
    series = pl.Series("CreatedAt", data)

    profile = profile_datetime_column(
        series=series,
        col_name="CreatedAt",
        data_type="datetime",
        total_rows=3,
    )

    assert profile.name == "CreatedAt"
    assert profile.profile_type == "datetime"
    assert profile.null_count == 1
    assert profile.min == "2026-01-01T00:00:00"
    assert profile.max == "2026-08-14T12:00:00"


def test_boolean_profiler_stats():
    data = [True, False, True, None]
    series = pl.Series("IsActive", data)

    profile = profile_boolean_column(
        series=series,
        col_name="IsActive",
        data_type="bit",
        total_rows=4,
    )

    assert profile.name == "IsActive"
    assert profile.profile_type == "boolean"
    assert profile.null_count == 1
    assert profile.null_percent == 25.0
    assert profile.true_count == 2
    assert profile.true_percent == 50.0
    assert profile.false_count == 1
    assert profile.false_percent == 25.0


def test_table_profiler_flow():
    mock_sampler = MagicMock()
    mock_discovery = MagicMock()

    mock_sampler.sample.return_value = TableSampleResponse(
        schema="dbo",
        table="DLPerson",
        requested_rows=100,
        returned_rows=2,
        columns=["PersonID", "Name", "IsActive"],
        rows=[
            {"PersonID": 1, "Name": "Alice", "IsActive": True},
            {"PersonID": 2, "Name": "Bob", "IsActive": False},
        ],
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
        ),
        ColumnInfo(
            ordinal=2,
            name="Name",
            data_type="nvarchar",
            nullable=True,
            identity=False,
            computed=False,
            has_default=False,
        ),
        ColumnInfo(
            ordinal=3,
            name="IsActive",
            data_type="bit",
            nullable=False,
            identity=False,
            computed=False,
            has_default=False,
        ),
    ]

    profiler = TableProfiler(sampler=mock_sampler, discovery=mock_discovery)
    res = profiler.profile_table("dbo", "DLPerson", limit=100)

    assert res.schema_name == "dbo"
    assert res.table == "DLPerson"
    assert res.returned_rows == 2
    assert len(res.columns) == 3
    assert res.columns[0].profile_type == "numeric"
    assert res.columns[1].profile_type == "text"
    assert res.columns[2].profile_type == "boolean"
