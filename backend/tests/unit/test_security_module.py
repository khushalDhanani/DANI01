from unittest.mock import patch

import pytest

from app.modules.definitions.security import SecurityModuleDefinition
from app.modules.security.analyzer import SecurityAnalyzer
from app.modules.security.schemas import (
    SecurityAccountOverview,
    SecurityDataQualityResponse,
    SecurityEmpLinkOverview,
    SecurityOverviewResponse,
    SecurityPostureOverview,
    SecurityRoleListResponse,
)
from app.modules.security.service import (
    SecurityService,
    sql_active_employee_predicate,
    sql_active_user_predicate,
)


def test_security_module_definition():
    """Test module definition metadata."""
    module_def = SecurityModuleDefinition
    assert module_def.code == "SECURITY"
    assert module_def.name == "User & Security Intelligence"
    assert len(module_def.tables) == 5
    assert module_def.root_table == "SecurityUserMst"
    assert len(module_def.relationships) == 5


def test_sql_predicates():
    """Test SSoT active qualification predicates."""
    emp_pred = sql_active_employee_predicate("e")
    assert "e.EmpIsActive = 1" in emp_pred
    assert "e.EmpIsDeleted = 0" in emp_pred

    user_pred = sql_active_user_predicate("u")
    assert "u.UserIsActive = 1" in user_pred
    assert "u.UserIsDeleted = 0" in user_pred


@pytest.mark.asyncio
async def test_get_security_overview_mocked():
    """Test get_security_overview with mocked database responses."""
    service = SecurityService()

    mock_account = [
        {
            "total_user_accounts": 5420,
            "active_users": 4214,
            "inactive_users": 785,
            "deleted_users": 421,
            "linked_to_employee": 2459,
            "unlinked_users": 2961,
            "master_admins_count": 52,
            "mfa_enabled_count": 13,
            "mobile_app_users_count": 1554,
            "sma_users_count": 219,
            "api_accessed_count": 2333,
            "never_logged_in_count": 3087,
        }
    ]
    mock_emp = [{"total_active_employees": 1316, "active_emps_with_active_user": 1284}]
    mock_dev = [{"c": 2038}]
    mock_roles = [
        {"RoleID": 2, "RoleDesc": "Employee", "total_users": 2355, "active_users": 1364},
        {"RoleID": 13, "RoleDesc": "Candidate", "total_users": 2600, "active_users": 2571},
    ]

    with patch(
        "app.modules.security.service.execute_readonly_query",
        side_effect=[mock_account, mock_emp, mock_dev, mock_roles],
    ):
        res = await service.get_security_overview()
        assert res.account_metrics.total_user_accounts == 5420
        assert res.account_metrics.active_users == 4214
        assert res.employee_link_metrics.total_active_employees == 1316
        assert res.employee_link_metrics.active_emps_with_active_user == 1284
        assert res.employee_link_metrics.active_emps_without_active_user == 32
        assert res.posture_metrics.master_admins_count == 52
        assert res.posture_metrics.total_registered_devices == 2038
        assert len(res.role_distribution) == 2


@pytest.mark.asyncio
async def test_get_user_directory_mocked():
    """Test get_user_directory with pagination and search."""
    service = SecurityService()

    mock_count = [{"total": 1}]
    mock_users = [
        {
            "UserID": 1,
            "UserName": "Admin",
            "UserEmail": "admin@aether.co.in",
            "UserMobile": "9876543210",
            "RoleID": 1,
            "RoleDesc": "All",
            "UserEmpID": 1,
            "EmpCode": "1001",
            "emp_name": "John Doe",
            "emp_status": "ACTIVE",
            "UserIsActive": True,
            "UserIsDeleted": False,
            "IsMasterAdmin": True,
            "MFA": True,
            "is_mobile_app_user": True,
            "LastAccessAPI": None,
            "UserEntDate": None,
            "registered_devices_count": 2,
        }
    ]

    with patch(
        "app.modules.security.service.execute_readonly_query",
        side_effect=[mock_count, mock_users],
    ):
        res = await service.get_user_directory(limit=10, offset=0)
        assert res.total == 1
        assert len(res.items) == 1
        assert res.items[0].username == "Admin"
        assert res.items[0].is_master_admin is True
        assert res.items[0].registered_devices_count == 2


@pytest.mark.asyncio
async def test_get_roles_catalog_mocked():
    """Test get_roles_catalog."""
    service = SecurityService()

    mock_roles = [
        {
            "RoleID": 1,
            "RoleDesc": "All",
            "CompID": 1,
            "RoleIsActive": True,
            "RoleIsDeleted": False,
            "total_assigned_users": 10,
            "active_assigned_users": 6,
            "assigned_menus_count": 651,
            "insert_perms_count": 651,
            "update_perms_count": 651,
            "delete_perms_count": 651,
            "view_perms_count": 651,
        }
    ]

    with patch(
        "app.modules.security.service.execute_readonly_query",
        return_value=mock_roles,
    ):
        res = await service.get_roles_catalog()
        assert res.total_roles == 1
        assert res.active_roles == 1
        assert res.items[0].role_desc == "All"
        assert res.items[0].assigned_menus_count == 651


@pytest.mark.asyncio
async def test_get_security_quality_mocked():
    """Test get_security_quality evaluation."""
    service = SecurityService()

    mock_rules = [
        {"code": "ORPHAN_USER_EMP_REF", "cnt": 0},
        {"code": "ACTIVE_USER_INACTIVE_EMP", "cnt": 125},
        {"code": "PRIVILEGED_INACTIVE_EMP_RISK", "cnt": 20},
        {"code": "ACTIVE_AND_DELETED_USER", "cnt": 56},
        {"code": "DUPLICATE_ACTIVE_USERNAME", "cnt": 30},
        {"code": "DUPLICATE_ACTIVE_LOGIN_EMAIL", "cnt": 28},
        {"code": "MULTIPLE_ACTIVE_USERS_PER_EMP", "cnt": 0},
        {"code": "MISSING_USER_ROLE", "cnt": 1},
        {"code": "ROLE_WITHOUT_PERMISSIONS", "cnt": 1},
        {"code": "ROLE_IS_DELETED_IN_USE", "cnt": 0},
        {"code": "EMP_WITHOUT_USER_LOGIN", "cnt": 32},
        {"code": "USER_WITHOUT_EMP_LINK", "cnt": 2961},
        {"code": "NEVER_LOGGED_IN_ACCOUNT", "cnt": 3087},
        {"code": "MFA_DISABLED_ADMIN", "cnt": 45},
    ]

    with patch(
        "app.modules.security.service.execute_readonly_query",
        return_value=mock_rules,
    ):
        res = await service.get_security_quality()
        assert len(res.rules) == 14
        assert res.critical_issues_count == 145
        assert res.warning_issues_count == 116
        assert res.info_issues_count == 6125


@pytest.mark.asyncio
async def test_get_role_permissions_mocked():
    """Test get_role_permissions found and not found."""
    service = SecurityService()

    # Not found
    with patch("app.modules.security.service.execute_readonly_query", return_value=[]):
        res = await service.get_role_permissions(role_id=999)
        assert res.role_id == 999
        assert res.is_deleted is True
        assert res.total_permissions == 0

    # Found
    mock_role = [{"RoleID": 1, "RoleDesc": "All", "RoleIsActive": True, "RoleIsDeleted": False}]
    mock_rights = [
        {
            "RoleMenuID": 10,
            "MenuID": 100,
            "MenuName": "Dashboard",
            "FormName": "frmDashboard",
            "RoutePortal": "portal",
            "InsertFlag": True,
            "UpdateFlag": True,
            "DeleteFlag": False,
            "ViewFlag": True,
            "RoleMenuIsActive": True,
            "RoleMenuIsDeleted": False,
        }
    ]
    with patch(
        "app.modules.security.service.execute_readonly_query",
        side_effect=[mock_role, mock_rights],
    ):
        res = await service.get_role_permissions(role_id=1)
        assert res.role_id == 1
        assert res.role_desc == "All"
        assert res.total_permissions == 1
        assert res.permissions[0].menu_name == "Dashboard"
        assert res.permissions[0].can_insert is True
        assert res.permissions[0].can_delete is False


@pytest.mark.asyncio
async def test_get_security_quality_issues_all_rules_mocked():
    """Test get_security_quality_issues for all 14 security rules."""
    service = SecurityService()

    rules = [
        "ORPHAN_USER_EMP_REF",
        "ACTIVE_USER_INACTIVE_EMP",
        "PRIVILEGED_INACTIVE_EMP_RISK",
        "ACTIVE_AND_DELETED_USER",
        "DUPLICATE_ACTIVE_USERNAME",
        "DUPLICATE_ACTIVE_LOGIN_EMAIL",
        "MULTIPLE_ACTIVE_USERS_PER_EMP",
        "MISSING_USER_ROLE",
        "ROLE_WITHOUT_PERMISSIONS",
        "ROLE_IS_DELETED_IN_USE",
        "EMP_WITHOUT_USER_LOGIN",
        "USER_WITHOUT_EMP_LINK",
        "NEVER_LOGGED_IN_ACCOUNT",
        "MFA_DISABLED_ADMIN",
    ]

    mock_count = [{"total": 1}]
    mock_items = [
        {
            "record_id": 1,
            "entity_type": "USER",
            "entity_name": "Test User",
            "issue_detail": "Sample issue detail",
            "account_role": "Employee",
            "status_detail": "Active Risk",
        }
    ]

    for rule_code in rules:
        with patch(
            "app.modules.security.service.execute_readonly_query",
            side_effect=[mock_count, mock_items],
        ):
            res = await service.get_security_quality_issues(issue_code=rule_code, search="Test")
            assert res.issue_code == rule_code
            assert res.total == 1
            assert len(res.items) == 1
            assert res.items[0].entity_name == "Test User"

    # Unknown rule
    res_unknown = await service.get_security_quality_issues(issue_code="NON_EXISTENT_RULE")
    assert res_unknown.total == 0
    assert len(res_unknown.items) == 0


@pytest.mark.asyncio
async def test_exports_mocked():
    """Test user directory and quality issues CSV exports."""
    service = SecurityService()

    mock_count = [{"total": 1}]
    mock_users = [
        {
            "UserID": 1,
            "UserName": "Admin",
            "UserEmail": "admin@aether.co.in",
            "UserMobile": "9876543210",
            "RoleID": 1,
            "RoleDesc": "All",
            "UserEmpID": 1,
            "EmpCode": "1001",
            "emp_name": "John Doe",
            "emp_status": "ACTIVE",
            "UserIsActive": True,
            "UserIsDeleted": False,
            "IsMasterAdmin": True,
            "MFA": True,
            "is_mobile_app_user": True,
            "LastAccessAPI": None,
            "UserEntDate": None,
            "registered_devices_count": 2,
        }
    ]

    with patch(
        "app.modules.security.service.execute_readonly_query",
        side_effect=[mock_count, mock_users],
    ):
        csv_out = await service.export_user_directory(status_filter="ACTIVE")
        assert "User ID,Username,Email" in csv_out
        assert "admin@aether.co.in" in csv_out

    mock_items = [
        {
            "record_id": 1,
            "entity_type": "USER",
            "entity_name": "Test User",
            "issue_detail": "Sample issue detail",
            "account_role": "Employee",
            "status_detail": "Active Risk",
        }
    ]
    with patch(
        "app.modules.security.service.execute_readonly_query",
        side_effect=[mock_count, mock_items],
    ):
        csv_issues = await service.export_security_quality_issues(
            issue_code="ACTIVE_USER_INACTIVE_EMP"
        )
        assert "Record ID,Entity Type,Entity Name" in csv_issues
        assert "ACTIVE_USER_INACTIVE_EMP" in csv_issues


@pytest.mark.asyncio
async def test_security_analyzer():
    """Test SecurityAnalyzer coordinator."""
    mock_service = SecurityService()

    with (
        patch.object(mock_service, "get_security_overview") as mock_ov,
        patch.object(mock_service, "get_roles_catalog") as mock_rc,
        patch.object(mock_service, "get_security_quality") as mock_ql,
    ):
        mock_ov.return_value = SecurityOverviewResponse(
            account_metrics=SecurityAccountOverview(),
            employee_link_metrics=SecurityEmpLinkOverview(),
            posture_metrics=SecurityPostureOverview(),
            role_distribution=[],
        )
        mock_rc.return_value = SecurityRoleListResponse()
        mock_ql.return_value = SecurityDataQualityResponse()

        analyzer = SecurityAnalyzer(service=mock_service)
        res = await analyzer.analyze()
        assert res["module"] == "SECURITY"
        assert "overview" in res
        assert "roles" in res
        assert "quality" in res
