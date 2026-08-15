from enum import StrEnum


class SemanticType(StrEnum):
    IDENTIFIER = "IDENTIFIER"

    NAME = "NAME"
    FIRST_NAME = "FIRST_NAME"
    MIDDLE_NAME = "MIDDLE_NAME"
    LAST_NAME = "LAST_NAME"

    EMAIL = "EMAIL"
    PHONE = "PHONE"
    URL = "URL"

    ADDRESS = "ADDRESS"
    STREET = "STREET"
    CITY = "CITY"
    STATE = "STATE"
    COUNTRY = "COUNTRY"
    POSTAL_CODE = "POSTAL_CODE"

    DATE = "DATE"
    DATETIME = "DATETIME"
    CREATED_DATETIME = "CREATED_DATETIME"
    UPDATED_DATETIME = "UPDATED_DATETIME"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"

    AMOUNT = "AMOUNT"
    QUANTITY = "QUANTITY"
    PERCENTAGE = "PERCENTAGE"

    LATITUDE = "LATITUDE"
    LONGITUDE = "LONGITUDE"

    STATUS = "STATUS"
    STATUS_FLAG = "STATUS_FLAG"

    DESCRIPTION = "DESCRIPTION"
    NOTES = "NOTES"

    CODE = "CODE"

    UNKNOWN = "UNKNOWN"


class SensitivityLevel(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PII = "PII"
    SENSITIVE = "SENSITIVE"


SEMANTIC_SENSITIVITY_MAP: dict[SemanticType, tuple[SensitivityLevel, bool]] = {
    # (SensitivityLevel, expose_values)
    SemanticType.EMAIL: (SensitivityLevel.PII, False),
    SemanticType.PHONE: (SensitivityLevel.PII, False),
    SemanticType.FIRST_NAME: (SensitivityLevel.PII, False),
    SemanticType.LAST_NAME: (SensitivityLevel.PII, False),
    SemanticType.MIDDLE_NAME: (SensitivityLevel.PII, False),
    SemanticType.NAME: (SensitivityLevel.PII, False),
    SemanticType.DATE_OF_BIRTH: (SensitivityLevel.PII, False),
    SemanticType.IDENTIFIER: (SensitivityLevel.INTERNAL, True),
    SemanticType.ADDRESS: (SensitivityLevel.INTERNAL, True),
    SemanticType.STREET: (SensitivityLevel.INTERNAL, True),
    SemanticType.POSTAL_CODE: (SensitivityLevel.INTERNAL, True),
    SemanticType.CREATED_DATETIME: (SensitivityLevel.INTERNAL, True),
    SemanticType.UPDATED_DATETIME: (SensitivityLevel.INTERNAL, True),
    SemanticType.STATUS_FLAG: (SensitivityLevel.INTERNAL, True),
    SemanticType.STATUS: (SensitivityLevel.INTERNAL, True),
    SemanticType.CODE: (SensitivityLevel.INTERNAL, True),
    SemanticType.AMOUNT: (SensitivityLevel.INTERNAL, True),
    SemanticType.QUANTITY: (SensitivityLevel.INTERNAL, True),
    SemanticType.PERCENTAGE: (SensitivityLevel.INTERNAL, True),
    SemanticType.CITY: (SensitivityLevel.PUBLIC, True),
    SemanticType.STATE: (SensitivityLevel.PUBLIC, True),
    SemanticType.COUNTRY: (SensitivityLevel.PUBLIC, True),
    SemanticType.LATITUDE: (SensitivityLevel.PUBLIC, True),
    SemanticType.LONGITUDE: (SensitivityLevel.PUBLIC, True),
    SemanticType.DATE: (SensitivityLevel.PUBLIC, True),
    SemanticType.DATETIME: (SensitivityLevel.PUBLIC, True),
    SemanticType.DESCRIPTION: (SensitivityLevel.PUBLIC, True),
    SemanticType.NOTES: (SensitivityLevel.PUBLIC, True),
    SemanticType.URL: (SensitivityLevel.PUBLIC, True),
    SemanticType.UNKNOWN: (SensitivityLevel.PUBLIC, True),
}
