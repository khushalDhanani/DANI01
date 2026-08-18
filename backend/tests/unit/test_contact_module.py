"""
Unit tests for ContactService, ContactAnalyzer, and ContactModuleDefinition.
"""

from unittest.mock import patch

import pytest

from app.modules.contact.analyzer import ContactAnalyzer
from app.modules.contact.service import ContactService
from app.modules.registry import module_registry


def test_contact_module_definition_registered():
    """Verify ContactModuleDefinition is properly registered in module_registry."""
    mod = module_registry.get("CONTACT")
    assert mod is not None
    assert mod.code == "CONTACT"
    assert mod.name == "Contact & Communication Intelligence"
    assert len(mod.tables) >= 5
    assert any(t.table_name == "EmployeeMst" for t in mod.tables)


def test_canonical_predicates():
    """Verify sql_valid_email_predicate and sql_valid_phone_predicate syntax."""
    email_sql = ContactService.sql_valid_email_predicate("col_email")
    assert "col_email LIKE '%@%.%'" in email_sql
    assert "NOT LIKE '% %'" in email_sql

    phone_sql = ContactService.sql_valid_phone_predicate("col_phone")
    assert "LEN(REPLACE(" in phone_sql
    assert "NOT LIKE '%[a-zA-Z]%'" in phone_sql


@pytest.mark.asyncio
async def test_get_contact_overview_mocked():
    """Test get_contact_overview with mocked DB response."""
    service = ContactService()

    mock_overview_rows = [
        {
            "total_active": 1316,
            "with_comp_email": 232,
            "with_pers_email": 1029,
            "with_alt_email": 41,
            "with_any_email": 1065,
            "without_any_email": 251,
            "without_comp_email": 1084,
            "without_pers_email": 287,
            "with_phone1": 1282,
            "with_phone2": 1067,
            "with_corr_phone1": 1297,
            "with_corr_phone2": 1080,
            "with_any_phone": 1299,
            "without_primary_phone": 34,
            "without_any_phone": 17,
            "phone1_verified": 1267,
            "phone2_verified": 1273,
            "with_perm_address": 1310,
            "with_corr_address": 1310,
            "with_perm_pincode": 1310,
            "with_corr_pincode": 1310,
            "with_ice": 27,
        }
    ]
    mock_domain_rows = [
        {"domain": "gmail.com (Personal)", "cnt": 1025},
        {"domain": "aether.co.in (Corporate)", "cnt": 219},
    ]
    mock_sec_rows = [
        {"total_active_users": 1284, "users_with_email": 1284, "users_with_mobile": 1245}
    ]

    with patch(
        "app.modules.contact.service.execute_readonly_query",
        side_effect=[mock_overview_rows, mock_domain_rows, mock_sec_rows],
    ):
        res = await service.get_contact_overview()
        assert res.total_active_employees == 1316
        assert res.email_metrics.with_company_email == 232
        assert res.email_metrics.with_personal_email == 1029
        assert res.phone_metrics.with_primary_phone == 1282
        assert res.address_metrics.with_ice_emergency_contact == 27
        assert len(res.domain_breakdown) == 2


@pytest.mark.asyncio
async def test_get_contact_directory_mocked():
    """Test get_contact_directory with mocked DB response."""
    service = ContactService()

    mock_count_res = [{"total": 1}]
    mock_items_res = [
        {
            "emp_id": 1,
            "emp_code": "1001",
            "full_name": "John Doe",
            "department": "CIS Team",
            "designation": "Technical Leader",
            "location": "Catalyst",
            "company_email": "john.doe@aether.co.in",
            "personal_email": "johndoe@gmail.com",
            "alternate_email": None,
            "primary_phone": "+919876543210",
            "is_verified_phone1": True,
            "secondary_phone": None,
            "is_verified_phone2": False,
            "corr_phone1": "+919876543210",
            "ice_mobile": "+919876543211",
            "ice_contact_name": "Jane Doe",
            "permanent_pincode": "395007",
            "correspondence_pincode": "395007",
            "has_valid_email": True,
            "has_valid_phone": True,
        }
    ]

    with patch(
        "app.modules.contact.service.execute_readonly_query",
        side_effect=[mock_count_res, mock_items_res],
    ):
        res = await service.get_contact_directory(limit=10, offset=0)
        assert res.total == 1
        assert len(res.items) == 1
        assert res.items[0].full_name == "John Doe"
        assert res.items[0].company_email == "john.doe@aether.co.in"


@pytest.mark.asyncio
async def test_get_contact_quality_mocked():
    """Test get_contact_quality with 16 rules evaluation."""
    service = ContactService()

    mock_dq_rows = [
        {"code": "MISSING_ALL_PHONES", "cnt": 17},
        {"code": "CONFLICTING_PRIMARY_CONTACT", "cnt": 0},
        {"code": "DUPLICATE_COMPANY_EMAIL", "cnt": 0},
        {"code": "DUPLICATE_PERSONAL_EMAIL", "cnt": 3},
        {"code": "DUPLICATE_PRIMARY_PHONE", "cnt": 8},
        {"code": "INVALID_EMAIL_FORMAT", "cnt": 0},
        {"code": "INVALID_PHONE_FORMAT", "cnt": 0},
        {"code": "PERSONAL_EMAIL_IN_COMPANY_FIELD", "cnt": 13},
        {"code": "MISSING_PRIMARY_PHONE", "cnt": 34},
        {"code": "MISSING_PERMANENT_PINCODE", "cnt": 33},
        {"code": "MISSING_CORRESPONDENCE_PINCODE", "cnt": 26},
        {"code": "SUSPICIOUS_PLACEHOLDER_EMAIL", "cnt": 0},
        {"code": "MISSING_ANY_EMAIL", "cnt": 251},
        {"code": "MISSING_COMPANY_EMAIL", "cnt": 1084},
        {"code": "MISSING_EMERGENCY_CONTACT", "cnt": 1292},
        {"code": "UNVERIFIED_PRIMARY_PHONE", "cnt": 46},
    ]

    with patch(
        "app.modules.contact.service.execute_readonly_query",
        return_value=mock_dq_rows,
    ):
        res = await service.get_contact_quality()
        assert len(res.rules) == 16
        assert res.critical_issues_count == 17
        assert res.warning_issues_count == 117
        assert res.info_issues_count == 2673


@pytest.mark.asyncio
async def test_contact_analyzer():
    """Test ContactAnalyzer coordinator."""
    service = ContactService()
    analyzer = ContactAnalyzer(service=service)

    mock_ov_obj = patch("app.modules.contact.schemas.ContactOverviewResponse").start()
    mock_q_obj = patch("app.modules.contact.schemas.ContactDataQualityResponse").start()
    mock_ov_obj.model_dump.return_value = {"total_active_employees": 1316}
    mock_q_obj.model_dump.return_value = {"overall_health_score": 90.0}

    with (
        patch.object(service, "get_contact_overview", return_value=mock_ov_obj),
        patch.object(service, "get_contact_quality", return_value=mock_q_obj),
    ):
        res = await analyzer.analyze()
        assert res["module"] == "CONTACT"
        assert res["overview"]["total_active_employees"] == 1316
        assert res["quality"]["overall_health_score"] == 90.0
