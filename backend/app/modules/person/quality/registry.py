"""
registry.py

Central quality rule registry for Daylite Person domain.
Aggregates rules across all 6 dimensions into a single declarative registry.
"""

from app.modules.person.quality.common import (
    ACTIVE_PERSON_WHERE_SQL,
    CLASSIFIED_CONTACTS_CTE_SQL,
    PERSON_NAME_SQL,
    QUALIFYING_EMAIL_EXISTS_SQL,
    QUALIFYING_PHONE_EXISTS_SQL,
)
from app.modules.person.quality.models import (
    ContactQualityIssueType,
    QualityDimension,
    QualityRule,
    QualityRuleMeta,
    TargetEntity,
)
from app.modules.person.quality.rules import (
    ACTIVE_EMP_MISSING_TITLE_WHERE_SQL,
    ADDR_CITY_WITHOUT_STATE_WHERE_SQL,
    ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL,
    ADDR_INVALID_PIN_FORMAT_WHERE_SQL,
    ADDR_MISSING_GEOCODES_WHERE_SQL,
    ADDR_MISSING_POSTAL_CODE_WHERE_SQL,
    ADDR_STREET_WITHOUT_CITY_WHERE_SQL,
    ADDRESS_RULES,
    ALL_RULES,
    AUDIT_DEL_BEFORE_ENT_WHERE_SQL,
    AUDIT_RULES,
    BLACKLIST_MISSING_DETAILS_WHERE_SQL,
    BLACKLIST_UNAPPROVED_WHERE_SQL,
    COMPANY_DUPLICATE_LINKS_WHERE_SQL,
    COMPANY_MISSING_ROLE_WHERE_SQL,
    COMPANY_ORPHAN_LINKS_WHERE_SQL,
    CONTACT_RULES,
    DELETED_MISSING_DEL_DATE_WHERE_SQL,
    DUPLICATE_EMAIL_CROSS_WHERE_SQL,
    DUPLICATE_EMAIL_SAME_WHERE_SQL,
    DUPLICATE_EXTRA_FIELDS_WHERE_SQL,
    DUPLICATE_PHONE_CROSS_WHERE_SQL,
    DUPLICATE_PHONE_SAME_WHERE_SQL,
    EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL,
    EXTRA_FIELD_ORPHAN_ID_WHERE_SQL,
    GOVERNANCE_RULES,
    INACTIVE_WITH_EMPID_WHERE_SQL,
    INVALID_EMAIL_WHERE_SQL,
    INVALID_PHONE_WHERE_SQL,
    INVALID_URL_WHERE_SQL,
    LIFECYCLE_RULES,
    MULTIPLE_PRIMARY_WHERE_SQL,
    PERSON_ANNIVERSARY_BEFORE_BIRTH_WHERE_SQL,
    PERSON_BIRTH_DATE_ANCIENT_WHERE_SQL,
    PERSON_INVALID_BIRTH_DATE_WHERE_SQL,
    PERSON_MISSING_LASTNAME_ONLY_WHERE_SQL,
    PERSON_SUSPICIOUS_DUMMY_NAMES_WHERE_SQL,
    PRIMARY_INACTIVE_WHERE_SQL,
    PROFILE_RULES,
    STALE_TEMP_PERSONS_WHERE_SQL,
    STATUS_ACTIVE_AND_DELETED_WHERE_SQL,
    SYNC_ZIMBRA_MISSING_ID_WHERE_SQL,
    UNVERIFIED_CONTACT_WHERE_SQL,
)
from app.modules.person.quality.rules.base import PersonQualityRule
from app.modules.person.quality.rules.completeness import (
    PersonMissingAddressRule,
    PersonMissingCompanyLinkRule,
    PersonMissingContactRule,
    PersonMissingEmailRule,
    PersonMissingPhoneRule,
)
from app.modules.person.quality.rules.consistency import (
    PersonCreatedAfterUpdatedRule,
    PersonSelfRelationshipRule,
)
from app.modules.person.quality.rules.integrity import (
    PersonOrphanAddressRule,
    PersonOrphanCompanyLinkRule,
    PersonOrphanContactRule,
    PersonOrphanRelationshipRule,
)
from app.modules.person.quality.rules.validity import (
    PersonInvalidEmailRule,
    PersonInvalidLatitudeRule,
    PersonInvalidLongitudeRule,
    PersonInvalidPhoneRule,
    PersonInvalidUrlRule,
)

# Central SSoT Registry
QUALITY_RULES_REGISTRY: dict[ContactQualityIssueType, QualityRule] = {
    rule.code: rule for rule in ALL_RULES
}

# Compatibility metadata dictionary
RULE_METADATA: dict[ContactQualityIssueType, QualityRuleMeta] = {
    rule.code: QualityRuleMeta(
        code=rule.code,
        title=rule.title,
        dimension=rule.dimension,
        severity=rule.severity,
        count_unit=rule.count_unit,
        unit_label_singular=rule.unit_label_singular,
        unit_label_plural=rule.unit_label_plural,
        description=rule.description,
    )
    for rule in ALL_RULES
}


def get_quality_rule(issue: str | ContactQualityIssueType) -> QualityRule | None:
    if isinstance(issue, ContactQualityIssueType):
        return QUALITY_RULES_REGISTRY.get(issue)
    try:
        norm_key = ContactQualityIssueType(issue.strip().upper())
        return QUALITY_RULES_REGISTRY.get(norm_key)
    except (ValueError, KeyError, AttributeError):
        return None


def get_all_quality_rules() -> list[QualityRule]:
    return list(QUALITY_RULES_REGISTRY.values())


class PersonQualityRuleRegistry:
    def __init__(self) -> None:
        self._rules: dict[str, PersonQualityRule] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        defaults: list[PersonQualityRule] = [
            PersonMissingEmailRule(),
            PersonMissingPhoneRule(),
            PersonMissingContactRule(),
            PersonMissingAddressRule(),
            PersonMissingCompanyLinkRule(),
            PersonInvalidEmailRule(),
            PersonInvalidPhoneRule(),
            PersonInvalidUrlRule(),
            PersonInvalidLatitudeRule(),
            PersonInvalidLongitudeRule(),
            PersonOrphanContactRule(),
            PersonOrphanAddressRule(),
            PersonOrphanCompanyLinkRule(),
            PersonOrphanRelationshipRule(),
            PersonCreatedAfterUpdatedRule(),
            PersonSelfRelationshipRule(),
        ]
        for r in defaults:
            self._rules[r.rule_code] = r

    def get_all_rules(self) -> list[PersonQualityRule]:
        return list(self._rules.values())

    def get_rule(self, code: str) -> PersonQualityRule | None:
        return self._rules.get(code)


person_quality_rule_registry = PersonQualityRuleRegistry()


__all__ = [
    "ACTIVE_EMP_MISSING_TITLE_WHERE_SQL",
    "ACTIVE_PERSON_WHERE_SQL",
    "ADDRESS_RULES",
    "ADDR_CITY_WITHOUT_STATE_WHERE_SQL",
    "ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL",
    "ADDR_INVALID_PIN_FORMAT_WHERE_SQL",
    "ADDR_MISSING_GEOCODES_WHERE_SQL",
    "ADDR_MISSING_POSTAL_CODE_WHERE_SQL",
    "ADDR_STREET_WITHOUT_CITY_WHERE_SQL",
    "ALL_RULES",
    "AUDIT_DEL_BEFORE_ENT_WHERE_SQL",
    "AUDIT_RULES",
    "BLACKLIST_MISSING_DETAILS_WHERE_SQL",
    "BLACKLIST_UNAPPROVED_WHERE_SQL",
    "CLASSIFIED_CONTACTS_CTE_SQL",
    "COMPANY_DUPLICATE_LINKS_WHERE_SQL",
    "COMPANY_MISSING_ROLE_WHERE_SQL",
    "COMPANY_ORPHAN_LINKS_WHERE_SQL",
    "CONTACT_RULES",
    "DELETED_MISSING_DEL_DATE_WHERE_SQL",
    "DUPLICATE_EMAIL_CROSS_WHERE_SQL",
    "DUPLICATE_EMAIL_SAME_WHERE_SQL",
    "DUPLICATE_EXTRA_FIELDS_WHERE_SQL",
    "DUPLICATE_PHONE_CROSS_WHERE_SQL",
    "DUPLICATE_PHONE_SAME_WHERE_SQL",
    "EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL",
    "EXTRA_FIELD_ORPHAN_ID_WHERE_SQL",
    "GOVERNANCE_RULES",
    "INACTIVE_WITH_EMPID_WHERE_SQL",
    "INVALID_EMAIL_WHERE_SQL",
    "INVALID_PHONE_WHERE_SQL",
    "INVALID_URL_WHERE_SQL",
    "LIFECYCLE_RULES",
    "MULTIPLE_PRIMARY_WHERE_SQL",
    "PERSON_ANNIVERSARY_BEFORE_BIRTH_WHERE_SQL",
    "PERSON_BIRTH_DATE_ANCIENT_WHERE_SQL",
    "PERSON_INVALID_BIRTH_DATE_WHERE_SQL",
    "PERSON_MISSING_LASTNAME_ONLY_WHERE_SQL",
    "PERSON_NAME_SQL",
    "PERSON_SUSPICIOUS_DUMMY_NAMES_WHERE_SQL",
    "PRIMARY_INACTIVE_WHERE_SQL",
    "PROFILE_RULES",
    "QUALIFYING_EMAIL_EXISTS_SQL",
    "QUALIFYING_PHONE_EXISTS_SQL",
    "QUALITY_RULES_REGISTRY",
    "RULE_METADATA",
    "STALE_TEMP_PERSONS_WHERE_SQL",
    "STATUS_ACTIVE_AND_DELETED_WHERE_SQL",
    "SYNC_ZIMBRA_MISSING_ID_WHERE_SQL",
    "UNVERIFIED_CONTACT_WHERE_SQL",
    "QualityDimension",
    "QualityRule",
    "QualityRuleMeta",
    "TargetEntity",
    "get_all_quality_rules",
    "get_quality_rule",
]
