import logging

import polars as pl

from app.discovery.metadata import MetadataDiscovery
from app.profiling.column_profiler import profile_column
from app.sampling.sampler import TableSampler
from app.schemas.profiling import TableProfileResponse

logger = logging.getLogger(__name__)


class TableProfiler:
    def __init__(
        self,
        sampler: TableSampler | None = None,
        discovery: MetadataDiscovery | None = None,
    ):
        self.sampler = sampler or TableSampler()
        self.discovery = discovery or MetadataDiscovery()

    def profile_table(
        self,
        schema_name: str,
        table_name: str,
        limit: int = 1000,
    ) -> TableProfileResponse:
        """
        Profiles a table by taking a safe sample, building an in-memory
        Polars DataFrame, and extracting statistical summaries per column.
        """
        # 1. Fetch safe sample
        sample = self.sampler.sample(schema_name, table_name, limit=limit)

        # 2. Fetch structural column metadata
        columns_meta = self.discovery.get_columns(schema_name, table_name)
        col_type_map = {col.name: col.data_type for col in columns_meta}

        # 3. Create Polars DataFrame in-memory
        total_rows = sample.returned_rows
        if total_rows > 0 and sample.rows:
            try:
                # Infer schema across all sampled rows
                df = pl.DataFrame(sample.rows, infer_schema_length=None, strict=False)
            except Exception:
                # Fallback: Construct series column-by-column
                col_data = {
                    col: [row.get(col) for row in sample.rows]
                    for col in sample.columns
                }
                df = pl.DataFrame(col_data, strict=False)
        else:
            # Empty DataFrame with string/null schema
            df = pl.DataFrame(
                {col.name: [] for col in columns_meta},
                strict=False,
            )

        # 4. Profile each column
        column_profiles = []
        for col_name in sample.columns:
            data_type = col_type_map.get(col_name, "varchar")
            if col_name in df.columns:
                series = df[col_name]
            else:
                series = pl.Series(col_name, [None] * total_rows)

            profile = profile_column(
                series=series,
                col_name=col_name,
                data_type=data_type,
                total_rows=total_rows,
            )
            column_profiles.append(profile)

        return TableProfileResponse(
            schema_name=sample.schema_name,
            table=sample.table,
            sample_size=sample.requested_rows,
            returned_rows=sample.returned_rows,
            columns=column_profiles,
        )
