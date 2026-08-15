"""
rules/profile.py

Dimension 3: Profile & Chronological Integrity Quality Rules (5 rules).
"""

from app.modules.person.quality.models import (
    ContactQualityIssueType,
    IssueCountUnit,
    QualityRule,
)

# Canonical Predicates
PERSON_ANNIVERSARY_BEFORE_BIRTH_WHERE_SQL = """
p.PersonAnneversaryDate IS NOT NULL
AND p.PersonBirthDate IS NOT NULL
AND p.PersonAnneversaryDate < p.PersonBirthDate
""".strip()

PERSON_INVALID_BIRTH_DATE_WHERE_SQL = """
p.PersonBirthDate IS NOT NULL
AND (
    p.PersonBirthDate > GETDATE()
    OR p.PersonBirthDate < '1900-01-01'
)
""".strip()

PERSON_BIRTH_DATE_ANCIENT_WHERE_SQL = """
p.PersonBirthDate IS NOT NULL
AND (
    CAST(p.PersonBirthDate AS DATE) = '1900-01-01'
    OR DATEDIFF(year, p.PersonBirthDate, GETDATE()) > 100
)
""".strip()

PERSON_SUSPICIOUS_DUMMY_NAMES_WHERE_SQL = """
(
    LOWER(LTRIM(RTRIM(ISNULL(p.PersonFirstName, '')))) IN ('test', 'dummy', 'asdf', 'admin', 'na', 'n/a', 'null', 'unknown', 'none', 'temp', 'demo', 'user')
    OR LOWER(LTRIM(RTRIM(ISNULL(p.PersonLastName, '')))) IN ('test', 'dummy', 'asdf', 'admin', 'na', 'n/a', 'null', 'unknown', 'none', 'temp', 'demo', 'user')
    OR LOWER(ISNULL(p.PersonFirstName, '')) LIKE '%test test%'
    OR LOWER(ISNULL(p.PersonLastName, '')) LIKE '%test test%'
)
""".strip()

PERSON_MISSING_LASTNAME_ONLY_WHERE_SQL = """
p.PersonFirstName IS NOT NULL
AND LTRIM(RTRIM(p.PersonFirstName)) <> ''
AND (p.PersonLastName IS NULL OR LTRIM(RTRIM(p.PersonLastName)) = '')
""".strip()


PROFILE_RULES: list[QualityRule] = [
    QualityRule(
        code=ContactQualityIssueType.ANNIVERSARY_BEFORE_BIRTH,
        title="Anniversary Before Birth",
        dimension="PROFILE",
        severity="CRITICAL",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="person_anniversary_before_birth",
        description="Wedding/anniversary date is chronologically earlier than date of birth",
        target_entity="PERSON",
        predicate_sql=PERSON_ANNIVERSARY_BEFORE_BIRTH_WHERE_SQL,
        contact_type="PROFILE",
        value_expr_sql="CONVERT(VARCHAR(10), p.PersonAnneversaryDate, 120) + ' < ' + CONVERT(VARCHAR(10), p.PersonBirthDate, 120)",
        label_expr_sql="'Anniversary / Birth'",
    ),
    QualityRule(
        code=ContactQualityIssueType.INVALID_BIRTH_DATE,
        title="Future / Invalid Birth Date",
        dimension="PROFILE",
        severity="CRITICAL",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="person_invalid_birth_date",
        description="Birth date is in the future or occurs before the year 1900",
        target_entity="PERSON",
        predicate_sql=PERSON_INVALID_BIRTH_DATE_WHERE_SQL,
        contact_type="PROFILE",
        value_expr_sql="CONVERT(VARCHAR(10), p.PersonBirthDate, 120)",
        label_expr_sql="'Birth Date'",
    ),
    QualityRule(
        code=ContactQualityIssueType.BIRTH_DATE_DEFAULT_OR_ANCIENT,
        title="Ancient / Default Birth Date",
        dimension="PROFILE",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="person_birth_date_ancient",
        description="Default placeholder 1900-01-01 or calculated person age exceeding 100 years",
        target_entity="PERSON",
        predicate_sql=PERSON_BIRTH_DATE_ANCIENT_WHERE_SQL,
        contact_type="PROFILE",
        value_expr_sql="CONVERT(VARCHAR(10), p.PersonBirthDate, 120)",
        label_expr_sql="'Birth Date'",
    ),
    QualityRule(
        code=ContactQualityIssueType.SUSPICIOUS_DUMMY_NAMES,
        title="Suspicious / Dummy Names",
        dimension="PROFILE",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="person_suspicious_dummy_names",
        description="First or last name contains placeholder keywords e.g. test, admin, dummy, asdf",
        target_entity="PERSON",
        predicate_sql=PERSON_SUSPICIOUS_DUMMY_NAMES_WHERE_SQL,
        contact_type="PROFILE",
        value_expr_sql="ISNULL(p.PersonFirstName, '') + ' ' + ISNULL(p.PersonLastName, '')",
        label_expr_sql="'Full Name'",
    ),
    QualityRule(
        code=ContactQualityIssueType.MISSING_LAST_NAME,
        title="Missing Last Name",
        dimension="PROFILE",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="person_missing_lastname_only",
        description="Person has first name populated but is missing family/last name",
        target_entity="PERSON",
        predicate_sql=PERSON_MISSING_LASTNAME_ONLY_WHERE_SQL,
        contact_type="PROFILE",
        value_expr_sql="p.PersonFirstName",
        label_expr_sql="'First Name'",
    ),
]
