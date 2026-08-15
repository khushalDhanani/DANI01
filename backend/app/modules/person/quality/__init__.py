"""
Daylite Person Quality package.
Exports the core Quality Service, Registry, Models, and Exporters.
"""

from app.modules.person.quality.compiler import (
    compile_drilldown_queries,
    compile_group_queries,
    compile_summary_query,
)
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
from app.modules.person.quality.registry import (
    QUALITY_RULES_REGISTRY,
    RULE_METADATA,
    get_all_quality_rules,
    get_quality_rule,
)
from app.modules.person.quality.service import ContactQualityService

__all__ = [
    "QUALITY_RULES_REGISTRY",
    "RULE_METADATA",
    "ContactQualityGroupItem",
    "ContactQualityGroupMember",
    "ContactQualityIssueItem",
    "ContactQualityIssueType",
    "ContactQualityIssuesResponse",
    "ContactQualityService",
    "ContactQualitySummaryResponse",
    "IssueCountUnit",
    "QualityDimension",
    "QualityRule",
    "QualityRuleMeta",
    "TargetEntity",
    "compile_drilldown_queries",
    "compile_group_queries",
    "compile_summary_query",
    "get_all_quality_rules",
    "get_quality_rule",
]
