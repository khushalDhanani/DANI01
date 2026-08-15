"""
common package for Daylite Person Quality engine.
"""

from app.modules.person.quality.common.contacts import (
    CLASSIFIED_CONTACTS_CTE_SQL,
    QUALIFYING_EMAIL_EXISTS_SQL,
    QUALIFYING_PHONE_EXISTS_SQL,
)
from app.modules.person.quality.common.normalization import (
    normalize_address_city_sql,
    normalize_address_postal_sql,
    normalize_address_street_sql,
    normalize_email_sql,
    normalize_phone_sql,
)
from app.modules.person.quality.common.persons import (
    ACTIVE_PERSON_WHERE_SQL,
    PERSON_NAME_SQL,
)

__all__ = [
    "ACTIVE_PERSON_WHERE_SQL",
    "CLASSIFIED_CONTACTS_CTE_SQL",
    "PERSON_NAME_SQL",
    "QUALIFYING_EMAIL_EXISTS_SQL",
    "QUALIFYING_PHONE_EXISTS_SQL",
    "normalize_address_city_sql",
    "normalize_address_postal_sql",
    "normalize_address_street_sql",
    "normalize_email_sql",
    "normalize_phone_sql",
]
