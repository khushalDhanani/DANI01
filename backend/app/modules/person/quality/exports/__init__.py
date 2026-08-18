"""
exports package for Daylite Person Quality engine.
"""

from datetime import UTC, datetime
from typing import Any

from app.modules.person.quality.exports.csv import generate_csv
from app.modules.person.quality.exports.excel import generate_xlsx
from app.modules.person.quality.models import (
    ContactQualityIssueItem,
    ContactQualitySummaryResponse,
)
from app.modules.person.quality.rules import ALL_RULES

_DIMENSION_DISPLAY_MAP: dict[str, str] = {
    "CONTACTS": "1. Contact & Communications",
    "ADDRESSES": "2. Address & Locations",
    "PROFILE": "3. Profile & Chronology",
    "EMPLOYMENT": "4. Employment & Lifecycle",
    "GOVERNANCE": "5. Governance, Linkages & Sync",
}


def export_summary_report(
    summary: ContactQualitySummaryResponse,
    format: str = "xlsx",
) -> tuple[bytes, str, str]:
    """
    Exports the 37-KPI quality summary report as CSV or Excel.
    Derived dynamically from ALL_RULES.
    """
    is_csv = format.lower().strip() == "csv"
    ext = "csv" if is_csv else "xlsx"
    media_type = (
        "text/csv; charset=utf-8"
        if is_csv
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    filename = f"daylite_quality_summary_{date_str}.{ext}"

    headers = [
        "Quality Dimension",
        "Rule Title",
        "Issue Code",
        "Severity",
        "Count Unit",
        "Affected Count",
        "Description",
    ]

    rows: list[list[Any]] = []
    for rule in ALL_RULES:
        val = getattr(summary, rule.summary_field, 0)
        rows.append(
            [
                _DIMENSION_DISPLAY_MAP.get(rule.dimension, rule.dimension),
                rule.title,
                rule.code.value,
                rule.severity,
                rule.unit_label_plural,
                val,
                rule.description,
            ]
        )

    if is_csv:
        content = generate_csv(headers, rows)
    else:
        content = generate_xlsx("Daylite Quality Summary", headers, rows)

    return content, media_type, filename


def export_issues_dataset(
    items: list[ContactQualityIssueItem],
    issue_code: str,
    format: str = "xlsx",
) -> tuple[bytes, str, str]:
    """
    Exports a list of ContactQualityIssueItem records as CSV or Excel.
    """
    is_csv = format.lower().strip() == "csv"
    ext = "csv" if is_csv else "xlsx"
    media_type = (
        "text/csv; charset=utf-8"
        if is_csv
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    filename = f"daylite_{issue_code.lower()}_{date_str}.{ext}"

    headers = [
        "Person ID",
        "Person Name",
        "Issue Code",
        "Severity",
        "Contact Type",
        "Field Label",
        "Offending Value",
        "Issue Description",
        "Is Active",
    ]

    data_rows: list[list[Any]] = []
    for item in items:
        data_rows.append(
            [
                item.person_id,
                item.person_name,
                item.issue_code,
                item.severity,
                item.contact_type,
                item.label_name or "",
                item.masked_value or item.current_value or "",
                item.issue_description,
                "Yes" if item.is_active else "No",
            ]
        )

    if is_csv:
        content = generate_csv(headers, data_rows)
    else:
        content = generate_xlsx(f"{issue_code} Issues", headers, data_rows)

    return content, media_type, filename


__all__ = [
    "export_issues_dataset",
    "export_summary_report",
    "generate_csv",
    "generate_xlsx",
]
