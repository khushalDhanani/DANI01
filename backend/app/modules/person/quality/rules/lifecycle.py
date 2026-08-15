"""
rules/lifecycle.py

Dimension 4: Employment & Status Lifecycle Quality Rules (4 rules).
"""

from app.modules.person.quality.models import (
    ContactQualityIssueType,
    IssueCountUnit,
    QualityRule,
)

# Canonical Predicates
ACTIVE_EMP_MISSING_TITLE_WHERE_SQL = """
p.EmpID IS NOT NULL 
AND LTRIM(RTRIM(p.EmpID)) <> ''
AND (p.PersonTitle IS NULL OR LTRIM(RTRIM(p.PersonTitle)) = '')
""".strip()

INACTIVE_WITH_EMPID_WHERE_SQL = """
p.PersonIsActive = 0
AND (p.PersonIsDeleted = 0 OR p.PersonIsDeleted IS NULL)
AND p.EmpID IS NOT NULL 
AND LTRIM(RTRIM(p.EmpID)) <> ''
""".strip()

STATUS_ACTIVE_AND_DELETED_WHERE_SQL = """
p.PersonIsActive = 1 
AND p.PersonIsDeleted = 1
""".strip()

STALE_TEMP_PERSONS_WHERE_SQL = """
p.PersonIsTemp = 1 
AND DATEDIFF(day, p.PersonEntDt, GETDATE()) > 90
""".strip()


LIFECYCLE_RULES: list[QualityRule] = [
    QualityRule(
        code=ContactQualityIssueType.ACTIVE_EMP_MISSING_TITLE,
        title="Active Employee Missing Title",
        dimension="EMPLOYMENT",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="active_emp_missing_title",
        description="Active employee record having EmpID but missing job designation title",
        target_entity="PERSON",
        predicate_sql=ACTIVE_EMP_MISSING_TITLE_WHERE_SQL,
        contact_type="EMPLOYEE",
        value_expr_sql="p.EmpID",
        label_expr_sql="'Employee ID'",
    ),
    QualityRule(
        code=ContactQualityIssueType.INACTIVE_WITH_ACTIVE_EMPID,
        title="Inactive Holding Employee ID",
        dimension="EMPLOYMENT",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="inactive_with_empid",
        description="Person record marked inactive (PersonIsActive = 0) while still retaining active EmpID",
        target_entity="PERSON",
        predicate_sql=INACTIVE_WITH_EMPID_WHERE_SQL,
        requires_active_person=False,
        contact_type="EMPLOYEE",
        value_expr_sql="p.EmpID",
        label_expr_sql="'Employee ID'",
    ),
    QualityRule(
        code=ContactQualityIssueType.STATUS_ACTIVE_AND_DELETED,
        title="Conflicting Status Flags",
        dimension="EMPLOYMENT",
        severity="CRITICAL",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="status_active_and_deleted",
        description="Person record has contradictory status flags (both PersonIsActive = 1 AND PersonIsDeleted = 1)",
        target_entity="PERSON",
        predicate_sql=STATUS_ACTIVE_AND_DELETED_WHERE_SQL,
        requires_active_person=False,
        contact_type="STATUS",
        value_expr_sql="'Active=1, Deleted=1'",
        label_expr_sql="'Status Flags'",
    ),
    QualityRule(
        code=ContactQualityIssueType.STALE_TEMP_PERSONS,
        title="Stale Temporary Records",
        dimension="EMPLOYMENT",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="stale_temp_persons",
        description="Temporary person record created more than 90 days ago that has not been converted",
        target_entity="PERSON",
        predicate_sql=STALE_TEMP_PERSONS_WHERE_SQL,
        contact_type="STATUS",
        value_expr_sql="CONVERT(VARCHAR(10), p.PersonEntDt, 120)",
        label_expr_sql="'Created Date'",
    ),
]
