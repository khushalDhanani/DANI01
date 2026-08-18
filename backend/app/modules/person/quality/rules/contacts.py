"""
rules/contacts.py

Dimension 1: Contact & Communication Channels Quality Rules (12 rules).
"""

from app.modules.person.quality.common.contacts import (
    QUALIFYING_EMAIL_EXISTS_SQL,
    QUALIFYING_PHONE_EXISTS_SQL,
)
from app.modules.person.quality.models import (
    ContactQualityIssueType,
    IssueCountUnit,
    QualityRule,
)

# Canonical Predicates
INVALID_EMAIL_WHERE_SQL = """
c.ContactCategory = 'EMAIL'
AND c.TypeValue IS NOT NULL
AND LTRIM(RTRIM(c.TypeValue)) <> ''
AND (
    CASE
        WHEN LEN(LTRIM(RTRIM(c.TypeValue))) > 254 THEN 1
        WHEN LEN(LTRIM(RTRIM(c.TypeValue))) - LEN(REPLACE(LTRIM(RTRIM(c.TypeValue)), '@', '')) <> 1 THEN 1
        WHEN CHARINDEX('@', LTRIM(RTRIM(c.TypeValue))) <= 1 THEN 1
        WHEN CHARINDEX('@', LTRIM(RTRIM(c.TypeValue))) = LEN(LTRIM(RTRIM(c.TypeValue))) THEN 1
        WHEN LTRIM(RTRIM(c.TypeValue)) LIKE '% %'
             OR LTRIM(RTRIM(c.TypeValue)) LIKE '%' + CHAR(9) + '%'
             OR LTRIM(RTRIM(c.TypeValue)) LIKE '%' + CHAR(10) + '%'
             OR LTRIM(RTRIM(c.TypeValue)) LIKE '%' + CHAR(13) + '%' THEN 1
        WHEN CHARINDEX('@', LTRIM(RTRIM(c.TypeValue))) - 1 > 64 THEN 1
        WHEN PATINDEX('%[^a-zA-Z0-9!#$%&''*+/=?^_`{|}~.-]%', LEFT(LTRIM(RTRIM(c.TypeValue)), CHARINDEX('@', LTRIM(RTRIM(c.TypeValue))) - 1)) > 0 THEN 1
        WHEN LEFT(LTRIM(RTRIM(c.TypeValue)), 1) = '.' THEN 1
        WHEN SUBSTRING(LTRIM(RTRIM(c.TypeValue)), CHARINDEX('@', LTRIM(RTRIM(c.TypeValue))) - 1, 1) = '.' THEN 1
        WHEN LEFT(LTRIM(RTRIM(c.TypeValue)), CHARINDEX('@', LTRIM(RTRIM(c.TypeValue)))) LIKE '%..%' THEN 1
        WHEN PATINDEX('%[^a-zA-Z0-9.-]%', RIGHT(LTRIM(RTRIM(c.TypeValue)), LEN(LTRIM(RTRIM(c.TypeValue))) - CHARINDEX('@', LTRIM(RTRIM(c.TypeValue))))) > 0 THEN 1
        WHEN RIGHT(LTRIM(RTRIM(c.TypeValue)), LEN(LTRIM(RTRIM(c.TypeValue))) - CHARINDEX('@', LTRIM(RTRIM(c.TypeValue)))) NOT LIKE '%.%' THEN 1
        WHEN SUBSTRING(LTRIM(RTRIM(c.TypeValue)), CHARINDEX('@', LTRIM(RTRIM(c.TypeValue))) + 1, 1) = '.' THEN 1
        WHEN RIGHT(LTRIM(RTRIM(c.TypeValue)), 1) = '.' THEN 1
        WHEN RIGHT(LTRIM(RTRIM(c.TypeValue)), LEN(LTRIM(RTRIM(c.TypeValue))) - CHARINDEX('@', LTRIM(RTRIM(c.TypeValue)))) LIKE '%..%' THEN 1
        WHEN RIGHT(LTRIM(RTRIM(c.TypeValue)), LEN(LTRIM(RTRIM(c.TypeValue))) - CHARINDEX('@', LTRIM(RTRIM(c.TypeValue)))) LIKE '-%' THEN 1
        WHEN RIGHT(LTRIM(RTRIM(c.TypeValue)), LEN(LTRIM(RTRIM(c.TypeValue))) - CHARINDEX('@', LTRIM(RTRIM(c.TypeValue)))) LIKE '%-' THEN 1
        WHEN RIGHT(LTRIM(RTRIM(c.TypeValue)), LEN(LTRIM(RTRIM(c.TypeValue))) - CHARINDEX('@', LTRIM(RTRIM(c.TypeValue)))) LIKE '%.-%' THEN 1
        WHEN RIGHT(LTRIM(RTRIM(c.TypeValue)), LEN(LTRIM(RTRIM(c.TypeValue))) - CHARINDEX('@', LTRIM(RTRIM(c.TypeValue)))) LIKE '%-.%' THEN 1
        WHEN RIGHT(LTRIM(RTRIM(c.TypeValue)), LEN(LTRIM(RTRIM(c.TypeValue))) - CHARINDEX('@', LTRIM(RTRIM(c.TypeValue)))) LIKE '%' + REPLICATE('[^.]', 64) + '%' THEN 1
        ELSE 0
    END = 1
)
""".strip()

INVALID_PHONE_WHERE_SQL = """
c.ContactCategory = 'PHONE'
AND c.TypeValue IS NOT NULL
AND LTRIM(RTRIM(c.TypeValue)) <> ''
AND (
    (
        c.LabelName = 'Extension'
        AND LEN(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(c.TypeValue)), ' ', ''), '-', ''), '+', ''), '(', ''), ')', ''), '.', ''), '/', '')) <> 4
    )
    OR (
        (c.LabelName <> 'Extension' OR c.LabelName IS NULL)
        AND (
            LEN(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(c.TypeValue)), ' ', ''), '-', ''), '+', ''), '(', ''), ')', ''), '.', ''), '/', '')) < 7
            OR LEN(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(c.TypeValue)), ' ', ''), '-', ''), '+', ''), '(', ''), ')', ''), '.', ''), '/', '')) > 15
        )
    )
)
""".strip()

INVALID_URL_WHERE_SQL = """
c.ContactCategory = 'URL'
AND c.TypeValue IS NOT NULL
AND LTRIM(RTRIM(c.TypeValue)) <> ''
AND (
    c.TypeValue NOT LIKE 'http://%'
    AND c.TypeValue NOT LIKE 'https://%'
    AND c.TypeValue NOT LIKE 'www.%'
)
""".strip()

UNVERIFIED_CONTACT_WHERE_SQL = """
(c.IsVerified = 0 OR c.IsVerified IS NULL)
AND c.TypeValue IS NOT NULL
AND LTRIM(RTRIM(c.TypeValue)) <> ''
""".strip()

DUPLICATE_EMAIL_CROSS_WHERE_SQL = """
c.ContactCategory = 'EMAIL'
AND c.TypeValue IS NOT NULL
AND LTRIM(RTRIM(c.TypeValue)) <> ''
AND c.NormalizedEmail IN (
    SELECT LOWER(LTRIM(RTRIM(sub.TypeValue)))
    FROM ClassifiedContacts sub
    WHERE sub.ContactCategory = 'EMAIL'
      AND sub.TypeValue IS NOT NULL
      AND LTRIM(RTRIM(sub.TypeValue)) <> ''
    GROUP BY LOWER(LTRIM(RTRIM(sub.TypeValue)))
    HAVING COUNT(DISTINCT sub.PersonID) > 1
)
""".strip()

DUPLICATE_PHONE_CROSS_WHERE_SQL = """
c.ContactCategory = 'PHONE'
AND c.TypeValue IS NOT NULL
AND LTRIM(RTRIM(c.TypeValue)) <> ''
AND c.NormalizedPhone IN (
    SELECT sub.NormalizedPhone
    FROM ClassifiedContacts sub
    WHERE sub.ContactCategory = 'PHONE'
      AND sub.TypeValue IS NOT NULL
      AND LTRIM(RTRIM(sub.TypeValue)) <> ''
    GROUP BY sub.NormalizedPhone
    HAVING COUNT(DISTINCT sub.PersonID) > 1
)
""".strip()

DUPLICATE_EMAIL_SAME_WHERE_SQL = """
c.ContactCategory = 'EMAIL'
AND c.TypeValue IS NOT NULL
AND LTRIM(RTRIM(c.TypeValue)) <> ''
AND EXISTS (
    SELECT 1
    FROM ClassifiedContacts dup
    WHERE dup.PersonID = c.PersonID
      AND dup.PersonPhoneID <> c.PersonPhoneID
      AND dup.ContactCategory = 'EMAIL'
      AND dup.NormalizedEmail = c.NormalizedEmail
)
""".strip()

DUPLICATE_PHONE_SAME_WHERE_SQL = """
c.ContactCategory = 'PHONE'
AND c.TypeValue IS NOT NULL
AND LTRIM(RTRIM(c.TypeValue)) <> ''
AND EXISTS (
    SELECT 1
    FROM ClassifiedContacts dup
    WHERE dup.PersonID = c.PersonID
      AND dup.PersonPhoneID <> c.PersonPhoneID
      AND dup.ContactCategory = 'PHONE'
      AND dup.NormalizedPhone = c.NormalizedPhone
)
""".strip()

MULTIPLE_PRIMARY_WHERE_SQL = """
c.IsPrimary = 1
AND c.PersonID IN (
    SELECT sub.PersonID
    FROM ClassifiedContacts sub
    WHERE sub.IsPrimary = 1
    GROUP BY sub.PersonID
    HAVING COUNT_BIG(1) > 1
)
""".strip()

PRIMARY_INACTIVE_WHERE_SQL = """
c.IsPrimary = 1
AND (c.PersonPhoneIsActive = 0 OR c.PersonPhoneIsActive IS NULL)
""".strip()


CONTACT_RULES: list[QualityRule] = [
    QualityRule(
        code=ContactQualityIssueType.MISSING_EMAIL,
        title="Missing Email",
        dimension="CONTACTS",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="persons_without_email",
        description="Active persons without any registered email address",
        target_entity="PERSON",
        predicate_sql=f"NOT {QUALIFYING_EMAIL_EXISTS_SQL}",
        contact_type="EMAIL",
    ),
    QualityRule(
        code=ContactQualityIssueType.MISSING_PHONE,
        title="Missing Phone",
        dimension="CONTACTS",
        severity="WARNING",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="persons_without_phone",
        description="Active persons without any registered phone number",
        target_entity="PERSON",
        predicate_sql=f"NOT {QUALIFYING_PHONE_EXISTS_SQL}",
        contact_type="PHONE",
    ),
    QualityRule(
        code=ContactQualityIssueType.INVALID_EMAIL,
        title="Invalid Email",
        dimension="CONTACTS",
        severity="CRITICAL",
        count_unit=IssueCountUnit.CONTACT,
        unit_label_singular="Contact Record",
        unit_label_plural="Contact Records",
        summary_field="invalid_emails",
        description="Email values that are malformed or contain invalid characters",
        target_entity="CONTACT",
        predicate_sql=INVALID_EMAIL_WHERE_SQL,
        contact_type="EMAIL",
    ),
    QualityRule(
        code=ContactQualityIssueType.INVALID_PHONE,
        title="Invalid Phone / Extension",
        dimension="CONTACTS",
        severity="CRITICAL",
        count_unit=IssueCountUnit.CONTACT,
        unit_label_singular="Contact Record",
        unit_label_plural="Contact Records",
        summary_field="invalid_phones",
        description="Phone numbers not having 7-15 digits or extensions not having exactly 4 digits",
        target_entity="CONTACT",
        predicate_sql=INVALID_PHONE_WHERE_SQL,
        contact_type="PHONE",
    ),
    QualityRule(
        code=ContactQualityIssueType.INVALID_URL,
        title="Invalid URLs",
        dimension="CONTACTS",
        severity="WARNING",
        count_unit=IssueCountUnit.CONTACT,
        unit_label_singular="Contact Record",
        unit_label_plural="Contact Records",
        summary_field="invalid_urls",
        description="Web URLs lacking http://, https://, or www. URI scheme",
        target_entity="CONTACT",
        predicate_sql=INVALID_URL_WHERE_SQL,
        contact_type="URL",
    ),
    QualityRule(
        code=ContactQualityIssueType.UNVERIFIED_CONTACT,
        title="Unverified Contacts",
        dimension="CONTACTS",
        severity="INFO",
        count_unit=IssueCountUnit.CONTACT,
        unit_label_singular="Contact Record",
        unit_label_plural="Contact Records",
        summary_field="unverified_contacts",
        description="Contact channels lacking verified flag status (IsVerified = 0 or NULL)",
        target_entity="CONTACT",
        predicate_sql=UNVERIFIED_CONTACT_WHERE_SQL,
        contact_type="CONTACT",
    ),
    QualityRule(
        code=ContactQualityIssueType.DUPLICATE_EMAIL_CROSS,
        title="Shared Email",
        dimension="CONTACTS",
        severity="WARNING",
        count_unit=IssueCountUnit.DUPLICATE_GROUP,
        unit_label_singular="Shared Email Group",
        unit_label_plural="Shared Email Groups",
        summary_field="duplicate_email_cross_persons",
        description="Identical email address registered across multiple distinct Person entities",
        target_entity="CONTACT",
        predicate_sql=DUPLICATE_EMAIL_CROSS_WHERE_SQL,
        contact_type="EMAIL",
        value_expr_sql="c.NormalizedEmail",
        label_expr_sql="c.NormalizedEmail",
        group_key_sql="c.NormalizedEmail",
        group_label_sql="c.NormalizedEmail",
        group_persons_count_sql="COUNT(DISTINCT c.PersonID)",
        group_records_count_sql="COUNT_BIG(1)",
    ),
    QualityRule(
        code=ContactQualityIssueType.DUPLICATE_PHONE_CROSS,
        title="Shared Phone",
        dimension="CONTACTS",
        severity="WARNING",
        count_unit=IssueCountUnit.DUPLICATE_GROUP,
        unit_label_singular="Shared Phone Group",
        unit_label_plural="Shared Phone Groups",
        summary_field="duplicate_phone_cross_persons",
        description="Identical phone number registered across multiple distinct Person entities",
        target_entity="CONTACT",
        predicate_sql=DUPLICATE_PHONE_CROSS_WHERE_SQL,
        contact_type="PHONE",
        value_expr_sql="c.NormalizedPhone",
        label_expr_sql="c.NormalizedPhone",
        group_key_sql="c.NormalizedPhone",
        group_label_sql="c.NormalizedPhone",
        group_persons_count_sql="COUNT(DISTINCT c.PersonID)",
        group_records_count_sql="COUNT_BIG(1)",
    ),
    QualityRule(
        code=ContactQualityIssueType.DUPLICATE_EMAIL_SAME,
        title="Duplicate Email (Self)",
        dimension="CONTACTS",
        severity="WARNING",
        count_unit=IssueCountUnit.DUPLICATE_GROUP,
        unit_label_singular="Duplicate Email Group",
        unit_label_plural="Duplicate Email Groups",
        summary_field="duplicate_email_same_person",
        description="Duplicate identical email records entered more than once for the same Person",
        target_entity="CONTACT",
        predicate_sql=DUPLICATE_EMAIL_SAME_WHERE_SQL,
        contact_type="EMAIL",
        value_expr_sql="c.NormalizedEmail",
        label_expr_sql="ISNULL(NULLIF(LTRIM(RTRIM(c.TypeValue)), ''), 'Blank Email')",
        group_key_sql="CAST(c.PersonID AS VARCHAR(20)) + '_' + ISNULL(NULLIF(c.NormalizedEmail, ''), 'BLANK')",
        group_label_sql="ISNULL(NULLIF(LTRIM(RTRIM(c.TypeValue)), ''), 'Blank Email')",
        group_persons_count_sql="1",
        group_records_count_sql="COUNT_BIG(1)",
    ),
    QualityRule(
        code=ContactQualityIssueType.DUPLICATE_PHONE_SAME,
        title="Duplicate Phone (Self)",
        dimension="CONTACTS",
        severity="WARNING",
        count_unit=IssueCountUnit.DUPLICATE_GROUP,
        unit_label_singular="Duplicate Phone Group",
        unit_label_plural="Duplicate Phone Groups",
        summary_field="duplicate_phone_same_person",
        description="Duplicate identical phone records entered more than once for the same Person",
        target_entity="CONTACT",
        predicate_sql=DUPLICATE_PHONE_SAME_WHERE_SQL,
        contact_type="PHONE",
        value_expr_sql="c.NormalizedPhone",
        label_expr_sql="ISNULL(NULLIF(LTRIM(RTRIM(c.TypeValue)), ''), 'Blank Phone')",
        group_key_sql="CAST(c.PersonID AS VARCHAR(20)) + '_' + ISNULL(NULLIF(c.NormalizedPhone, ''), 'BLANK')",
        group_label_sql="ISNULL(NULLIF(LTRIM(RTRIM(c.TypeValue)), ''), 'Blank Phone')",
        group_persons_count_sql="1",
        group_records_count_sql="COUNT_BIG(1)",
    ),
    QualityRule(
        code=ContactQualityIssueType.MULTIPLE_PRIMARY,
        title="Multiple Primary Contacts",
        dimension="CONTACTS",
        severity="CRITICAL",
        count_unit=IssueCountUnit.PERSON,
        unit_label_singular="Person",
        unit_label_plural="Persons",
        summary_field="persons_multiple_primary",
        description="Persons with conflicting primary contact flags (more than 1 primary contact)",
        target_entity="CONTACT",
        predicate_sql=MULTIPLE_PRIMARY_WHERE_SQL,
        contact_type="CONTACT",
    ),
    QualityRule(
        code=ContactQualityIssueType.PRIMARY_INACTIVE,
        title="Primary Inactive",
        dimension="CONTACTS",
        severity="CRITICAL",
        count_unit=IssueCountUnit.CONTACT,
        unit_label_singular="Contact Record",
        unit_label_plural="Contact Records",
        summary_field="primary_contact_inactive",
        description="Designated Primary contact record is disabled or marked inactive",
        target_entity="CONTACT",
        predicate_sql=PRIMARY_INACTIVE_WHERE_SQL,
        contact_type="CONTACT",
    ),
]
