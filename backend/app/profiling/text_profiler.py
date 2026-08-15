import polars as pl

from app.schemas.profiling import TextColumnProfile, ValueFrequency


def profile_text_column(
    series: pl.Series,
    col_name: str,
    data_type: str,
    total_rows: int,
) -> TextColumnProfile:
    """Profiles text/string columns using Polars, distinguishing empty vs whitespace blanks."""
    if total_rows == 0:
        return TextColumnProfile(
            name=col_name,
            data_type=data_type,
            null_count=0,
            null_percent=0.0,
            distinct_count=0,
            distinct_percent=0.0,
        )

    null_count = series.null_count()
    null_percent = round((null_count / total_rows) * 100, 2)

    # Filter non-null strings
    non_null_series = series.drop_nulls()
    if non_null_series.dtype != pl.String:
        non_null_series = non_null_series.cast(pl.String)

    valid_count = len(non_null_series)
    distinct_count = series.n_unique()
    distinct_percent = round((distinct_count / total_rows) * 100, 2)

    if valid_count == 0:
        return TextColumnProfile(
            name=col_name,
            data_type=data_type,
            null_count=null_count,
            null_percent=null_percent,
            distinct_count=distinct_count,
            distinct_percent=distinct_percent,
        )

    # Empty vs Blank discrimination
    empty_mask = non_null_series == ""
    empty_count = int(empty_mask.sum())
    empty_percent = round((empty_count / total_rows) * 100, 2)

    # Blank: whitespace only and length > 0
    stripped = non_null_series.str.strip_chars()
    blank_mask = (stripped == "") & (~empty_mask)
    blank_count = int(blank_mask.sum())
    blank_percent = round((blank_count / total_rows) * 100, 2)

    # Length statistics
    lengths = non_null_series.str.len_chars()
    min_len = int(lengths.min()) if lengths.min() is not None else None
    max_len = int(lengths.max()) if lengths.max() is not None else None
    avg_len = round(float(lengths.mean()), 2) if lengths.mean() is not None else None

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

    return TextColumnProfile(
        name=col_name,
        data_type=data_type,
        null_count=null_count,
        null_percent=null_percent,
        distinct_count=distinct_count,
        distinct_percent=distinct_percent,
        empty_count=empty_count,
        empty_percent=empty_percent,
        blank_count=blank_count,
        blank_percent=blank_percent,
        min_length=min_len,
        max_length=max_len,
        avg_length=avg_len,
        top_values=top_values,
    )
