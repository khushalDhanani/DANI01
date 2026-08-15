"""initial analysis persistence

Revision ID: 001_initial_analysis
Revises: 
Create Date: 2026-08-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_analysis"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. analysis_runs
    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("database_name", sa.String(length=128), nullable=False),
        sa.Column("analysis_type", sa.String(length=64), server_default="QUICK", nullable=False),
        sa.Column("schema_filter", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("tables_total", sa.Integer(), server_default="0", nullable=False),
        sa.Column("tables_completed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("tables_skipped", sa.Integer(), server_default="0", nullable=False),
        sa.Column("tables_failed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("columns_discovered", sa.Integer(), server_default="0", nullable=False),
        sa.Column("columns_profiled", sa.Integer(), server_default="0", nullable=False),
        sa.Column("columns_classified", sa.Integer(), server_default="0", nullable=False),
        sa.Column("progress_percent", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Float(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("celery_task_id", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_analysis_runs_status", "analysis_runs", ["status"])

    # 2. analysis_errors
    op.create_table(
        "analysis_errors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=36), sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("schema_name", sa.String(length=128), nullable=True),
        sa.Column("table_name", sa.String(length=128), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_analysis_errors_run_id", "analysis_errors", ["run_id"])

    # 3. analysis_table_results
    op.create_table(
        "analysis_table_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=36), sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("schema_name", sa.String(length=128), nullable=False),
        sa.Column("table_name", sa.String(length=128), nullable=False),
        sa.Column("estimated_rows", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("sample_size", sa.Integer(), server_default="0", nullable=False),
        sa.Column("returned_rows", sa.Integer(), server_default="0", nullable=False),
        sa.Column("column_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("profiled_columns", sa.Integer(), server_default="0", nullable=False),
        sa.Column("classified_columns", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("skip_reason", sa.String(length=64), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Float(), server_default="0.0", nullable=False),
        sa.UniqueConstraint("run_id", "schema_name", "table_name", name="uq_run_schema_table"),
    )
    op.create_index("ix_analysis_table_results_run_id", "analysis_table_results", ["run_id"])
    op.create_index("ix_analysis_table_results_status", "analysis_table_results", ["status"])

    # 4. analysis_table_timings
    op.create_table(
        "analysis_table_timings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("table_result_id", sa.Integer(), sa.ForeignKey("analysis_table_results.id", ondelete="CASCADE"), nullable=False),
        sa.Column("structure_duration_ms", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("sampling_duration_ms", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("profiling_duration_ms", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("classification_duration_ms", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("total_duration_ms", sa.Float(), server_default="0.0", nullable=False),
        sa.UniqueConstraint("table_result_id", name="uq_timing_table_result_id"),
    )
    op.create_index("ix_analysis_table_timings_table_result_id", "analysis_table_timings", ["table_result_id"])

    # 5. analysis_column_profiles
    op.create_table(
        "analysis_column_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("table_result_id", sa.Integer(), sa.ForeignKey("analysis_table_results.id", ondelete="CASCADE"), nullable=False),
        sa.Column("column_name", sa.String(length=128), nullable=False),
        sa.Column("data_type", sa.String(length=64), nullable=False),
        sa.Column("profile_type", sa.String(length=32), server_default="generic", nullable=False),
        sa.Column("null_count", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("null_percent", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("distinct_count", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("distinct_percent", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("top_values", sa.JSON(), nullable=True),
        sa.Column("stats", sa.JSON(), nullable=True),
    )
    op.create_index("ix_analysis_column_profiles_table_result_id", "analysis_column_profiles", ["table_result_id"])

    # 6. analysis_column_classifications
    op.create_table(
        "analysis_column_classifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("table_result_id", sa.Integer(), sa.ForeignKey("analysis_table_results.id", ondelete="CASCADE"), nullable=False),
        sa.Column("column_name", sa.String(length=128), nullable=False),
        sa.Column("sql_type", sa.String(length=64), nullable=False),
        sa.Column("semantic_type", sa.String(length=64), nullable=False),
        sa.Column("sensitivity", sa.String(length=32), nullable=False),
        sa.Column("expose_values", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("confidence", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("signals", sa.JSON(), nullable=True),
    )
    op.create_index("ix_analysis_column_classifications_table_result_id", "analysis_column_classifications", ["table_result_id"])


def downgrade() -> None:
    op.drop_table("analysis_column_classifications")
    op.drop_table("analysis_column_profiles")
    op.drop_table("analysis_table_timings")
    op.drop_table("analysis_table_results")
    op.drop_table("analysis_errors")
    op.drop_table("analysis_runs")
