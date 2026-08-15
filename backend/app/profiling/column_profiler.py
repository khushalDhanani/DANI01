import polars as pl

from app.profiling.boolean_profiler import profile_boolean_column
from app.profiling.datetime_profiler import profile_datetime_column
from app.profiling.numeric_profiler import profile_numeric_column
from app.profiling.text_profiler import profile_text_column
from app.schemas.profiling import BaseColumnProfile, ValueFrequency

TEXT_TYPES = {
    "varchar",
    "nvarchar",
    "char",
    "nchar",
    "text",
    "ntext",
    "xml",
    "uniqueidentifier",
    "sysname",
}
NUMERIC_TYPES = {
    "int",
    "bigint",
    "smallint",
    "tinyint",
    "decimal",
    "numeric",
    "float",
    "real",
    "money",
    "smallmoney",
}
DATETIME_TYPES = {
    "datetime",
    "datetime2",
    "date",
    "time",
    "smalldatetime",
    "datetimeoffset",
}
BOOLEAN_TYPES = {"bit", "bool", "boolean"}


def profile_column(
    series: pl.Series,
    col_name: str,
    data_type: str,
    total_rows: int,
):
    """Dispatches column series to the appropriate profiler based on SQL datatype."""
    dt_lower = data_type.lower()

    if dt_lower in TEXT_TYPES:
        return profile_text_column(series, col_name, data_type, total_rows)
    elif dt_lower in NUMERIC_TYPES:
        return profile_numeric_column(series, col_name, data_type, total_rows)
    elif dt_lower in DATETIME_TYPES:
        return profile_datetime_column(series, col_name, data_type, total_rows)
    elif dt_lower in BOOLEAN_TYPES:
        return profile_boolean_column(series, col_name, data_type, total_rows)
    else:
        # Generic / Binary fallback
        null_count = series.null_count()
        null_percent = round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
        non_null_series = series.drop_nulls()
        distinct_count = series.n_unique()
        distinct_percent = round((distinct_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

        vc = non_null_series.value_counts(sort=True).head(5)
        top_values = [
            ValueFrequency(
                value=str(row[0]),
                count=int(row[1]),
                percent=round((int(row[1]) / total_rows) * 100, 2),
            )
            for row in vc.iter_rows()
        ]

        return BaseColumnProfile(
            name=col_name,
            data_type=data_type,
            profile_type="binary" if "binary" in dt_lower or "image" in dt_lower else "generic",
            null_count=null_count,
            null_percent=null_percent,
            distinct_count=distinct_count,
            distinct_percent=distinct_percent,
            top_values=top_values,
        )
