"""
contact_quality_schemas.py

Backward-compatibility facade forwarding to app.modules.person.quality.models and quality.registry.
"""

from app.modules.person.quality.models import (
    ContactQualityGroupItem,
    ContactQualityGroupMember,
    ContactQualityIssueItem,
    ContactQualityIssuesResponse,
    ContactQualityIssueType,
    ContactQualitySummaryResponse,
    IssueCountUnit,
    QualityDimension,
    QualityRule,
    QualityRuleMeta,
    TargetEntity,
)
from app.modules.person.quality.registry import RULE_METADATA

__all__ = [
    "RULE_METADATA",
    "ContactQualityGroupItem",
    "ContactQualityGroupMember",
    "ContactQualityIssueItem",
    "ContactQualityIssueType",
    "ContactQualityIssuesResponse",
    "ContactQualitySummaryResponse",
    "IssueCountUnit",
    "QualityDimension",
    "QualityRule",
    "QualityRuleMeta",
    "TargetEntity",
]
