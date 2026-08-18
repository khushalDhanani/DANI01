"""
User / Login & Security Analysis Module Definition.

Identifies user authentication accounts, role catalogs, menu rights/permissions,
employee-to-user mappings, device registrations, and security data-quality metrics.
"""

from app.modules.models import (
    ModuleDefinition,
    ModuleRelationshipDefinition,
    ModuleTableDefinition,
    ModuleTableRole,
)

SecurityModuleDefinition = ModuleDefinition(
    code="SECURITY",
    name="User & Security Intelligence",
    description=(
        "Discovery, profiling, RBAC role-rights auditing, employee-to-user mappings, "
        "mobile devices, and security vulnerability checks across user authentication accounts."
    ),
    root_schema="dbo",
    root_table="SecurityUserMst",
    root_key="UserID",
    tables=[
        # 1. Primary User Master
        ModuleTableDefinition(
            schema="dbo",
            table="SecurityUserMst",
            role=ModuleTableRole.ROOT,
            required=True,
            key_columns=["UserID"],
            important_columns=[
                "UserID",
                "UserEmpID",
                "RoleID",
                "UserName",
                "UserEmail",
                "UserMobile",
                "UserADID",
                "UserIsActive",
                "UserIsDeleted",
                "IsMasterAdmin",
                "IsSecurityLogin",
                "LastAccessAPI",
                "UserEntDate",
                "IOSUser",
                "AndroidUser",
                "SMALogin",
                "MFA",
                "LoginStatus",
                "DeviceID",
                "UserID365",
            ],
            description="User authentication and login accounts master",
        ),
        # 2. Security Roles Master
        ModuleTableDefinition(
            schema="dbo",
            table="SecurityRoleMst",
            role=ModuleTableRole.LOOKUP,
            required=True,
            key_columns=["RoleID"],
            important_columns=[
                "RoleID",
                "CompID",
                "RoleDesc",
                "RoleIsActive",
                "RoleIsDeleted",
            ],
            description="Security roles catalog and definitions",
        ),
        # 3. Role Rights / Permissions
        ModuleTableDefinition(
            schema="dbo",
            table="SecurityRoleRightsMst",
            role=ModuleTableRole.DETAIL,
            required=True,
            key_columns=["RoleMenuID"],
            important_columns=[
                "RoleMenuID",
                "RoleID",
                "MenuID",
                "InsertFlag",
                "UpdateFlag",
                "DeleteFlag",
                "ViewFlag",
                "RoleMenuIsActive",
                "RoleMenuIsDeleted",
            ],
            description="Role permissions and CRUD access flags per menu/form",
        ),
        # 4. System Menus & Forms
        ModuleTableDefinition(
            schema="dbo",
            table="SecurityMenuMst",
            role=ModuleTableRole.LOOKUP,
            required=True,
            key_columns=["MenuID"],
            important_columns=[
                "MenuID",
                "MenuName",
                "FormName",
                "ShortName",
                "MenuType",
                "RouteState",
                "RoutePortal",
                "RefModuleId",
                "IsActive",
            ],
            description="System menus, forms, portals, and module routes",
        ),
        # 5. User Devices
        ModuleTableDefinition(
            schema="dbo",
            table="SecurityUserDevice",
            role=ModuleTableRole.DETAIL,
            required=False,
            key_columns=["UserDeviceID"],
            important_columns=[
                "UserDeviceID",
                "UserID",
                "DeviceID",
                "DeviceName",
                "DeviceType",
                "IsActive",
                "IsDeleted",
            ],
            description="Registered mobile and desktop login devices per user",
        ),
    ],
    relationships=[
        ModuleRelationshipDefinition(
            parent_table="dbo.EmployeeMst",
            child_table="dbo.SecurityUserMst",
            parent_key="EmpID",
            child_key="UserEmpID",
            relationship_type="ONE_TO_ONE",
            required=False,
        ),
        ModuleRelationshipDefinition(
            parent_table="dbo.SecurityRoleMst",
            child_table="dbo.SecurityUserMst",
            parent_key="RoleID",
            child_key="RoleID",
            relationship_type="ONE_TO_MANY",
            required=False,
        ),
        ModuleRelationshipDefinition(
            parent_table="dbo.SecurityRoleMst",
            child_table="dbo.SecurityRoleRightsMst",
            parent_key="RoleID",
            child_key="RoleID",
            relationship_type="ONE_TO_MANY",
            required=True,
        ),
        ModuleRelationshipDefinition(
            parent_table="dbo.SecurityMenuMst",
            child_table="dbo.SecurityRoleRightsMst",
            parent_key="MenuID",
            child_key="MenuID",
            relationship_type="ONE_TO_MANY",
            required=True,
        ),
        ModuleRelationshipDefinition(
            parent_table="dbo.SecurityUserMst",
            child_table="dbo.SecurityUserDevice",
            parent_key="UserID",
            child_key="UserID",
            relationship_type="ONE_TO_MANY",
            required=False,
        ),
    ],
)
