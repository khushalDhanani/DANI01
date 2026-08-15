import polars as pl

from app.schemas.profiling import BooleanColumnProfile, ValueFrequency


def profile_boolean_column(
    series: pl.Series,
    col_name: str,
    data_type: str,
    total_rows: int,
) -> BooleanColumnProfile:
    """Profiles boolean and bit columns using Polars."""
    if total_rows == 0:
        return BooleanColumnProfile(
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
    try:
        bool_series = non_null_series.cast(pl.Boolean, strict=False)
    except (pl.exceptions.PolarsError, TypeError, ValueError):
        bool_series = non_null_series

    valid_count = len(bool_series)
    distinct_count = series.n_unique()
    distinct_percent = round((distinct_count / total_rows) * 100, 2)

    true_count = int(bool_series.sum()) if valid_count > 0 else 0
    false_count = int((~bool_series).sum()) if valid_count > 0 else 0

    true_percent = round((true_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
    false_percent = round((false_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

    vc = non_null_series.value_counts(sort=True).head(5)
    top_values = [
        ValueFrequency(
            value=row[0],
            count=int(row[1]),
            percent=round((int(row[1]) / total_rows) * 100, 2),
        )
        for row in vc.iter_rows()
    ]

    return BooleanColumnProfile(
        name=col_name,
        data_type=data_type,
        null_count=null_count,
        null_percent=null_percent,
        distinct_count=distinct_count,
        distinct_percent=distinct_percent,
        true_count=true_count,
        false_count=false_count,
        true_percent=true_percent,
        false_percent=false_percent,
        top_values=top_values,
    )
