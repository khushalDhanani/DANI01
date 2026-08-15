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


class PersonQualityRuleRegistry:
    """
    Registry providing the standard suite of PERSON data quality rules.
    """

    def __init__(self) -> None:
        self._rules: list[PersonQualityRule] = [
            # 1. Completeness Rules
            PersonMissingAddressRule(),
            PersonMissingContactRule(),
            PersonMissingEmailRule(),
            PersonMissingPhoneRule(),
            PersonMissingCompanyLinkRule(),
            # 2. Validity Rules
            PersonInvalidEmailRule(),
            PersonInvalidPhoneRule(),
            PersonInvalidUrlRule(),
            PersonInvalidLatitudeRule(),
            PersonInvalidLongitudeRule(),
            # 3. Integrity Rules
            PersonOrphanAddressRule(),
            PersonOrphanContactRule(),
            PersonOrphanCompanyLinkRule(),
            PersonOrphanRelationshipRule(),
            # 4. Consistency Rules
            PersonSelfRelationshipRule(),
            PersonCreatedAfterUpdatedRule(),
        ]

    def get_all_rules(self) -> list[PersonQualityRule]:
        return list(self._rules)


person_quality_rule_registry = PersonQualityRuleRegistry()
