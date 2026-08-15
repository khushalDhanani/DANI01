"""
rules/addresses.py

Dimension 2: Physical Address & Location Quality Rules (6 rules).
"""

from app.modules.person.quality.models import (
    ContactQualityIssueType,
    IssueCountUnit,
    QualityRule,
)

# Canonical Predicates
ADDR_MISSING_POSTAL_CODE_WHERE_SQL = """
(a.PostalCode IS NULL OR LTRIM(RTRIM(a.PostalCode)) = '')
""".strip()

ADDR_INVALID_PIN_FORMAT_WHERE_SQL = """
a.PostalCode IS NOT NULL
AND LTRIM(RTRIM(a.PostalCode)) <> ''
AND (
    LEN(LTRIM(RTRIM(a.PostalCode))) NOT IN (5, 6)
    OR a.PostalCode LIKE '%[^0-9]%'
)
""".strip()

ADDR_STREET_WITHOUT_CITY_WHERE_SQL = """
a.Street IS NOT NULL
AND LTRIM(RTRIM(a.Street)) <> ''
AND (a.CityName IS NULL OR LTRIM(RTRIM(a.CityName)) = '')
""".strip()

ADDR_CITY_WITHOUT_STATE_WHERE_SQL = """
a.CityName IS NOT NULL
AND LTRIM(RTRIM(a.CityName)) <> ''
AND (a.StateName IS NULL OR LTRIM(RTRIM(a.StateName)) = '')
""".strip()

ADDR_MISSING_GEOCODES_WHERE_SQL = """
(a.Latitude IS NULL OR a.Longitude IS NULL OR a.Latitude = 0 OR a.Longitude = 0)
""".strip()

ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL = """
EXISTS (
    SELECT 1
    FROM dbo.DLPersonAddressDet a2
    WHERE a2.PersonID = a.PersonID
      AND a2.PersonAddID <> a.PersonAddID
      AND LOWER(LTRIM(RTRIM(a2.Street))) = LOWER(LTRIM(RTRIM(a.Street)))
      AND ISNULL(LOWER(LTRIM(RTRIM(a2.CityName))), '') = ISNULL(LOWER(LTRIM(RTRIM(a.CityName))), '')
      AND ISNULL(LOWER(LTRIM(RTRIM(a2.PostalCode))), '') = ISNULL(LOWER(LTRIM(RTRIM(a.PostalCode))), '')
)
""".strip()


ADDRESS_RULES: list[QualityRule] = [
    QualityRule(
        code=ContactQualityIssueType.MISSING_POSTAL_CODE,
        title="Missing Postal Code",
        dimension="ADDRESSES",
        severity="WARNING",
        count_unit=IssueCountUnit.ADDRESS,
        unit_label_singular="Address Record",
        unit_label_plural="Address Records",
        summary_field="addr_missing_postal_code",
        description="Address records without a postal / PIN code",
        target_entity="ADDRESS",
        predicate_sql=ADDR_MISSING_POSTAL_CODE_WHERE_SQL,
        contact_type="ADDRESS",
        value_expr_sql="a.Street",
        label_expr_sql="a.AddressTypeName",
    ),
    QualityRule(
        code=ContactQualityIssueType.INVALID_PIN_CODE_FORMAT,
        title="Invalid PIN Code Format",
        dimension="ADDRESSES",
        severity="CRITICAL",
        count_unit=IssueCountUnit.ADDRESS,
        unit_label_singular="Address Record",
        unit_label_plural="Address Records",
        summary_field="addr_invalid_pin_format",
        description="Postal code length is not 5 or 6 digits, or contains non-numeric characters",
        target_entity="ADDRESS",
        predicate_sql=ADDR_INVALID_PIN_FORMAT_WHERE_SQL,
        contact_type="ADDRESS",
        value_expr_sql="a.PostalCode",
        label_expr_sql="a.AddressTypeName",
    ),
    QualityRule(
        code=ContactQualityIssueType.STREET_WITHOUT_CITY,
        title="Street Without City",
        dimension="ADDRESSES",
        severity="WARNING",
        count_unit=IssueCountUnit.ADDRESS,
        unit_label_singular="Address Record",
        unit_label_plural="Address Records",
        summary_field="addr_street_without_city",
        description="Address line has street location populated but missing city name",
        target_entity="ADDRESS",
        predicate_sql=ADDR_STREET_WITHOUT_CITY_WHERE_SQL,
        contact_type="ADDRESS",
        value_expr_sql="a.Street",
        label_expr_sql="a.AddressTypeName",
    ),
    QualityRule(
        code=ContactQualityIssueType.CITY_WITHOUT_STATE,
        title="City Without State",
        dimension="ADDRESSES",
        severity="WARNING",
        count_unit=IssueCountUnit.ADDRESS,
        unit_label_singular="Address Record",
        unit_label_plural="Address Records",
        summary_field="addr_city_without_state",
        description="Address has city name populated but missing state or region",
        target_entity="ADDRESS",
        predicate_sql=ADDR_CITY_WITHOUT_STATE_WHERE_SQL,
        contact_type="ADDRESS",
        value_expr_sql="a.CityName",
        label_expr_sql="a.AddressTypeName",
    ),
    QualityRule(
        code=ContactQualityIssueType.MISSING_GEOCODES,
        title="Missing Coordinates",
        dimension="ADDRESSES",
        severity="INFO",
        count_unit=IssueCountUnit.ADDRESS,
        unit_label_singular="Address Record",
        unit_label_plural="Address Records",
        summary_field="addr_missing_geocodes",
        description="Physical address missing GPS latitude and longitude coordinates",
        target_entity="ADDRESS",
        predicate_sql=ADDR_MISSING_GEOCODES_WHERE_SQL,
        contact_type="ADDRESS",
        value_expr_sql="ISNULL(a.Street, a.CityName)",
        label_expr_sql="a.AddressTypeName",
    ),
    QualityRule(
        code=ContactQualityIssueType.DUPLICATE_ADDRESSES_SAME_PERSON,
        title="Duplicate Address (Self)",
        dimension="ADDRESSES",
        severity="WARNING",
        count_unit=IssueCountUnit.DUPLICATE_GROUP,
        unit_label_singular="Duplicate Address Group",
        unit_label_plural="Duplicate Address Groups",
        summary_field="addr_duplicate_same_person",
        description="Identical address details (Street, City, PostalCode) entered multiple times for same Person",
        target_entity="ADDRESS",
        predicate_sql=ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL,
        contact_type="ADDRESS",
        value_expr_sql="a.Street",
        label_expr_sql="a.AddressTypeName",
        group_key_sql="LOWER(LTRIM(RTRIM(a.Street)))",
        group_label_sql="a.Street",
        group_persons_count_sql="1",
        group_records_count_sql="COUNT_BIG(1)",
    ),
]
