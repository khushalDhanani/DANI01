import pytest
from app.db.mssql import execute_readonly_query
from app.modules.person.quality.rules.contacts import INVALID_EMAIL_WHERE_SQL

VALID_EMAILS = [
    "john@example.com",
    "john.doe@example.com",
    "john_doe@example.com",
    "john-doe@example.com",
    "john+sales@example.com",
    "john123@example.com",
    "o'connor@example.com",
    "sales+india@company.co.in",
    "john@sub.example.com",
    "user_name@example-domain.com",
    "12345@example.com",
    "a" * 64 + "@example.com",
    "john@" + "a" * 63 + ".com",
]

INVALID_EMAILS = [
    "john",
    "john@",
    "@example.com",
    "john@@example.com",
    "john@abc@example.com",
    ".john@example.com",
    "john.@example.com",
    "john..doe@example.com",
    "john@example",
    "john@.example.com",
    "john@example.com.",
    "john@example..com",
    "john@-example.com",
    "john@example-.com",
    "john@example_domain.com",
    "john doe@example.com",
    "john@ example.com",
    "john@example .com",
    "a" * 65 + "@example.com",
    "john@" + "a" * 64 + ".com",
    "a" * 64 + "@" + "b" * 63 + "." + "c" * 63 + "." + "d" * 63 + ".com"
]

def test_email_sql_validation_valid_cases():
    valid_exact_254 = "a" * 64 + "@" + "b" * 63 + "." + "c" * 63 + "." + "d" * 59
    cases = VALID_EMAILS.copy()
    cases.append(valid_exact_254)
    
    sql_logic = INVALID_EMAIL_WHERE_SQL.split("AND (")[1].rsplit(")", 1)[0].strip()
    if sql_logic.endswith("= 1"):
        sql_logic = sql_logic[:-3].strip()
    
    for email in cases:
        query = f"""
        DECLARE @val NVARCHAR(500) = '{email.replace("'", "''")}';
        SELECT {sql_logic.replace("c.TypeValue", "@val")} AS IsInvalid
        """
        result = execute_readonly_query(query)
        assert result[0]["IsInvalid"] == 0, f"Expected {email} to be VALID, but SQL flagged it as INVALID."

def test_email_sql_validation_invalid_cases():
    sql_logic = INVALID_EMAIL_WHERE_SQL.split("AND (")[1].rsplit(")", 1)[0].strip()
    if sql_logic.endswith("= 1"):
        sql_logic = sql_logic[:-3].strip()
    
    for email in INVALID_EMAILS:
        query = f"""
        DECLARE @val NVARCHAR(500) = '{email.replace("'", "''")}';
        SELECT {sql_logic.replace("c.TypeValue", "@val")} AS IsInvalid
        """
        result = execute_readonly_query(query)
        assert result[0]["IsInvalid"] == 1, f"Expected {email} to be INVALID, but SQL flagged it as VALID."
