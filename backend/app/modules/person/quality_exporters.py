"""
quality_exporters.py

Backward-compatibility facade forwarding to app.modules.person.quality.exports.
"""

from app.modules.person.quality.exports import (
    export_issues_dataset,
    export_summary_report,
    generate_csv,
    generate_xlsx,
)

__all__ = [
    "export_issues_dataset",
    "export_summary_report",
    "generate_csv",
    "generate_xlsx",
]
