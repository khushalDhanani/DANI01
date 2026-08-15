"""
rules/audit.py

Dimension 6: Audit Trail & External System Sync Integration Rules (3 rules).
"""

from app.modules.person.quality.models import (
    ContactQualityIssueType,
    IssueCountUnit,
    QualityRule,
)

# Canonical Predicates
DELETED_MISSING_DEL_DATE_WHERE_SQL = """
p.PersonIsDeleted = 1 
AND p.PersonDelDt IS NULL
""".strip()

AUDIT_DEL_BEFORE_ENT_WHERE_SQL = """
p.PersonIsDeleted = 1 
AND p.PersonDelDt IS NOT NULL 
AND p.PersonDelDt < p.PersonEntDt
""".strip()

SYNC_ZIMBRA_MISSING_ID_WHERE_SQL = """
p.IsContactSync = 1 
AND (p.ZimbraContactID IS NULL OR LTRIM(RTRIM(p.ZimbraContactID)) = '')
""".strip()


AUDIT_RULES: list[QualityRule] = [
    QualityRule(
        code=ContactQualityIssueType.DELETED_MISSING_TIMESTAMP,
        title="Deleted Without Timestamp",
        dimension="GOVERNANCE",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="deleted_missing_del_date",
        description="Record is flagged as deleted but has no deletion timestamp (PersonDelDt is NULL)",
        target_entity="PERSON",
        predicate_sql=DELETED_MISSING_DEL_DATE_WHERE_SQL,
        requires_active_person=False,
        contact_type="AUDIT",
        value_expr_sql="'Deleted=1, DelDt=NULL'",
        label_expr_sql="'Audit Timestamp'",
    ),
    QualityRule(
        code=ContactQualityIssueType.AUDIT_DEL_BEFORE_ENT,
        title="Deletion Before Creation",
        dimension="GOVERNANCE",
        severity="CRITICAL",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="audit_del_before_ent",
        description="Deletion timestamp is earlier than creation timestamp (audit log corruption)",
        target_entity="PERSON",
        predicate_sql=AUDIT_DEL_BEFORE_ENT_WHERE_SQL,
        requires_active_person=False,
        contact_type="AUDIT",
        value_expr_sql="CONVERT(VARCHAR(10), p.PersonDelDt, 120) + ' < ' + CONVERT(VARCHAR(10), p.PersonEntDt, 120)",
        label_expr_sql="'Deletion / Creation'",
    ),
    QualityRule(
        code=ContactQualityIssueType.SYNC_ZIMBRA_MISSING_ID,
        title="Broken Zimbra Sync",
        dimension="GOVERNANCE",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="sync_zimbra_missing_id",
        description="Sync is enabled on record but Zimbra Contact ID is missing or null",
        target_entity="PERSON",
        predicate_sql=SYNC_ZIMBRA_MISSING_ID_WHERE_SQL,
        contact_type="SYNC",
        value_expr_sql="'Sync=1, ZimbraID=NULL'",
        label_expr_sql="'Zimbra Sync ID'",
    ),
]
