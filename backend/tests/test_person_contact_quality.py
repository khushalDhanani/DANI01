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
    }

    with patch("app.modules.person.contact_quality_service.execute_readonly_query", return_value=[mock_row]):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/api/v1/modules/PERSON/contact-quality")
            assert response.status_code == 200
            data = response.json()
            assert data["persons_without_email"] == 12
            assert data["persons_multiple_primary"] == 5
            assert data["primary_contact_inactive"] == 2
            assert data["total_persons_evaluated"] == 28493
            assert data["related_tables_checked"] == 8
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
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
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
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
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
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
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
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
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
    mock_count = [{"total": 1}]
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
        side_effect=[mock_count, mock_items],
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
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
    mock_count = [{"total": 1}]
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
        side_effect=[mock_count, mock_items],
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
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

    with patch("app.modules.person.contact_quality_service.execute_readonly_query", return_value=[mock_row]):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
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
    with patch("app.modules.person.contact_quality_service.execute_readonly_query", return_value=[mock_summary_row]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            summary_res = await ac.get("/api/v1/modules/PERSON/contact-quality")
            assert summary_res.status_code == 200
            summary_count = summary_res.json()["persons_without_email"]
            assert summary_count == 3

    # 2. Issues drilldown endpoint
    with patch("app.modules.person.contact_quality_service.execute_readonly_query", side_effect=[mock_count, mock_items]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            issues_res = await ac.get("/api/v1/modules/PERSON/contact-quality/issues?issue=MISSING_EMAIL&limit=10")
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
    with patch("app.modules.person.contact_quality_service.execute_readonly_query", side_effect=[mock_count, mock_items]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            export_res = await ac.get("/api/v1/modules/PERSON/contact-quality/export?issue=MISSING_EMAIL&format=csv")
            assert export_res.status_code == 200
            csv_content = export_res.text
            assert "MISSING_EMAIL" in csv_content
            assert "Alice" in csv_content
            assert "Smith" in csv_content
            assert "Person #103" in csv_content

