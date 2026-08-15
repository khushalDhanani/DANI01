import polars as pl

from app.schemas.profiling import NumericColumnProfile, ValueFrequency


def profile_numeric_column(
    series: pl.Series,
    col_name: str,
    data_type: str,
    total_rows: int,
) -> NumericColumnProfile:
    """Profiles numeric (integer, decimal, float) columns using Polars."""
    if total_rows == 0:
        return NumericColumnProfile(
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
        non_null_floats = non_null_series.cast(pl.Float64, strict=False)
    except (pl.exceptions.PolarsError, TypeError, ValueError):
        non_null_floats = non_null_series

    valid_count = len(non_null_floats)
    distinct_count = series.n_unique()
    distinct_percent = round((distinct_count / total_rows) * 100, 2)

    if valid_count == 0:
        return NumericColumnProfile(
            name=col_name,
            data_type=data_type,
            null_count=null_count,
            null_percent=null_percent,
            distinct_count=distinct_count,
            distinct_percent=distinct_percent,
        )

    # Calculate numeric stats
    min_val = round(float(non_null_floats.min()), 4) if non_null_floats.min() is not None else None
    max_val = round(float(non_null_floats.max()), 4) if non_null_floats.max() is not None else None
    mean_val = (
        round(float(non_null_floats.mean()), 4) if non_null_floats.mean() is not None else None
    )
    median_val = (
        round(float(non_null_floats.median()), 4) if non_null_floats.median() is not None else None
    )
    std_val = round(float(non_null_floats.std()), 4) if non_null_floats.std() is not None else None

    zero_mask = non_null_floats == 0
    zero_count = int(zero_mask.sum())
    zero_percent = round((zero_count / total_rows) * 100, 2)

    negative_mask = non_null_floats < 0
    negative_count = int(negative_mask.sum())
    negative_percent = round((negative_count / total_rows) * 100, 2)

    # Top values
    vc = non_null_series.value_counts(sort=True).head(5)
    top_values = [
        ValueFrequency(
            value=row[0],
            count=int(row[1]),
            percent=round((int(row[1]) / total_rows) * 100, 2),
        )
        for row in vc.iter_rows()
    ]

    return NumericColumnProfile(
        name=col_name,
        data_type=data_type,
        null_count=null_count,
        null_percent=null_percent,
        distinct_count=distinct_count,
        distinct_percent=distinct_percent,
        min=min_val,
        max=max_val,
        mean=mean_val,
        median=median_val,
        std_dev=std_val,
        zero_count=zero_count,
        zero_percent=zero_percent,
        negative_count=negative_count,
        negative_percent=negative_percent,
        top_values=top_values,
    )
