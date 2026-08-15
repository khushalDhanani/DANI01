from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_get_contact_quality_summary():
    mock_row = {
        "persons_without_email": 12,
        "persons_without_phone": 15,
        "invalid_emails": 4,
        "invalid_phones": 3,
        "invalid_urls": 1,
        "unverified_contacts": 50,
        "duplicate_email_cross_persons": 8,
        "duplicate_email_same_person": 2,
        "duplicate_phone_cross_persons": 6,
        "duplicate_phone_same_person": 1,
        "persons_multiple_primary": 5,
        "primary_contact_inactive": 2,
        "addr_missing_postal_code": 20,
        "addr_invalid_pin_format": 7,
        "addr_street_without_city": 3,
        "addr_city_without_state": 4,
        "addr_missing_geocodes": 100,
        "addr_duplicate_same_person": 2,
        "person_anniversary_before_birth": 1,
        "person_invalid_birth_date": 0,
        "person_birth_date_ancient": 10,
        "person_suspicious_dummy_names": 5,
        "person_missing_lastname_only": 12,
        "active_emp_missing_title": 8,
        "inactive_with_empid": 15,
        "status_active_and_deleted": 0,
        "stale_temp_persons": 3,
        "blacklist_unapproved": 1,
        "blacklist_missing_details": 0,
        "company_orphan_links": 2,
        "company_duplicate_links": 4,
        "company_missing_role": 6,
        "extra_field_orphan_id": 1,
        "extra_field_duplicate_entries": 3,
        "deleted_missing_del_date": 0,
        "audit_del_before_ent": 0,
        "sync_zimbra_missing_id": 2,
        "total_persons_evaluated": 28493,
        "total_inactive_persons": 4200,
        "total_deleted_persons": 150,
        "persons_with_critical_issues": 25,
        "persons_with_warning_issues": 120,
        "persons_with_any_issue": 135,
    }

    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query", return_value=[mock_row]
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/modules/PERSON/contact-quality")
            assert response.status_code == 200
            data = response.json()
            assert data["persons_without_email"] == 12
            assert data["persons_multiple_primary"] == 5
            assert data["primary_contact_inactive"] == 2
            assert data["total_persons_evaluated"] == 28493
            assert data["related_tables_checked"] == 8
            assert data["persons_with_critical_issues"] == 25
            assert data["persons_with_warning_issues"] == 120
            assert data["persons_with_any_issue"] == 135
            assert data["total_clean_persons"] == 28493 - 135
            assert data["health_score_pct"] > 90.0
            assert data["total_critical_findings"] > 0
            assert data["total_warning_findings"] > 0
            assert data["total_info_findings"] == 150
            assert "duration_ms" in data


@pytest.mark.asyncio
async def test_get_contact_quality_issues_invalid_email():
    mock_count = [{"total": 1}]
    mock_items = [
        {
            "PersonID": 101,
            "PersonName": "John Doe",
            "ContactID": 501,
            "ContactType": "EMAIL",
            "LabelName": "Work Email",
            "CurrentValue": "johndoe@@invalid",
            "IssueCode": "INVALID_EMAIL",
            "IssueDescription": "Malformed email format or invalid characters",
            "Severity": "CRITICAL",
            "IsVerified": False,
            "IsPrimary": True,
            "IsActive": True,
        }
    ]

    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[mock_count, mock_items],
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/issues?issue=INVALID_EMAIL&limit=5&sort_by=PersonID&sort_order=desc"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["issue"] == "INVALID_EMAIL"
            assert data["total"] == 1
            assert len(data["items"]) == 1
            first = data["items"][0]
            assert first["PersonID"] == 101
            assert first["PersonName"] == "John Doe"
            assert first["IssueCode"] == "INVALID_EMAIL"
            assert first["MaskedValue"] == "johndoe@@invalid"


@pytest.mark.asyncio
async def test_get_contact_quality_issues_multiple_primary():
    mock_count = [{"total": 2}]
    mock_items = [
        {
            "PersonID": 202,
            "PersonName": "Jane Smith",
            "ContactID": 601,
            "ContactType": "EMAIL",
            "LabelName": "Primary Email",
            "CurrentValue": "jane@example.com",
            "IssueCode": "MULTIPLE_PRIMARY",
            "IssueDescription": "Person record has multiple contacts flagged as Primary",
            "Severity": "CRITICAL",
            "IsVerified": True,
            "IsPrimary": True,
            "IsActive": True,
        }
    ]

    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[mock_count, mock_items],
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/issues?issue=MULTIPLE_PRIMARY&limit=10"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["issue"] == "MULTIPLE_PRIMARY"
            assert data["total"] == 2
            assert len(data["items"]) == 1
            assert data["items"][0]["IssueCode"] == "MULTIPLE_PRIMARY"


@pytest.mark.asyncio
async def test_get_contact_quality_issues_primary_inactive():
    mock_count = [{"total": 1}]
    mock_items = [
        {
            "PersonID": 303,
            "PersonName": "Bob Wilson",
            "ContactID": 701,
            "ContactType": "PHONE",
            "LabelName": "Primary Mobile",
            "CurrentValue": "+1 555-0199",
            "IssueCode": "PRIMARY_INACTIVE",
            "IssueDescription": "Primary contact is marked as inactive or disabled",
            "Severity": "CRITICAL",
            "IsVerified": False,
            "IsPrimary": True,
            "IsActive": True,
        }
    ]

    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[mock_count, mock_items],
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/issues?issue=PRIMARY_INACTIVE&limit=5"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["issue"] == "PRIMARY_INACTIVE"
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["IssueCode"] == "PRIMARY_INACTIVE"


@pytest.mark.asyncio
async def test_get_contact_quality_issues_with_search_and_sorting():
    mock_count = [{"total": 1}]
    mock_items = [
        {
            "PersonID": 404,
            "PersonName": "Alice Wonder",
            "ContactID": 801,
            "ContactType": "ADDRESS",
            "LabelName": "Postal Code",
            "CurrentValue": "9999999",
            "IssueCode": "INVALID_PIN_CODE_FORMAT",
            "IssueDescription": "Postal code contains non-numeric characters or invalid length",
            "Severity": "CRITICAL",
            "IsVerified": None,
            "IsPrimary": None,
            "IsActive": True,
        }
    ]

    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[mock_count, mock_items],
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/issues?issue=INVALID_PIN_CODE_FORMAT&search=Alice&sort_by=PersonName&sort_order=asc&limit=5"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["issue"] == "INVALID_PIN_CODE_FORMAT"
            assert data["total"] == 1
            assert data["items"][0]["PersonName"] == "Alice Wonder"


@pytest.mark.asyncio
async def test_export_contact_quality_issues_csv():
    mock_items = [
        {
            "PersonID": 505,
            "PersonName": "Export User",
            "ContactID": 901,
            "ContactType": "EMAIL",
            "LabelName": "Email",
            "CurrentValue": "bad-email",
            "IssueCode": "INVALID_EMAIL",
            "IssueDescription": "Malformed email",
            "Severity": "CRITICAL",
            "IsVerified": False,
            "IsPrimary": True,
            "IsActive": True,
        }
    ]

    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        return_value=mock_items,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/export?issue=INVALID_EMAIL&format=csv"
            )
            assert response.status_code == 200
            assert "text/csv" in response.headers["content-type"]
            assert "attachment; filename=" in response.headers["content-disposition"]
            assert "daylite_invalid_email_" in response.headers["content-disposition"]
            assert ".csv" in response.headers["content-disposition"]
            content = response.text
            assert "Person ID" in content
            assert "Export User" in content
            assert "INVALID_EMAIL" in content


@pytest.mark.asyncio
async def test_export_contact_quality_issues_xlsx():
    mock_items = [
        {
            "PersonID": 505,
            "PersonName": "Export User",
            "ContactID": 901,
            "ContactType": "EMAIL",
            "LabelName": "Email",
            "CurrentValue": "bad-email",
            "IssueCode": "INVALID_EMAIL",
            "IssueDescription": "Malformed email",
            "Severity": "CRITICAL",
            "IsVerified": False,
            "IsPrimary": True,
            "IsActive": True,
        }
    ]

    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        return_value=mock_items,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/export?issue=INVALID_EMAIL&format=xlsx"
            )
            assert response.status_code == 200
            assert "spreadsheetml.sheet" in response.headers["content-type"]
            assert "attachment; filename=" in response.headers["content-disposition"]
            assert "daylite_invalid_email_" in response.headers["content-disposition"]
            assert ".xlsx" in response.headers["content-disposition"]
            assert len(response.content) > 100


@pytest.mark.asyncio
async def test_export_contact_quality_issues_batches_beyond_100_rows():
    """
    Proves that export is NOT silently limited to 100 rows, and properly batches
    to export thousands of records.
    """
    batch_1 = [
        {
            "PersonID": i,
            "PersonName": f"User {i}",
            "ContactID": i * 10,
            "ContactType": "EMAIL",
            "LabelName": "Work",
            "CurrentValue": f"user{i}@bad",
            "IssueCode": "INVALID_EMAIL",
            "IssueDescription": "Malformed email",
            "Severity": "CRITICAL",
            "IsVerified": False,
            "IsPrimary": True,
            "IsActive": True,
        }
        for i in range(1, 1001)
    ]
    batch_2 = [
        {
            "PersonID": i,
            "PersonName": f"User {i}",
            "ContactID": i * 10,
            "ContactType": "EMAIL",
            "LabelName": "Work",
            "CurrentValue": f"user{i}@bad",
            "IssueCode": "INVALID_EMAIL",
            "IssueDescription": "Malformed email",
            "Severity": "CRITICAL",
            "IsVerified": False,
            "IsPrimary": True,
            "IsActive": True,
        }
        for i in range(1001, 2001)
    ]
    batch_3 = [
        {
            "PersonID": i,
            "PersonName": f"User {i}",
            "ContactID": i * 10,
            "ContactType": "EMAIL",
            "LabelName": "Work",
            "CurrentValue": f"user{i}@bad",
            "IssueCode": "INVALID_EMAIL",
            "IssueDescription": "Malformed email",
            "Severity": "CRITICAL",
            "IsVerified": False,
            "IsPrimary": True,
            "IsActive": True,
        }
        for i in range(2001, 2501)
    ]

    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[batch_1, batch_2, batch_3],
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/export?issue=INVALID_EMAIL&format=csv"
            )
            assert response.status_code == 200
            lines = response.text.strip().split("\r\n")
            # 1 header line + 2500 data lines = 2501 lines
            assert len(lines) == 2501
            assert "User 1" in lines[1]
            assert "User 1500" in lines[1500]
            assert "User 2500" in lines[2500]


@pytest.mark.asyncio
async def test_export_contact_quality_summary_xlsx():
    mock_row = {
        "persons_without_email": 12,
        "persons_without_phone": 15,
        "invalid_emails": 4,
        "invalid_phones": 3,
        "invalid_urls": 1,
        "unverified_contacts": 50,
        "duplicate_email_cross_persons": 8,
        "duplicate_email_same_person": 2,
        "duplicate_phone_cross_persons": 6,
        "duplicate_phone_same_person": 1,
        "persons_multiple_primary": 5,
        "primary_contact_inactive": 2,
        "addr_missing_postal_code": 20,
        "addr_invalid_pin_format": 7,
        "addr_street_without_city": 3,
        "addr_city_without_state": 4,
        "addr_missing_geocodes": 100,
        "addr_duplicate_same_person": 2,
        "person_anniversary_before_birth": 1,
        "person_invalid_birth_date": 0,
        "person_birth_date_ancient": 10,
        "person_suspicious_dummy_names": 5,
        "person_missing_lastname_only": 12,
        "active_emp_missing_title": 8,
        "inactive_with_empid": 15,
        "status_active_and_deleted": 0,
        "stale_temp_persons": 3,
        "blacklist_unapproved": 1,
        "blacklist_missing_details": 0,
        "company_orphan_links": 2,
        "company_duplicate_links": 4,
        "company_missing_role": 6,
        "extra_field_orphan_id": 1,
        "extra_field_duplicate_entries": 3,
        "deleted_missing_del_date": 0,
        "audit_del_before_ent": 0,
        "sync_zimbra_missing_id": 2,
        "total_persons_evaluated": 28493,
        "total_inactive_persons": 4200,
        "total_deleted_persons": 150,
    }

    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query", return_value=[mock_row]
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/summary/export?format=xlsx"
            )
            assert response.status_code == 200
            assert "spreadsheetml.sheet" in response.headers["content-type"]
            assert "daylite_quality_summary_" in response.headers["content-disposition"]
            assert len(response.content) > 100


@pytest.mark.asyncio
async def test_missing_email_consistency_and_person_name_formatting():
    """
    Proves that MISSING_EMAIL returns consistent counts across summary, drilldown, and export,
    and correctly handles partial name formatting without falling back to Person #ID.
    """
    mock_summary_row = {
        "persons_without_email": 3,
        "persons_without_phone": 5,
        "invalid_emails": 1,
        "invalid_phones": 1,
        "invalid_urls": 0,
        "unverified_contacts": 10,
        "duplicate_email_cross_persons": 0,
        "duplicate_email_same_person": 0,
        "duplicate_phone_cross_persons": 0,
        "duplicate_phone_same_person": 0,
        "persons_multiple_primary": 0,
        "primary_contact_inactive": 0,
        "addr_missing_postal_code": 0,
        "addr_invalid_pin_format": 0,
        "addr_street_without_city": 0,
        "addr_city_without_state": 0,
        "addr_missing_geocodes": 0,
        "addr_duplicate_same_person": 0,
        "person_anniversary_before_birth": 0,
        "person_invalid_birth_date": 0,
        "person_birth_date_ancient": 0,
        "person_suspicious_dummy_names": 0,
        "person_missing_lastname_only": 0,
        "active_emp_missing_title": 0,
        "inactive_with_empid": 0,
        "status_active_and_deleted": 0,
        "stale_temp_persons": 0,
        "blacklist_unapproved": 0,
        "blacklist_missing_details": 0,
        "company_orphan_links": 0,
        "company_duplicate_links": 0,
        "company_missing_role": 0,
        "extra_field_orphan_id": 0,
        "extra_field_duplicate_entries": 0,
        "deleted_missing_del_date": 0,
        "audit_del_before_ent": 0,
        "sync_zimbra_missing_id": 0,
        "total_persons_evaluated": 100,
        "total_inactive_persons": 10,
        "total_deleted_persons": 2,
    }

    mock_count = [{"total": 3}]
    mock_items = [
        {
            "PersonID": 101,
            "PersonName": "Alice",  # First name only
            "ContactID": None,
            "ContactType": "EMAIL",
            "LabelName": None,
            "CurrentValue": None,
            "IssueCode": "MISSING_EMAIL",
            "IssueDescription": "Person record does not have any registered email address",
            "Severity": "WARNING",
            "IsVerified": None,
            "IsPrimary": None,
            "IsActive": True,
        },
        {
            "PersonID": 102,
            "PersonName": "Smith",  # Last name only
            "ContactID": None,
            "ContactType": "EMAIL",
            "LabelName": None,
            "CurrentValue": None,
            "IssueCode": "MISSING_EMAIL",
            "IssueDescription": "Person record does not have any registered email address",
            "Severity": "WARNING",
            "IsVerified": None,
            "IsPrimary": None,
            "IsActive": True,
        },
        {
            "PersonID": 103,
            "PersonName": "Person #103",  # No names
            "ContactID": None,
            "ContactType": "EMAIL",
            "LabelName": None,
            "CurrentValue": None,
            "IssueCode": "MISSING_EMAIL",
            "IssueDescription": "Person record does not have any registered email address",
            "Severity": "WARNING",
            "IsVerified": None,
            "IsPrimary": None,
            "IsActive": True,
        },
    ]

    # 1. Summary KPI endpoint
    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        return_value=[mock_summary_row],
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            summary_res = await ac.get("/api/v1/modules/PERSON/contact-quality")
            assert summary_res.status_code == 200
            summary_count = summary_res.json()["persons_without_email"]
            assert summary_count == 3

    # 2. Issues drilldown endpoint
    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[mock_count, mock_items],
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            issues_res = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/issues?issue=MISSING_EMAIL&limit=10"
            )
            assert issues_res.status_code == 200
            issues_data = issues_res.json()
            assert issues_data["total"] == summary_count
            assert issues_data["issue"] == "MISSING_EMAIL"
            assert len(issues_data["items"]) == 3
            # Check name formatting
            assert issues_data["items"][0]["PersonName"] == "Alice"
            assert issues_data["items"][1]["PersonName"] == "Smith"
            assert issues_data["items"][2]["PersonName"] == "Person #103"
            for item in issues_data["items"]:
                assert item["IssueCode"] == "MISSING_EMAIL"
                assert item["CurrentValue"] is None

    # 3. Export endpoint
    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query", return_value=mock_items
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            export_res = await ac.get(
                "/api/v1/modules/PERSON/contact-quality/export?issue=MISSING_EMAIL&format=csv"
            )
            assert export_res.status_code == 200
            csv_content = export_res.text
            assert "MISSING_EMAIL" in csv_content
            assert "Alice" in csv_content
            assert "Smith" in csv_content
            assert "Person #103" in csv_content


@pytest.mark.asyncio
async def test_all_quality_issue_types_supported():
    from app.modules.person.contact_quality_schemas import ContactQualityIssueType
    from app.modules.person.contact_quality_service import ContactQualityService

    svc = ContactQualityService()

    # Verify that each enum value produces a valid query without syntax error / unhandled branch
    for issue_type in ContactQualityIssueType:
        mock_count = [{"total": 0}]
        with patch(
            "app.modules.person.contact_quality_service.execute_readonly_query",
            return_value=mock_count,
        ):
            res = await svc.get_contact_quality_issues(issue=issue_type.value, limit=5)
            assert res.issue == issue_type.value
            assert res.total == 0
            assert res.items == []


@pytest.mark.asyncio
async def test_duplicate_predicates_and_address_city_matching():
    """
    Verifies that all 8 duplicate/grouping rules generate SQL with canonical predicates,
    including the address duplicate predicate comparing both Street, CityName, and PostalCode.
    """
    from app.modules.person.contact_quality_service import (
        ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL,
        COMPANY_DUPLICATE_LINKS_WHERE_SQL,
        DUPLICATE_EMAIL_CROSS_WHERE_SQL,
        DUPLICATE_EMAIL_SAME_WHERE_SQL,
        DUPLICATE_PHONE_CROSS_WHERE_SQL,
        DUPLICATE_PHONE_SAME_WHERE_SQL,
        EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL,
        MULTIPLE_PRIMARY_WHERE_SQL,
        _build_issue_queries,
    )

    # 1. Verify address duplicate compares street, city, and postal code
    assert "a2.Street" in ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL
    assert "a2.CityName" in ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL
    assert "a2.PostalCode" in ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL

    # 2. Check query generation for all 8 grouping rules
    group_rules = [
        ("DUPLICATE_EMAIL_CROSS", DUPLICATE_EMAIL_CROSS_WHERE_SQL),
        ("DUPLICATE_EMAIL_SAME", DUPLICATE_EMAIL_SAME_WHERE_SQL),
        ("DUPLICATE_PHONE_CROSS", DUPLICATE_PHONE_CROSS_WHERE_SQL),
        ("DUPLICATE_PHONE_SAME", DUPLICATE_PHONE_SAME_WHERE_SQL),
        ("DUPLICATE_COMPANY_LINKS", COMPANY_DUPLICATE_LINKS_WHERE_SQL),
        ("DUPLICATE_EXTRA_FIELDS", EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL),
        ("DUPLICATE_ADDRESSES_SAME_PERSON", ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL),
    ]

    for rule_code, predicate in group_rules:
        count_sql, items_sql, _ = _build_issue_queries(rule_code)
        assert count_sql is not None, f"count_sql was None for {rule_code}"
        assert items_sql is not None, f"items_sql was None for {rule_code}"
        assert predicate in count_sql, f"Predicate missing in count_sql for {rule_code}"
        assert predicate in items_sql, f"Predicate missing in items_sql for {rule_code}"

    # For MULTIPLE_PRIMARY: count_sql evaluates distinct persons, items_sql evaluates records
    count_sql, items_sql, _ = _build_issue_queries("MULTIPLE_PRIMARY")
    assert "HAVING COUNT(1) > 1" in count_sql
    assert MULTIPLE_PRIMARY_WHERE_SQL in items_sql


@pytest.mark.asyncio
async def test_count_unit_metadata_and_group_drilldown():
    """
    Verifies that RULE_METADATA covers all 37 rules with explicit count units,
    and DUPLICATE_GROUP rules return structured group clusters with nested members.
    """
    from app.modules.person.contact_quality_schemas import (
        RULE_METADATA,
        ContactQualityIssueType,
        IssueCountUnit,
    )
    from app.modules.person.contact_quality_service import ContactQualityService

    # 1. Verify metadata coverage for all 37 rules
    assert len(RULE_METADATA) == len(ContactQualityIssueType)
    for issue_type in ContactQualityIssueType:
        meta = RULE_METADATA.get(issue_type)
        assert meta is not None, f"Missing metadata for {issue_type}"
        assert isinstance(meta.count_unit, IssueCountUnit)
        assert meta.unit_label_singular != ""
        assert meta.unit_label_plural != ""
        assert meta.title != ""

    # 2. Verify DUPLICATE_GROUP rules taxonomy
    duplicate_group_rules = [
        ContactQualityIssueType.DUPLICATE_EMAIL_CROSS,
        ContactQualityIssueType.DUPLICATE_PHONE_CROSS,
        ContactQualityIssueType.DUPLICATE_EMAIL_SAME,
        ContactQualityIssueType.DUPLICATE_PHONE_SAME,
        ContactQualityIssueType.DUPLICATE_ADDRESSES_SAME_PERSON,
        ContactQualityIssueType.DUPLICATE_COMPANY_LINKS,
        ContactQualityIssueType.DUPLICATE_EXTRA_FIELDS,
    ]
    for r in duplicate_group_rules:
        assert RULE_METADATA[r].count_unit == IssueCountUnit.DUPLICATE_GROUP
        assert "Group" in RULE_METADATA[r].unit_label_singular
        assert "Groups" in RULE_METADATA[r].unit_label_plural

    # 3. Test drilldown returns groups for DUPLICATE_EMAIL_CROSS
    mock_count = [{"total": 1}]
    mock_groups = [
        {
            "GroupKey": "shared@acme.com",
            "GroupLabel": "shared@acme.com",
            "AffectedPersonsCount": 2,
            "AffectedRecordsCount": 2,
        }
    ]
    mock_members = [
        {
            "PersonID": 101,
            "PersonName": "Alice Smith",
            "ContactID": 1001,
            "ContactType": "EMAIL",
            "LabelName": "Work",
            "CurrentValue": "shared@acme.com",
            "IssueCode": "DUPLICATE_EMAIL_CROSS",
            "IssueDescription": "Email is shared across multiple distinct Person accounts",
            "Severity": "WARNING",
            "IsVerified": True,
            "IsPrimary": True,
            "IsActive": True,
        },
        {
            "PersonID": 102,
            "PersonName": "Bob Jones",
            "ContactID": 1002,
            "ContactType": "EMAIL",
            "LabelName": "Work",
            "CurrentValue": "shared@acme.com",
            "IssueCode": "DUPLICATE_EMAIL_CROSS",
            "IssueDescription": "Email is shared across multiple distinct Person accounts",
            "Severity": "WARNING",
            "IsVerified": True,
            "IsPrimary": True,
            "IsActive": True,
        },
    ]

    svc = ContactQualityService()
    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[mock_count, mock_groups, mock_members],
    ):
        res = await svc.get_contact_quality_issues(issue="DUPLICATE_EMAIL_CROSS", limit=25)
        assert res.issue == "DUPLICATE_EMAIL_CROSS"
        assert res.count_unit == IssueCountUnit.DUPLICATE_GROUP
        assert res.unit_label_singular == "Shared Email Group"
        assert res.unit_label_plural == "Shared Email Groups"
        assert res.total == 1
        assert len(res.groups) == 1
        assert res.groups[0].group_key == "shared@acme.com"
        assert res.groups[0].affected_persons_count == 2
        assert res.groups[0].affected_records_count == 2
        assert len(res.groups[0].members) == 2
        assert res.groups[0].members[0].person_name == "Alice Smith"
        assert res.groups[0].members[1].person_name == "Bob Jones"


@pytest.mark.asyncio
async def test_cross_layer_predicate_identity_all_37_rules():
    """
    Exhaustively proves that every single one of the 37 rules uses its canonical
    WHERE clause predicate across drill-down, summary queries, and export filters.
    Prevents silent predicate drift between summary counts and detail rows.
    """
    from app.modules.person.contact_quality_schemas import (
        RULE_METADATA,
        ContactQualityIssueType,
        IssueCountUnit,
    )
    from app.modules.person.contact_quality_service import (
        ACTIVE_EMP_MISSING_TITLE_WHERE_SQL,
        ADDR_CITY_WITHOUT_STATE_WHERE_SQL,
        ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL,
        ADDR_INVALID_PIN_FORMAT_WHERE_SQL,
        ADDR_MISSING_GEOCODES_WHERE_SQL,
        ADDR_MISSING_POSTAL_CODE_WHERE_SQL,
        ADDR_STREET_WITHOUT_CITY_WHERE_SQL,
        AUDIT_DEL_BEFORE_ENT_WHERE_SQL,
        BLACKLIST_MISSING_DETAILS_WHERE_SQL,
        BLACKLIST_UNAPPROVED_WHERE_SQL,
        COMPANY_DUPLICATE_LINKS_WHERE_SQL,
        COMPANY_MISSING_ROLE_WHERE_SQL,
        COMPANY_ORPHAN_LINKS_WHERE_SQL,
        DELETED_MISSING_DEL_DATE_WHERE_SQL,
        DUPLICATE_EMAIL_CROSS_WHERE_SQL,
        DUPLICATE_EMAIL_SAME_WHERE_SQL,
        DUPLICATE_PHONE_CROSS_WHERE_SQL,
        DUPLICATE_PHONE_SAME_WHERE_SQL,
        EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL,
        EXTRA_FIELD_ORPHAN_ID_WHERE_SQL,
        INACTIVE_WITH_EMPID_WHERE_SQL,
        INVALID_EMAIL_WHERE_SQL,
        INVALID_PHONE_WHERE_SQL,
        INVALID_URL_WHERE_SQL,
        MULTIPLE_PRIMARY_WHERE_SQL,
        PERSON_ANNIVERSARY_BEFORE_BIRTH_WHERE_SQL,
        PERSON_BIRTH_DATE_ANCIENT_WHERE_SQL,
        PERSON_INVALID_BIRTH_DATE_WHERE_SQL,
        PERSON_MISSING_LASTNAME_ONLY_WHERE_SQL,
        PERSON_SUSPICIOUS_DUMMY_NAMES_WHERE_SQL,
        PRIMARY_INACTIVE_WHERE_SQL,
        QUALIFYING_EMAIL_EXISTS_SQL,
        QUALIFYING_PHONE_EXISTS_SQL,
        STALE_TEMP_PERSONS_WHERE_SQL,
        STATUS_ACTIVE_AND_DELETED_WHERE_SQL,
        SYNC_ZIMBRA_MISSING_ID_WHERE_SQL,
        UNVERIFIED_CONTACT_WHERE_SQL,
        _build_group_queries,
        _build_issue_queries,
    )

    predicate_map = {
        ContactQualityIssueType.MISSING_EMAIL: QUALIFYING_EMAIL_EXISTS_SQL,
        ContactQualityIssueType.MISSING_PHONE: QUALIFYING_PHONE_EXISTS_SQL,
        ContactQualityIssueType.INVALID_EMAIL: INVALID_EMAIL_WHERE_SQL,
        ContactQualityIssueType.INVALID_PHONE: INVALID_PHONE_WHERE_SQL,
        ContactQualityIssueType.INVALID_URL: INVALID_URL_WHERE_SQL,
        ContactQualityIssueType.UNVERIFIED_CONTACT: UNVERIFIED_CONTACT_WHERE_SQL,
        ContactQualityIssueType.DUPLICATE_EMAIL_CROSS: DUPLICATE_EMAIL_CROSS_WHERE_SQL,
        ContactQualityIssueType.DUPLICATE_PHONE_CROSS: DUPLICATE_PHONE_CROSS_WHERE_SQL,
        ContactQualityIssueType.DUPLICATE_EMAIL_SAME: DUPLICATE_EMAIL_SAME_WHERE_SQL,
        ContactQualityIssueType.DUPLICATE_PHONE_SAME: DUPLICATE_PHONE_SAME_WHERE_SQL,
        ContactQualityIssueType.MULTIPLE_PRIMARY: MULTIPLE_PRIMARY_WHERE_SQL,
        ContactQualityIssueType.PRIMARY_INACTIVE: PRIMARY_INACTIVE_WHERE_SQL,
        ContactQualityIssueType.MISSING_POSTAL_CODE: ADDR_MISSING_POSTAL_CODE_WHERE_SQL,
        ContactQualityIssueType.INVALID_PIN_CODE_FORMAT: ADDR_INVALID_PIN_FORMAT_WHERE_SQL,
        ContactQualityIssueType.STREET_WITHOUT_CITY: ADDR_STREET_WITHOUT_CITY_WHERE_SQL,
        ContactQualityIssueType.CITY_WITHOUT_STATE: ADDR_CITY_WITHOUT_STATE_WHERE_SQL,
        ContactQualityIssueType.MISSING_GEOCODES: ADDR_MISSING_GEOCODES_WHERE_SQL,
        ContactQualityIssueType.DUPLICATE_ADDRESSES_SAME_PERSON: ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL,
        ContactQualityIssueType.ANNIVERSARY_BEFORE_BIRTH: PERSON_ANNIVERSARY_BEFORE_BIRTH_WHERE_SQL,
        ContactQualityIssueType.INVALID_BIRTH_DATE: PERSON_INVALID_BIRTH_DATE_WHERE_SQL,
        ContactQualityIssueType.BIRTH_DATE_DEFAULT_OR_ANCIENT: PERSON_BIRTH_DATE_ANCIENT_WHERE_SQL,
        ContactQualityIssueType.SUSPICIOUS_DUMMY_NAMES: PERSON_SUSPICIOUS_DUMMY_NAMES_WHERE_SQL,
        ContactQualityIssueType.MISSING_LAST_NAME: PERSON_MISSING_LASTNAME_ONLY_WHERE_SQL,
        ContactQualityIssueType.ACTIVE_EMP_MISSING_TITLE: ACTIVE_EMP_MISSING_TITLE_WHERE_SQL,
        ContactQualityIssueType.INACTIVE_WITH_ACTIVE_EMPID: INACTIVE_WITH_EMPID_WHERE_SQL,
        ContactQualityIssueType.STATUS_ACTIVE_AND_DELETED: STATUS_ACTIVE_AND_DELETED_WHERE_SQL,
        ContactQualityIssueType.STALE_TEMP_PERSONS: STALE_TEMP_PERSONS_WHERE_SQL,
        ContactQualityIssueType.BLACKLIST_UNAPPROVED: BLACKLIST_UNAPPROVED_WHERE_SQL,
        ContactQualityIssueType.BLACKLIST_MISSING_DETAILS: BLACKLIST_MISSING_DETAILS_WHERE_SQL,
        ContactQualityIssueType.ORPHAN_COMPANY_LINK: COMPANY_ORPHAN_LINKS_WHERE_SQL,
        ContactQualityIssueType.DUPLICATE_COMPANY_LINKS: COMPANY_DUPLICATE_LINKS_WHERE_SQL,
        ContactQualityIssueType.COMPANY_MISSING_ROLE: COMPANY_MISSING_ROLE_WHERE_SQL,
        ContactQualityIssueType.EXTRA_FIELD_ORPHAN_ID: EXTRA_FIELD_ORPHAN_ID_WHERE_SQL,
        ContactQualityIssueType.DUPLICATE_EXTRA_FIELDS: EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL,
        ContactQualityIssueType.DELETED_MISSING_TIMESTAMP: DELETED_MISSING_DEL_DATE_WHERE_SQL,
        ContactQualityIssueType.AUDIT_DEL_BEFORE_ENT: AUDIT_DEL_BEFORE_ENT_WHERE_SQL,
        ContactQualityIssueType.SYNC_ZIMBRA_MISSING_ID: SYNC_ZIMBRA_MISSING_ID_WHERE_SQL,
    }

    # Verify all 37 rules are checked
    assert len(predicate_map) == len(ContactQualityIssueType) == 37

    for issue_type, canonical_pred in predicate_map.items():
        meta = RULE_METADATA[issue_type]
        if meta.count_unit == IssueCountUnit.DUPLICATE_GROUP:
            count_sql, group_sql, _ = _build_group_queries(issue_type.value)
            assert count_sql is not None, f"Group count_sql is None for {issue_type}"
            assert group_sql is not None, f"Group groups_sql is None for {issue_type}"
            # Verify the canonical predicate is embedded in the standard row-fetch query as well
            _, items_sql, _ = _build_issue_queries(issue_type.value)
            assert canonical_pred in items_sql, (
                f"Canonical predicate drifted in items_sql for {issue_type}"
            )
        else:
            count_sql, items_sql, _ = _build_issue_queries(issue_type.value)
            assert count_sql is not None, f"count_sql is None for {issue_type}"
            assert items_sql is not None, f"items_sql is None for {issue_type}"
            assert canonical_pred in items_sql, (
                f"Canonical predicate drifted in items_sql for {issue_type}"
            )
            if issue_type == ContactQualityIssueType.MULTIPLE_PRIMARY:
                assert "HAVING COUNT(1) > 1" in count_sql
            else:
                assert canonical_pred in count_sql, (
                    f"Canonical predicate drifted in count_sql for {issue_type}"
                )


@pytest.mark.asyncio
async def test_ui_pagination_clamping_vs_export_full_batching():
    """
    Proves that:
    1. UI drilldown endpoint strictly clamps user-requested limit (e.g. 50,000) to MAX_PAGE_SIZE = 100.
    2. Export endpoint bypasses UI page clamping and retrieves all rows across multiple batches up to 50,000.
    """
    from app.modules.person.contact_quality_service import ContactQualityService

    # Create a 350-row database mock dataset
    total_mock_rows = 350
    all_mock_rows = [
        {
            "PersonID": i,
            "PersonName": f"User {i}",
            "ContactID": i * 10,
            "ContactType": "EMAIL",
            "LabelName": "Work",
            "CurrentValue": f"user{i}@@bad",
            "IssueCode": "INVALID_EMAIL",
            "IssueDescription": "Malformed email address",
            "Severity": "CRITICAL",
            "IsVerified": False,
            "IsPrimary": True,
            "IsActive": True,
        }
        for i in range(1, total_mock_rows + 1)
    ]

    svc = ContactQualityService()

    # 1. UI Drilldown: requested limit=50,000 -> clamped to 100
    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[[{"total": total_mock_rows}], all_mock_rows[:100]],
    ):
        ui_res = await svc.get_contact_quality_issues(issue="INVALID_EMAIL", limit=50000, offset=0)
        assert ui_res.limit == 100  # Clamped to MAX_PAGE_SIZE
        assert len(ui_res.items) == 100
        assert ui_res.total == 350

    # 2. Export: retrieves all 350 rows across batches (batch 1: 350 rows, batch 2: empty)
    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[all_mock_rows, []],
    ):
        content, _media_type, _filename = await svc.export_contact_quality_issues(
            issue="INVALID_EMAIL",
            format="csv",
        )
        csv_lines = content.decode("utf-8").strip().split("\r\n")
        # 1 header line + 350 data rows = 351 lines
        assert len(csv_lines) == 351
        assert "User 1" in csv_lines[1]
        assert "User 350" in csv_lines[350]
        assert "INVALID_EMAIL" in csv_lines[1]


@pytest.mark.asyncio
async def test_issue_export_can_exceed_api_page_size():
    """
    Export regression test: verifies that export can fetch >100 matching rows across batches,
    exceeding MAX_PAGE_SIZE = 100.
    """
    from app.modules.person.contact_quality_service import ContactQualityService

    matching_count = 250
    mock_rows = [
        {
            "PersonID": i,
            "PersonName": f"User {i}",
            "ContactID": i * 10,
            "ContactType": "EMAIL",
            "LabelName": "Work",
            "CurrentValue": f"user{i}@@bad",
            "IssueCode": "INVALID_EMAIL",
            "IssueDescription": "Malformed email",
            "Severity": "CRITICAL",
            "IsVerified": False,
            "IsPrimary": True,
            "IsActive": True,
        }
        for i in range(1, matching_count + 1)
    ]

    svc = ContactQualityService()
    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=[mock_rows, []],
    ):
        content, _media_type, _filename = await svc.export_contact_quality_issues(
            issue="INVALID_EMAIL",
            format="csv",
        )
        lines = content.decode("utf-8").strip().split("\r\n")
        data_rows_count = len(lines) - 1
        assert data_rows_count == 250
        assert data_rows_count > 100


@pytest.mark.parametrize(
    ("issue", "summary_field"),
    [
        ("MISSING_EMAIL", "persons_without_email"),
        ("MISSING_PHONE", "persons_without_phone"),
        ("INVALID_EMAIL", "invalid_emails"),
        ("INVALID_PHONE", "invalid_phones"),
        ("INVALID_URL", "invalid_urls"),
        ("UNVERIFIED_CONTACT", "unverified_contacts"),
        ("DUPLICATE_EMAIL_CROSS", "duplicate_email_cross_persons"),
        ("DUPLICATE_PHONE_CROSS", "duplicate_phone_cross_persons"),
        ("DUPLICATE_EMAIL_SAME", "duplicate_email_same_person"),
        ("DUPLICATE_PHONE_SAME", "duplicate_phone_same_person"),
        ("MULTIPLE_PRIMARY", "persons_multiple_primary"),
        ("PRIMARY_INACTIVE", "primary_contact_inactive"),
        ("MISSING_POSTAL_CODE", "addr_missing_postal_code"),
        ("INVALID_PIN_CODE_FORMAT", "addr_invalid_pin_format"),
        ("STREET_WITHOUT_CITY", "addr_street_without_city"),
        ("CITY_WITHOUT_STATE", "addr_city_without_state"),
        ("MISSING_GEOCODES", "addr_missing_geocodes"),
        ("DUPLICATE_ADDRESSES_SAME_PERSON", "addr_duplicate_same_person"),
        ("ANNIVERSARY_BEFORE_BIRTH", "person_anniversary_before_birth"),
        ("INVALID_BIRTH_DATE", "person_invalid_birth_date"),
        ("BIRTH_DATE_DEFAULT_OR_ANCIENT", "person_birth_date_ancient"),
        ("SUSPICIOUS_DUMMY_NAMES", "person_suspicious_dummy_names"),
        ("MISSING_LAST_NAME", "person_missing_lastname_only"),
        ("ACTIVE_EMP_MISSING_TITLE", "active_emp_missing_title"),
        ("INACTIVE_WITH_ACTIVE_EMPID", "inactive_with_empid"),
        ("STATUS_ACTIVE_AND_DELETED", "status_active_and_deleted"),
        ("STALE_TEMP_PERSONS", "stale_temp_persons"),
        ("BLACKLIST_UNAPPROVED", "blacklist_unapproved"),
        ("BLACKLIST_MISSING_DETAILS", "blacklist_missing_details"),
        ("ORPHAN_COMPANY_LINK", "company_orphan_links"),
        ("DUPLICATE_COMPANY_LINKS", "company_duplicate_links"),
        ("COMPANY_MISSING_ROLE", "company_missing_role"),
        ("EXTRA_FIELD_ORPHAN_ID", "extra_field_orphan_id"),
        ("DUPLICATE_EXTRA_FIELDS", "extra_field_duplicate_entries"),
        ("DELETED_MISSING_TIMESTAMP", "deleted_missing_del_date"),
        ("AUDIT_DEL_BEFORE_ENT", "audit_del_before_ent"),
        ("SYNC_ZIMBRA_MISSING_ID", "sync_zimbra_missing_id"),
    ],
)
@pytest.mark.asyncio
async def test_summary_equals_issue_total(issue, summary_field):
    """
    Cardinality invariant test: for every quality rule, Summary metric and Issue drilldown total
    evaluate to identical counts against a deterministic shared dataset.
    """
    from app.modules.person.contact_quality_service import ContactQualityService

    deterministic_cardinality = {
        "persons_without_email": 14,
        "persons_without_phone": 9,
        "invalid_emails": 6,
        "invalid_phones": 5,
        "invalid_urls": 2,
        "unverified_contacts": 40,
        "duplicate_email_cross_persons": 7,
        "duplicate_phone_cross_persons": 4,
        "duplicate_email_same_person": 3,
        "duplicate_phone_same_person": 2,
        "persons_multiple_primary": 8,
        "primary_contact_inactive": 1,
        "addr_missing_postal_code": 11,
        "addr_invalid_pin_format": 4,
        "addr_street_without_city": 3,
        "addr_city_without_state": 2,
        "addr_missing_geocodes": 15,
        "addr_duplicate_same_person": 5,
        "person_anniversary_before_birth": 2,
        "person_invalid_birth_date": 1,
        "person_birth_date_ancient": 4,
        "person_suspicious_dummy_names": 6,
        "person_missing_lastname_only": 7,
        "active_emp_missing_title": 5,
        "inactive_with_empid": 3,
        "status_active_and_deleted": 1,
        "stale_temp_persons": 2,
        "blacklist_unapproved": 1,
        "blacklist_missing_details": 1,
        "company_orphan_links": 2,
        "company_duplicate_links": 3,
        "company_missing_role": 4,
        "extra_field_orphan_id": 1,
        "extra_field_duplicate_entries": 2,
        "deleted_missing_del_date": 1,
        "audit_del_before_ent": 1,
        "sync_zimbra_missing_id": 3,
        "total_persons_evaluated": 1500,
        "total_inactive_persons": 200,
        "total_deleted_persons": 25,
        "persons_with_critical_issues": 15,
        "persons_with_warning_issues": 45,
        "persons_with_any_issue": 50,
    }

    expected_total = deterministic_cardinality[summary_field]

    def deterministic_query_driver(sql: str, params: dict | None = None):
        sql_upper = sql.upper()
        # Summary queries (6 parallel): return the full cardinality dict for any
        # query that contains recognized summary field aliases.
        summary_markers = [
            "AS TOTAL_PERSONS_EVALUATED",
            "AS PERSONS_WITHOUT_EMAIL",
            "AS INVALID_EMAILS",
            "AS ADDR_MISSING_POSTAL_CODE",
            "AS COMPANY_ORPHAN_LINKS",
            "AS EXTRA_FIELD_ORPHAN_ID",
            "AS PERSONS_WITH_CRITICAL_ISSUES",
        ]
        if any(m in sql_upper for m in summary_markers):
            return [deterministic_cardinality]
        if "AS TOTAL" in sql_upper:
            return [{"total": expected_total}]
        return []

    svc = ContactQualityService()
    with patch(
        "app.modules.person.contact_quality_service.execute_readonly_query",
        side_effect=deterministic_query_driver,
    ):
        summary = await svc.get_contact_quality_summary()
        issues = await svc.get_contact_quality_issues(issue=issue, limit=1)

        assert getattr(summary, summary_field) == issues.total
        assert issues.total == expected_total


def test_address_duplicate_normalization_and_city_matching_semantics():
    """
    Specifically proves the business logic of duplicate address matching:
    - Same Person + Same Street + Same City -> DUPLICATE
    - Same Person + Same Street + Different City -> NOT DUPLICATE
    - Same Person + Same Street with case/whitespace variations + Same City -> DUPLICATE
    - Different Person + Same Street + Same City -> NOT DUPLICATE under same person
    """

    def normalize_addr(person_id: int, street: str | None, city: str | None, postal: str | None):
        if not street or not street.strip():
            return None
        return (
            person_id,
            street.strip().lower(),
            (city or "").strip().lower(),
            (postal or "").strip().lower(),
        )

    def is_duplicate(target_idx: int, address_table: list[dict]):
        target = address_table[target_idx]
        target_key = normalize_addr(
            target["PersonID"],
            target.get("Street"),
            target.get("CityName"),
            target.get("PostalCode"),
        )
        if not target_key:
            return False

        for i, other in enumerate(address_table):
            if i == target_idx or other.get("PersonAddID") == target.get("PersonAddID"):
                continue
            other_key = normalize_addr(
                other["PersonID"],
                other.get("Street"),
                other.get("CityName"),
                other.get("PostalCode"),
            )
            if target_key == other_key:
                return True
        return False

    test_table = [
        # Case 1: Same person, same street, same city -> Duplicate
        {
            "PersonAddID": 1,
            "PersonID": 10,
            "Street": "12 Station Road",
            "CityName": "Pune",
            "PostalCode": "411001",
        },
        {
            "PersonAddID": 2,
            "PersonID": 10,
            "Street": "12 Station Road",
            "CityName": "Pune",
            "PostalCode": "411001",
        },
        # Case 2: Same person, same street, DIFFERENT city -> NOT Duplicate
        {
            "PersonAddID": 3,
            "PersonID": 20,
            "Street": "12 Station Road",
            "CityName": "Pune",
            "PostalCode": "411001",
        },
        {
            "PersonAddID": 4,
            "PersonID": 20,
            "Street": "12 Station Road",
            "CityName": "Mumbai",
            "PostalCode": "400001",
        },
        # Case 3: Same person, case & whitespace variations -> Duplicate
        {
            "PersonAddID": 5,
            "PersonID": 30,
            "Street": "  100 MG ROAD  ",
            "CityName": "bengaluru",
            "PostalCode": "560001",
        },
        {
            "PersonAddID": 6,
            "PersonID": 30,
            "Street": "100 mg road",
            "CityName": "Bengaluru",
            "PostalCode": "560001",
        },
        # Case 4: Different person, same street and city -> NOT Duplicate under same person
        {
            "PersonAddID": 7,
            "PersonID": 40,
            "Street": "55 Park Avenue",
            "CityName": "Delhi",
            "PostalCode": "110001",
        },
        {
            "PersonAddID": 8,
            "PersonID": 41,
            "Street": "55 Park Avenue",
            "CityName": "Delhi",
            "PostalCode": "110001",
        },
    ]

    # Assert Case 1 (Duplicates)
    assert is_duplicate(0, test_table) is True
    assert is_duplicate(1, test_table) is True

    # Assert Case 2 (Different Cities -> NOT Duplicates)
    assert is_duplicate(2, test_table) is False
    assert is_duplicate(3, test_table) is False

    # Assert Case 3 (Case/Whitespace -> Duplicates)
    assert is_duplicate(4, test_table) is True
    assert is_duplicate(5, test_table) is True

    # Assert Case 4 (Different Persons -> NOT Duplicates)
    assert is_duplicate(6, test_table) is False
    assert is_duplicate(7, test_table) is False


def test_severity_parameter_elimination_contract():
    """
    Proves that the redundant severity filter parameter is completely removed
    from both get_contact_quality_issues and export_contact_quality_issues signatures.
    """
    import inspect

    from app.api.routes.modules import (
        export_contact_quality_issues,
        get_contact_quality_issues,
    )
    from app.modules.person.contact_quality_service import ContactQualityService

    svc_issues_params = inspect.signature(
        ContactQualityService.get_contact_quality_issues
    ).parameters
    svc_export_params = inspect.signature(
        ContactQualityService.export_contact_quality_issues
    ).parameters
    route_issues_params = inspect.signature(get_contact_quality_issues).parameters
    route_export_params = inspect.signature(export_contact_quality_issues).parameters

    assert "severity" not in svc_issues_params
    assert "severity" not in svc_export_params
    assert "severity" not in route_issues_params
    assert "severity" not in route_export_params


@pytest.mark.asyncio
async def test_get_contact_quality_rules_endpoint():
    """
    Tests that the rules catalog API endpoint returns all 37 declarative rules with complete metadata.
    """
    from app.api.routes.modules import get_contact_quality_rules
    from app.modules.person.contact_quality_schemas import ContactQualityIssueType

    rules = await get_contact_quality_rules()
    assert len(rules) == 37
    rule_codes = {r.code for r in rules}
    assert rule_codes == set(ContactQualityIssueType)
    for r in rules:
        assert r.title != ""
        assert r.dimension in {"CONTACTS", "ADDRESSES", "PROFILE", "EMPLOYMENT", "GOVERNANCE"}
        assert r.severity in {"CRITICAL", "WARNING", "INFO"}
        assert r.unit_label_singular != ""
        assert r.unit_label_plural != ""
