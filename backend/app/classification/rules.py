import re
from typing import Any

from app.classification.taxonomy import SemanticType
from app.schemas.database import ColumnInfo


def classify_column_signals(
    column: ColumnInfo,
    sample_values: list[Any] | None = None,
) -> tuple[SemanticType, float, list[str]]:
    """
    Evaluates column metadata, naming patterns, SQL datatype, PK/FK flags,
    and sample values to determine the SemanticType, confidence score, and matched signals.
    """
    name = column.name
    name_clean = re.sub(r"[^a-zA-Z0-9]", "", name).lower()
    sql_type = column.data_type.lower()
    signals: list[str] = []

    # 1. Primary Key / Foreign Key Identifier
    if (column.primary_key or column.foreign_key) and (
        name_clean.endswith("id") or name_clean == "id" or "id" in name_clean
    ):
        if column.primary_key:
            signals.append("primary_key")
        if column.foreign_key:
            signals.append("foreign_key")
        signals.append("column_name_suffix_id")
        return SemanticType.IDENTIFIER, 1.0, signals

    # Non-PK/FK ID match
    if name_clean.endswith("id") or name_clean == "id":
        signals.append("column_name_suffix_id")
        return SemanticType.IDENTIFIER, 0.95, signals

    if name_clean in {"guid", "uuid"} or sql_type == "uniqueidentifier":
        signals.append("datatype_uniqueidentifier_or_guid")
        return SemanticType.IDENTIFIER, 0.98, signals

    # 2. Email
    if "email" in name_clean or "mail" in name_clean:
        signals.append("column_name_email_match")
        return SemanticType.EMAIL, 0.98, signals

    # 3. Phone
    if any(p in name_clean for p in ("phone", "mobile", "cellphone", "telephone", "fax")):
        signals.append("column_name_phone_match")
        return SemanticType.PHONE, 0.95, signals

    # 4. URL
    if any(u in name_clean for u in ("url", "website", "link", "webpage", "locationmapurl")):
        signals.append("column_name_url_match")
        return SemanticType.URL, 0.98, signals

    # 5. Latitude / Longitude
    if name_clean in {"latitude", "lat"} or name_clean.endswith("latitude"):
        signals.append("column_name_latitude_match")
        return SemanticType.LATITUDE, 0.99, signals

    if name_clean in {"longitude", "long", "lon", "lng"} or name_clean.endswith(
        ("longitude", "lng")
    ):
        signals.append("column_name_longitude_match")
        return SemanticType.LONGITUDE, 0.99, signals

    # 6. Postal Code
    if any(pc in name_clean for pc in ("postalcode", "zipcode", "zip", "pincode", "postcode")):
        signals.append("column_name_postalcode_match")
        return SemanticType.POSTAL_CODE, 0.98, signals

    # 7. Street / Address
    if any(
        st in name_clean
        for st in ("street", "streetaddress", "addressline", "address1", "address2")
    ):
        signals.append("column_name_street_match")
        return SemanticType.STREET, 0.98, signals

    if (
        any(addr in name_clean for addr in ("address", "addr", "location"))
        and "url" not in name_clean
    ):
        signals.append("column_name_address_match")
        return SemanticType.ADDRESS, 0.92, signals

    # 8. City / State / Country
    if name_clean in {"cityname", "city"} or name_clean.endswith("cityname"):
        signals.append("column_name_city_match")
        return SemanticType.CITY, 0.98, signals

    if any(st in name_clean for st in ("statename", "state", "province", "region")):
        signals.append("column_name_state_match")
        return SemanticType.STATE, 0.98, signals

    if name_clean in {"countryname", "country"} or name_clean.endswith("countryname"):
        signals.append("column_name_country_match")
        return SemanticType.COUNTRY, 0.98, signals

    # 9. First / Middle / Last / Full Name
    if any(fn in name_clean for fn in ("firstname", "fname", "first_name")):
        signals.append("column_name_firstname_match")
        return SemanticType.FIRST_NAME, 0.98, signals

    if any(ln in name_clean for ln in ("lastname", "lname", "surname", "last_name")):
        signals.append("column_name_lastname_match")
        return SemanticType.LAST_NAME, 0.98, signals

    if any(mn in name_clean for mn in ("middlename", "mname", "middle_name")):
        signals.append("column_name_middlename_match")
        return SemanticType.MIDDLE_NAME, 0.98, signals

    if any(
        n in name_clean for n in ("fullname", "personname", "username", "customername", "empname")
    ):
        signals.append("column_name_name_match")
        return SemanticType.NAME, 0.95, signals

    # 10. Date of Birth
    if any(dob in name_clean for dob in ("dob", "dateofbirth", "birthdate")):
        signals.append("column_name_date_of_birth_match")
        return SemanticType.DATE_OF_BIRTH, 0.99, signals

    # 11. Created / Updated DateTime
    if any(
        c in name_clean
        for c in (
            "entdt",
            "createddt",
            "createdat",
            "createdon",
            "creationdate",
            "insertdate",
            "entrydate",
        )
    ):
        signals.append("column_name_created_datetime_match")
        return SemanticType.CREATED_DATETIME, 0.98, signals

    if any(
        u in name_clean
        for u in (
            "upddt",
            "updateddt",
            "updatedat",
            "updatedon",
            "modificationdate",
            "modifiedon",
            "deldt",
            "deleteddt",
        )
    ):
        signals.append("column_name_updated_datetime_match")
        return SemanticType.UPDATED_DATETIME, 0.98, signals

    # 12. Status Flags / Status
    if sql_type in {"bit", "bool", "boolean"}:
        signals.append("datatype_boolean_status_flag")
        return SemanticType.STATUS_FLAG, 0.98, signals

    if any(
        f in name_clean
        for f in (
            "isactive",
            "isdeleted",
            "isdelted",
            "isdefault",
            "isenabled",
            "islocked",
            "has",
            "can",
        )
    ):
        signals.append("column_name_status_flag_match")
        return SemanticType.STATUS_FLAG, 0.95, signals

    if name_clean in {"status", "state", "stage", "phase"} or name_clean.endswith("status"):
        signals.append("column_name_status_match")
        return SemanticType.STATUS, 0.90, signals

    # 13. Financial Amounts / Quantity / Percentage
    if sql_type in {"money", "smallmoney"} or any(
        amt in name_clean
        for amt in (
            "amount",
            "price",
            "cost",
            "fee",
            "salary",
            "total",
            "balance",
            "subtotal",
            "grandtotal",
        )
    ):
        signals.append("financial_amount_match")
        return SemanticType.AMOUNT, 0.95, signals

    if any(qty in name_clean for qty in ("qty", "quantity", "count", "numberof")):
        signals.append("quantity_match")
        return SemanticType.QUANTITY, 0.95, signals

    if any(pct in name_clean for pct in ("percent", "percentage", "pct", "rate")):
        signals.append("percentage_match")
        return SemanticType.PERCENTAGE, 0.95, signals

    # 14. Descriptions / Notes
    if any(
        desc in name_clean
        for desc in (
            "notes",
            "remarks",
            "comments",
            "summary",
            "desc",
            "description",
        )
    ):
        signals.append("description_notes_match")
        return (
            SemanticType.NOTES if "notes" in name_clean else SemanticType.DESCRIPTION,
            0.95,
            signals,
        )

    # 15. Codes
    if name_clean.endswith("code") or name_clean in {"code", "isocode"}:
        signals.append("code_match")
        return SemanticType.CODE, 0.95, signals

    # 16. Fallback Dates
    if sql_type in {"datetime", "datetime2", "smalldatetime", "datetimeoffset"}:
        signals.append("datatype_datetime_fallback")
        return SemanticType.DATETIME, 0.80, signals

    if sql_type == "date" or name_clean.endswith("date"):
        signals.append("datatype_date_fallback")
        return SemanticType.DATE, 0.80, signals

    # 17. Generic Name
    if name_clean in {"name", "title"} or name_clean.endswith("name"):
        signals.append("column_name_generic_name_match")
        return SemanticType.NAME, 0.75, signals

    # 18. Fallback Unknown
    signals.append("no_rule_match")
    return SemanticType.UNKNOWN, 0.0, signals
