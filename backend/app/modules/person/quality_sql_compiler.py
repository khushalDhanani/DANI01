"""
quality_sql_compiler.py

Backward-compatibility facade forwarding to app.modules.person.quality.compiler.
"""

from app.modules.person.quality.compiler import (
    PERSON_NAME_SQL,
    compile_drilldown_queries,
    compile_group_queries,
    compile_summary_query,
    resolve_order_clause,
)

__all__ = [
    "PERSON_NAME_SQL",
    "compile_drilldown_queries",
    "compile_group_queries",
    "compile_summary_query",
    "resolve_order_clause",
]
