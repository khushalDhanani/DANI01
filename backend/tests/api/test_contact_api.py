"""
API Route tests for /api/v1/modules/CONTACT endpoints.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_contact_service
from app.main import app
from app.modules.contact.schemas import (
    ContactAddressOverview,
    ContactDataQualityResponse,
    ContactDirectoryItem,
    ContactDirectoryListResponse,
    ContactEmailOverview,
    ContactOverviewResponse,
    ContactPhoneOverview,
    ContactQualityIssuesListResponse,
)
from app.modules.employee.schemas import IssueSeverity


@pytest.fixture
def mock_contact_service():
    service = AsyncMock()

    service.get_contact_overview.return_value = ContactOverviewResponse(
        total_active_employees=1316,
        email_metrics=ContactEmailOverview(
            total_active_employees=1316,
            with_company_email=232,
            with_company_email_pct=17.6,
            with_personal_email=1029,
            with_personal_email_pct=78.2,
            with_alternate_email=41,
            with_alternate_email_pct=3.1,
            with_any_email=1065,
            with_any_email_pct=80.9,
            without_any_email=251,
            without_any_email_pct=19.1,
            without_company_email=1084,
            without_company_email_pct=82.4,
            without_personal_email=287,
            without_personal_email_pct=21.8,
        ),
        phone_metrics=ContactPhoneOverview(
            with_primary_phone=1282,
            with_primary_phone_pct=97.4,
            with_secondary_phone=1067,
            with_secondary_phone_pct=81.1,
            with_corr_phone1=1297,
            with_corr_phone1_pct=98.6,
            with_corr_phone2=1080,
            with_corr_phone2_pct=82.1,
            with_any_phone=1299,
            with_any_phone_pct=98.7,
            without_primary_phone=34,
            without_primary_phone_pct=2.6,
            without_any_phone=17,
            without_any_phone_pct=1.3,
            primary_phone_verified=1267,
            primary_phone_verified_pct=98.8,
            secondary_phone_verified=1060,
            secondary_phone_verified_pct=99.3,
        ),
        address_metrics=ContactAddressOverview(
            with_permanent_address=1310,
            with_permanent_address_pct=99.5,
            with_correspondence_address=1310,
            with_correspondence_address_pct=99.5,
            with_permanent_pincode=1310,
            with_correspondence_pincode=1310,
            with_ice_emergency_contact=27,
            with_ice_emergency_contact_pct=2.1,
        ),
        domain_breakdown=[],
        security_user_sync={"total_active_users": 1284},
        generated_at="2026-08-17T12:00:00Z",
    )

    service.get_contact_directory.return_value = ContactDirectoryListResponse(
        total=1,
        limit=25,
        offset=0,
        items=[
            ContactDirectoryItem(
                emp_id=1,
                emp_code="1001",
                full_name="John Doe",
                department="CIS Team",
                designation="Technical Leader",
                location="Catalyst",
                company_email="john.doe@aether.co.in",
                personal_email="johndoe@gmail.com",
                primary_phone="+919876543210",
                is_verified_phone1=True,
                has_valid_email=True,
                has_valid_phone=True,
            )
        ],
    )

    service.export_contact_directory.return_value = (
        b"emp_id,emp_code,full_name\n1,1001,John Doe\n",
        "text/csv",
        "contact_directory.csv",
    )

    service.get_contact_quality.return_value = ContactDataQualityResponse(
        overall_health_score=85.0,
        critical_issues_count=17,
        warning_issues_count=64,
        info_issues_count=2639,
        rules=[],
        summary_by_severity={"CRITICAL": 17, "WARNING": 64, "INFO": 2639},
        generated_at="2026-08-17T12:00:00Z",
    )

    service.get_contact_quality_issues.return_value = ContactQualityIssuesListResponse(
        issue_code="MISSING_ALL_PHONES",
        issue_name="Active Employee Missing All Phone Numbers",
        severity=IssueSeverity.CRITICAL,
        total=17,
        limit=25,
        offset=0,
        items=[],
    )

    service.export_contact_quality_issues.return_value = (
        b"record_id,emp_code,entity_name\n1,1001,John Doe\n",
        "text/csv",
        "contact_quality_missing_all_phones.csv",
    )

    return service


def test_get_contact_overview_endpoint(mock_contact_service):
    app.dependency_overrides[get_contact_service] = lambda: mock_contact_service
    client = TestClient(app)
    try:
        response = client.get("/api/v1/modules/CONTACT/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["total_active_employees"] == 1316
        assert data["email_metrics"]["with_company_email"] == 232
        assert data["phone_metrics"]["with_primary_phone"] == 1282
    finally:
        app.dependency_overrides.clear()


def test_get_contact_directory_endpoint(mock_contact_service):
    app.dependency_overrides[get_contact_service] = lambda: mock_contact_service
    client = TestClient(app)
    try:
        response = client.get(
            "/api/v1/modules/CONTACT/directory?email_filter=WITH_COMPANY_EMAIL&limit=10"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["emp_code"] == "1001"
    finally:
        app.dependency_overrides.clear()


def test_export_contact_directory_endpoint(mock_contact_service):
    app.dependency_overrides[get_contact_service] = lambda: mock_contact_service
    client = TestClient(app)
    try:
        response = client.get("/api/v1/modules/CONTACT/directory/export")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "emp_id,emp_code,full_name" in response.text
    finally:
        app.dependency_overrides.clear()


def test_get_contact_quality_endpoint(mock_contact_service):
    app.dependency_overrides[get_contact_service] = lambda: mock_contact_service
    client = TestClient(app)
    try:
        response = client.get("/api/v1/modules/CONTACT/quality")
        assert response.status_code == 200
        data = response.json()
        assert data["overall_health_score"] == 85.0
        assert data["critical_issues_count"] == 17
    finally:
        app.dependency_overrides.clear()


def test_get_contact_quality_issues_endpoint(mock_contact_service):
    app.dependency_overrides[get_contact_service] = lambda: mock_contact_service
    client = TestClient(app)
    try:
        response = client.get("/api/v1/modules/CONTACT/quality/issues?issue=MISSING_ALL_PHONES")
        assert response.status_code == 200
        data = response.json()
        assert data["issue_code"] == "MISSING_ALL_PHONES"
        assert data["total"] == 17
    finally:
        app.dependency_overrides.clear()
