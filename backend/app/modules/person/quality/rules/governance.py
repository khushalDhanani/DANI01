"""
rules/governance.py

Dimension 5: Governance, Blacklist Compliance & Entity Linkage Rules (7 rules).
"""

from app.modules.person.quality.models import (
    ContactQualityIssueType,
    IssueCountUnit,
    QualityRule,
)

# Canonical Predicates
BLACKLIST_UNAPPROVED_WHERE_SQL = """
p.PersonIsBlackList = 1
AND (p.PersonBlackListHODApprove IS NULL OR p.PersonBlackListHODApprove = 0)
""".strip()

BLACKLIST_MISSING_DETAILS_WHERE_SQL = """
p.PersonIsBlackList = 1
AND (
    p.PersonBlackListDate IS NULL
    OR p.PersonBlackListType IS NULL
    OR LTRIM(RTRIM(CAST(p.PersonBlackListType AS VARCHAR(100)))) = ''
)
""".strip()

COMPANY_ORPHAN_LINKS_WHERE_SQL = """
l.DLCompID IS NOT NULL
AND l.DLCompID > 0
AND NOT EXISTS (
    SELECT 1
    FROM dbo.DLCompanyMst c
    WHERE c.DLCompID = l.DLCompID
)
""".strip()

COMPANY_DUPLICATE_LINKS_WHERE_SQL = """
l.DLCompID IS NOT NULL
AND l.DLCompID > 0
AND EXISTS (
    SELECT 1
    FROM dbo.DLPersonCompanyLinkDet dup
    WHERE dup.PersonID = l.PersonID
      AND dup.PersonLinkID <> l.PersonLinkID
      AND dup.DLCompID = l.DLCompID
)
""".strip()

COMPANY_MISSING_ROLE_WHERE_SQL = """
l.DLCompID IS NOT NULL
AND l.DLCompID > 0
AND (l.CompPersonRoleID IS NULL OR l.CompPersonRoleID = 0)
""".strip()

EXTRA_FIELD_ORPHAN_ID_WHERE_SQL = """
e.ExtraFieldID IS NOT NULL
AND e.ExtraFieldID > 0
AND NOT EXISTS (
    SELECT 1
    FROM dbo.DLExtraFieldDet ef
    WHERE ef.ExtraFieldID = e.ExtraFieldID
)
""".strip()

EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL = """
e.ExtraFieldID IS NOT NULL
AND e.ExtraFieldID > 0
AND EXISTS (
    SELECT 1
    FROM dbo.DLPersonExtraFieldValueDet dup
    WHERE dup.PersonID = e.PersonID
      AND dup.PersonExtraFieldValueID <> e.PersonExtraFieldValueID
      AND dup.ExtraFieldID = e.ExtraFieldID
)
""".strip()

DUPLICATE_EXTRA_FIELDS_WHERE_SQL = EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL


GOVERNANCE_RULES: list[QualityRule] = [
    QualityRule(
        code=ContactQualityIssueType.BLACKLIST_UNAPPROVED,
        title="Unapproved Blacklist",
        dimension="GOVERNANCE",
        severity="CRITICAL",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="blacklist_unapproved",
        description="Person is flagged as blacklisted without required Head-of-Department (HOD) sign-off",
        target_entity="PERSON",
        predicate_sql=BLACKLIST_UNAPPROVED_WHERE_SQL,
        contact_type="BLACKLIST",
        value_expr_sql="'Blacklisted without HOD Sign-off'",
        label_expr_sql="'Blacklist Approval'",
    ),
    QualityRule(
        code=ContactQualityIssueType.BLACKLIST_MISSING_DETAILS,
        title="Blacklist Missing Details",
        dimension="GOVERNANCE",
        severity="CRITICAL",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="blacklist_missing_details",
        description="Blacklisted person record is missing blacklist timestamp or reason category",
        target_entity="PERSON",
        predicate_sql=BLACKLIST_MISSING_DETAILS_WHERE_SQL,
        contact_type="BLACKLIST",
        value_expr_sql="'Missing Date/Reason'",
        label_expr_sql="'Blacklist Metadata'",
    ),
    QualityRule(
        code=ContactQualityIssueType.ORPHAN_COMPANY_LINK,
        title="Orphan Company Link",
        dimension="GOVERNANCE",
        severity="CRITICAL",
        count_unit=IssueCountUnit.COMPANY_LINK,
        unit_label_singular="Company Link Record",
        unit_label_plural="Company Link Records",
        summary_field="company_orphan_links",
        description="Company affiliation link references a non-existent company ID in DLCompanyMst",
        target_entity="COMPANY_LINK",
        predicate_sql=COMPANY_ORPHAN_LINKS_WHERE_SQL,
        contact_type="COMPANY_LINK",
        value_expr_sql="'Company #' + CAST(l.DLCompID AS VARCHAR(20))",
        label_expr_sql="'Company Link'",
    ),
    QualityRule(
        code=ContactQualityIssueType.DUPLICATE_COMPANY_LINKS,
        title="Duplicate Company Links",
        dimension="GOVERNANCE",
        severity="WARNING",
        count_unit=IssueCountUnit.DUPLICATE_GROUP,
        unit_label_singular="Duplicate Link Group",
        unit_label_plural="Duplicate Link Groups",
        summary_field="company_duplicate_links",
        description="Same company entity is linked multiple times to the same Person",
        target_entity="COMPANY_LINK",
        predicate_sql=COMPANY_DUPLICATE_LINKS_WHERE_SQL,
        contact_type="COMPANY_LINK",
        value_expr_sql="'Company #' + CAST(l.DLCompID AS VARCHAR(20))",
        label_expr_sql="'Company Link'",
        group_key_sql="CAST(l.DLCompID AS VARCHAR(20))",
        group_label_sql="'Company #' + CAST(l.DLCompID AS VARCHAR(20))",
        group_persons_count_sql="1",
        group_records_count_sql="COUNT_BIG(1)",
    ),
    QualityRule(
        code=ContactQualityIssueType.COMPANY_MISSING_ROLE,
        title="Company Missing Role",
        dimension="GOVERNANCE",
        severity="WARNING",
        count_unit=IssueCountUnit.COMPANY_LINK,
        unit_label_singular="Company Link Record",
        unit_label_plural="Company Link Records",
        summary_field="company_missing_role",
        description="Company affiliation link is missing designation role (CompPersonRoleID = 0/NULL)",
        target_entity="COMPANY_LINK",
        predicate_sql=COMPANY_MISSING_ROLE_WHERE_SQL,
        contact_type="COMPANY_LINK",
        value_expr_sql="'Company #' + CAST(l.DLCompID AS VARCHAR(20))",
        label_expr_sql="'Designation Role'",
    ),
    QualityRule(
        code=ContactQualityIssueType.EXTRA_FIELD_ORPHAN_ID,
        title="Orphan Extra Field",
        dimension="GOVERNANCE",
        severity="CRITICAL",
        count_unit=IssueCountUnit.EXTRA_FIELD,
        unit_label_singular="Custom Field Record",
        unit_label_plural="Custom Field Records",
        summary_field="extra_field_orphan_id",
        description="Custom field value references an invalid or deleted ExtraField schema ID",
        target_entity="EXTRA_FIELD",
        predicate_sql=EXTRA_FIELD_ORPHAN_ID_WHERE_SQL,
        contact_type="CUSTOM_FIELD",
        value_expr_sql="e.PersonExtraFieldValue",
        label_expr_sql="'Field ID ' + CAST(e.ExtraFieldID AS VARCHAR(20))",
    ),
    QualityRule(
        code=ContactQualityIssueType.DUPLICATE_EXTRA_FIELDS,
        title="Duplicate Extra Fields",
        dimension="GOVERNANCE",
        severity="WARNING",
        count_unit=IssueCountUnit.DUPLICATE_GROUP,
        unit_label_singular="Duplicate Field Group",
        unit_label_plural="Duplicate Field Groups",
        summary_field="extra_field_duplicate_entries",
        description="Duplicate custom field value entries recorded under the same Person",
        target_entity="EXTRA_FIELD",
        predicate_sql=EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL,
        contact_type="CUSTOM_FIELD",
        value_expr_sql="e.PersonExtraFieldValue",
        label_expr_sql="'Field ID ' + CAST(e.ExtraFieldID AS VARCHAR(20))",
        group_key_sql="CAST(e.ExtraFieldID AS VARCHAR(20))",
        group_label_sql="'Field ID ' + CAST(e.ExtraFieldID AS VARCHAR(20))",
        group_persons_count_sql="1",
        group_records_count_sql="COUNT_BIG(1)",
    ),
]
