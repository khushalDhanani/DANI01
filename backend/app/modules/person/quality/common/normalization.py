"""
normalization.py

SQL expressions and functions for normalizing strings, emails, phone numbers, and addresses.
"""


def normalize_email_sql(column: str = "c.TypeValue") -> str:
    return f"LOWER(LTRIM(RTRIM({column})))"


def normalize_phone_sql(column: str = "c.TypeValue") -> str:
    return f"REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM({column})), ' ', ''), '-', ''), '+', ''), '(', ''), ')', ''), '.', ''), '/', '')"


def normalize_address_street_sql(column: str = "a.Street") -> str:
    return f"LOWER(LTRIM(RTRIM({column})))"


def normalize_address_city_sql(column: str = "a.CityName") -> str:
    return f"ISNULL(LOWER(LTRIM(RTRIM({column}))), '')"


def normalize_address_postal_sql(column: str = "a.PostalCode") -> str:
    return f"ISNULL(LOWER(LTRIM(RTRIM({column}))), '')"
