"""API route tests for User / Login & Security Analysis Module."""

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.security.schemas import (
    SecurityAccountOverview,
    SecurityDataQualityResponse,
    SecurityEmpLinkOverview,
    SecurityOverviewResponse,
    SecurityPostureOverview,
    SecurityQualityIssuesListResponse,
    SecurityRoleDetailResponse,
    SecurityRoleListResponse,
    SecurityUserListResponse,
)


@pytest.mark.asyncio
async def test_get_security_overview_endpoint():
    """Test GET /api/v1/modules/SECURITY/overview."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.modules.security.service.SecurityService.get_security_overview") as mock_fn:
            mock_fn.return_value = SecurityOverviewResponse(
                account_metrics=SecurityAccountOverview(
                    total_user_accounts=5420,
                    active_users=4214,
                ),
                employee_link_metrics=SecurityEmpLinkOverview(
                    total_active_employees=1316,
                    active_emps_with_active_user=1284,
                ),
                posture_metrics=SecurityPostureOverview(
                    master_admins_count=52,
                ),
                role_distribution=[],
            )

            res = await client.get("/api/v1/modules/SECURITY/overview")
            assert res.status_code == 200
            data = res.json()
            assert data["account_metrics"]["total_user_accounts"] == 5420
            assert data["employee_link_metrics"]["active_emps_with_active_user"] == 1284


@pytest.mark.asyncio
async def test_get_security_users_endpoint():
    """Test GET /api/v1/modules/SECURITY/users."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.modules.security.service.SecurityService.get_user_directory") as mock_fn:
            mock_fn.return_value = SecurityUserListResponse(
                total=10,
                limit=25,
                offset=0,
                items=[],
            )

            res = await client.get("/api/v1/modules/SECURITY/users?status_filter=ACTIVE&limit=25")
            assert res.status_code == 200
            data = res.json()
            assert data["total"] == 10


@pytest.mark.asyncio
async def test_get_security_roles_endpoint():
    """Test GET /api/v1/modules/SECURITY/roles."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.modules.security.service.SecurityService.get_roles_catalog") as mock_fn:
            mock_fn.return_value = SecurityRoleListResponse(
                total_roles=16,
                active_roles=13,
                items=[],
            )

            res = await client.get("/api/v1/modules/SECURITY/roles")
            assert res.status_code == 200
            data = res.json()
            assert data["total_roles"] == 16


@pytest.mark.asyncio
async def test_get_security_role_permissions_endpoint():
    """Test GET /api/v1/modules/SECURITY/roles/1/permissions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.modules.security.service.SecurityService.get_role_permissions") as mock_fn:
            mock_fn.return_value = SecurityRoleDetailResponse(
                role_id=1,
                role_desc="All",
                is_active=True,
                is_deleted=False,
                total_permissions=651,
                permissions=[],
            )

            res = await client.get("/api/v1/modules/SECURITY/roles/1/permissions")
            assert res.status_code == 200
            data = res.json()
            assert data["role_desc"] == "All"
            assert data["total_permissions"] == 651


@pytest.mark.asyncio
async def test_get_security_quality_endpoint():
    """Test GET /api/v1/modules/SECURITY/quality."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.modules.security.service.SecurityService.get_security_quality") as mock_fn:
            mock_fn.return_value = SecurityDataQualityResponse(
                overall_security_score=94.5,
                critical_issues_count=145,
                rules=[],
            )

            res = await client.get("/api/v1/modules/SECURITY/quality")
            assert res.status_code == 200
            data = res.json()
            assert data["overall_security_score"] == 94.5


@pytest.mark.asyncio
async def test_get_security_quality_issues_endpoint():
    """Test GET /api/v1/modules/SECURITY/quality/issues."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch(
            "app.modules.security.service.SecurityService.get_security_quality_issues"
        ) as mock_fn:
            mock_fn.return_value = SecurityQualityIssuesListResponse(
                issue_code="ACTIVE_USER_INACTIVE_EMP",
                issue_name="Active User Linked to Inactive Employee",
                severity="CRITICAL",
                total=125,
                limit=25,
                offset=0,
                items=[],
            )

            res = await client.get(
                "/api/v1/modules/SECURITY/quality/issues?issue=ACTIVE_USER_INACTIVE_EMP"
            )
            assert res.status_code == 200
            data = res.json()
            assert data["total"] == 125
            assert data["issue_code"] == "ACTIVE_USER_INACTIVE_EMP"
