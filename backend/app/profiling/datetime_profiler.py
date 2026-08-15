import polars as pl

from app.schemas.profiling import DateTimeColumnProfile, ValueFrequency


def profile_datetime_column(
    series: pl.Series,
    col_name: str,
    data_type: str,
    total_rows: int,
) -> DateTimeColumnProfile:
    """Profiles datetime, date, and time columns using Polars."""
    if total_rows == 0:
        return DateTimeColumnProfile(
            name=col_name,
            data_type=data_type,
            null_count=0,
            null_percent=0.0,
            distinct_count=0,
            distinct_percent=0.0,
        )

    null_count = series.null_count()
    null_percent = round((null_count / total_rows) * 100, 2)

    non_null_series = series.drop_nulls()
    valid_count = len(non_null_series)
    distinct_count = series.n_unique()
    distinct_percent = round((distinct_count / total_rows) * 100, 2)

    if valid_count == 0:
        return DateTimeColumnProfile(
            name=col_name,
            data_type=data_type,
            null_count=null_count,
            null_percent=null_percent,
            distinct_count=distinct_count,
            distinct_percent=distinct_percent,
        )

    min_val = str(non_null_series.min()) if non_null_series.min() is not None else None
    max_val = str(non_null_series.max()) if non_null_series.max() is not None else None

    vc = non_null_series.value_counts(sort=True).head(5)
    top_values = [
        ValueFrequency(
            value=str(row[0]),
            count=int(row[1]),
            percent=round((int(row[1]) / total_rows) * 100, 2),
        )
        for row in vc.iter_rows()
    ]

    return DateTimeColumnProfile(
        name=col_name,
        data_type=data_type,
        null_count=null_count,
        null_percent=null_percent,
        distinct_count=distinct_count,
        distinct_percent=distinct_percent,
        min=min_val,
        max=max_val,
        top_values=top_values,
    )
