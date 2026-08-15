"""
exports/csv.py

CSV report generation utilities for Daylite Person Quality findings and summaries.
"""

import csv
import io
from typing import Any


def generate_csv(headers: list[str], rows: list[list[Any]]) -> bytes:
    """
    Encodes tabular headers and rows as UTF-8 CSV bytes.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for r in rows:
        writer.writerow(r)
    return output.getvalue().encode("utf-8")
