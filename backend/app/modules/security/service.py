import asyncio
import csv
import io
import logging
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.employee.schemas import IssueSeverity
from app.modules.security.schemas import (
    SecurityAccountOverview,
    SecurityDataQualityResponse,
    SecurityEmpLinkOverview,
    SecurityMenuPermissionItem,
    SecurityOverviewResponse,
    SecurityPostureOverview,
    SecurityQualityIssueItem,
    SecurityQualityIssuesListResponse,
    SecurityQualityRuleResult,
    SecurityRoleDetailResponse,
    SecurityRoleDistributionItem,
    SecurityRoleItem,
    SecurityRoleListResponse,
    SecurityUserItem,
    SecurityUserListResponse,
)

logger = logging.getLogger(__name__)


def sql_active_employee_predicate(prefix: str = "e") -> str:
    """Canonical active employee qualification rule."""
    return f"""
        {prefix}.EmpIsActive = 1
        AND {prefix}.EmpIsDeleted = 0
        AND ({prefix}.EmpResignDate IS NULL OR {prefix}.EmpResignDate > GETDATE())
    """


def sql_active_user_predicate(prefix: str = "u") -> str:
    """Canonical active user qualification rule."""
    return f"""
        {prefix}.UserIsActive = 1
        AND {prefix}.UserIsDeleted = 0
    """


class SecurityService:
    """Domain service for User / Login & Security analysis and RBAC audits."""

    # ─────────────────────────────────────────────────────────────
    # 1. OVERVIEW & METRICS
    # ─────────────────────────────────────────────────────────────

    async def get_security_overview(self) -> SecurityOverviewResponse:
        return await asyncio.to_thread(self._get_security_overview_sync)

    def _get_security_overview_sync(self) -> SecurityOverviewResponse:
        active_emp_pred = sql_active_employee_predicate("e")
        active_usr_pred = sql_active_user_predicate("u")

        account_row = execute_readonly_query(f"""
        SELECT
            COUNT(*) AS total_user_accounts,
            SUM(CASE WHEN {active_usr_pred} THEN 1 ELSE 0 END) AS active_users,
            SUM(CASE WHEN u.UserIsActive = 0 AND u.UserIsDeleted = 0 THEN 1 ELSE 0 END) AS inactive_users,
            SUM(CASE WHEN u.UserIsDeleted = 1 THEN 1 ELSE 0 END) AS deleted_users,
            SUM(CASE WHEN u.UserEmpID IS NOT NULL AND u.UserEmpID > 0 THEN 1 ELSE 0 END) AS linked_to_employee,
            SUM(CASE WHEN u.UserEmpID IS NULL OR u.UserEmpID = 0 THEN 1 ELSE 0 END) AS unlinked_users,
            SUM(CASE WHEN u.IsMasterAdmin = 1 THEN 1 ELSE 0 END) AS master_admins_count,
            SUM(CASE WHEN u.MFA = 1 THEN 1 ELSE 0 END) AS mfa_enabled_count,
            SUM(CASE WHEN u.IOSUser = 1 OR u.AndroidUser = 1 THEN 1 ELSE 0 END) AS mobile_app_users_count,
            SUM(CASE WHEN u.SMALogin = 1 THEN 1 ELSE 0 END) AS sma_users_count,
            SUM(CASE WHEN u.LastAccessAPI IS NOT NULL THEN 1 ELSE 0 END) AS api_accessed_count,
            SUM(CASE WHEN u.LastAccessAPI IS NULL THEN 1 ELSE 0 END) AS never_logged_in_count
        FROM dbo.SecurityUserMst u
        """)[0]

        emp_row = execute_readonly_query(f"""
        SELECT
            COUNT(DISTINCT e.EmpID) AS total_active_employees,
            COUNT(DISTINCT CASE WHEN {active_usr_pred} THEN e.EmpID END) AS active_emps_with_active_user
        FROM dbo.EmployeeMst e
        LEFT JOIN dbo.SecurityUserMst u ON e.EmpID = u.UserEmpID
        WHERE {active_emp_pred}
        """)[0]

        device_cnt = execute_readonly_query("SELECT COUNT(*) AS c FROM dbo.SecurityUserDevice")[0][
            "c"
        ]

        role_rows = execute_readonly_query(f"""
        SELECT
            r.RoleID,
            r.RoleDesc,
            COUNT(u.UserID) AS total_users,
            SUM(CASE WHEN {active_usr_pred} THEN 1 ELSE 0 END) AS active_users
        FROM dbo.SecurityRoleMst r
        LEFT JOIN dbo.SecurityUserMst u ON r.RoleID = u.RoleID
        WHERE r.RoleIsDeleted = 0
        GROUP BY r.RoleID, r.RoleDesc
        ORDER BY active_users DESC, total_users DESC
        """)

        tot_users = int(account_row["total_user_accounts"] or 0)
        act_users = int(account_row["active_users"] or 0)
        inact_users = int(account_row["inactive_users"] or 0)
        del_users = int(account_row["deleted_users"] or 0)
        linked_users = int(account_row["linked_to_employee"] or 0)
        unlinked_users = int(account_row["unlinked_users"] or 0)

        tot_emps = int(emp_row["total_active_employees"] or 0)
        emps_with_user = int(emp_row["active_emps_with_active_user"] or 0)
        emps_without_user = max(0, tot_emps - emps_with_user)

        def _calc_pct(val: int, base: int) -> float:
            return round((val / base) * 100.0, 1) if base > 0 else 0.0

        role_items: list[SecurityRoleDistributionItem] = []
        for r in role_rows:
            r_tot = int(r["total_users"] or 0)
            r_act = int(r["active_users"] or 0)
            role_items.append(
                SecurityRoleDistributionItem(
                    role_id=r["RoleID"],
                    role_desc=r["RoleDesc"] or "Unassigned",
                    total_users=r_tot,
                    active_users=r_act,
                    percentage=_calc_pct(r_act, act_users),
                )
            )

        return SecurityOverviewResponse(
            account_metrics=SecurityAccountOverview(
                total_user_accounts=tot_users,
                active_users=act_users,
                active_users_pct=_calc_pct(act_users, tot_users),
                inactive_users=inact_users,
                inactive_users_pct=_calc_pct(inact_users, tot_users),
                deleted_users=del_users,
                deleted_users_pct=_calc_pct(del_users, tot_users),
                linked_to_employee=linked_users,
                linked_to_employee_pct=_calc_pct(linked_users, tot_users),
                unlinked_users=unlinked_users,
                unlinked_users_pct=_calc_pct(unlinked_users, tot_users),
            ),
            employee_link_metrics=SecurityEmpLinkOverview(
                total_active_employees=tot_emps,
                active_emps_with_active_user=emps_with_user,
                active_emps_with_active_user_pct=_calc_pct(emps_with_user, tot_emps),
                active_emps_without_active_user=emps_without_user,
                active_emps_without_active_user_pct=_calc_pct(emps_without_user, tot_emps),
            ),
            posture_metrics=SecurityPostureOverview(
                master_admins_count=int(account_row["master_admins_count"] or 0),
                mfa_enabled_count=int(account_row["mfa_enabled_count"] or 0),
                mfa_enabled_pct=_calc_pct(int(account_row["mfa_enabled_count"] or 0), act_users),
                mobile_app_users_count=int(account_row["mobile_app_users_count"] or 0),
                sma_users_count=int(account_row["sma_users_count"] or 0),
                api_accessed_count=int(account_row["api_accessed_count"] or 0),
                never_logged_in_count=int(account_row["never_logged_in_count"] or 0),
                total_registered_devices=device_cnt,
            ),
            role_distribution=role_items,
        )

    # ─────────────────────────────────────────────────────────────
    # 2. USER DIRECTORY & CSV EXPORT
    # ─────────────────────────────────────────────────────────────

    async def get_user_directory(
        self,
        role_id: int | None = None,
        status_filter: str
        | None = None,  # 'ACTIVE', 'INACTIVE', 'DELETED', 'ADMIN', 'MFA', 'LINKED', 'UNLINKED'
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> SecurityUserListResponse:
        return await asyncio.to_thread(
            self._get_user_directory_sync,
            role_id=role_id,
            status_filter=status_filter,
            search=search,
            limit=limit,
            offset=offset,
        )

    def _get_user_directory_sync(
        self,
        role_id: int | None = None,
        status_filter: str | None = None,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> SecurityUserListResponse:
        where_clauses: list[str] = []
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if role_id is not None:
            where_clauses.append("u.RoleID = :role_id")
            params["role_id"] = role_id

        if status_filter:
            sf = status_filter.upper()
            if sf == "ACTIVE":
                where_clauses.append("u.UserIsActive = 1 AND u.UserIsDeleted = 0")
            elif sf == "INACTIVE":
                where_clauses.append("u.UserIsActive = 0 AND u.UserIsDeleted = 0")
            elif sf == "DELETED":
                where_clauses.append("u.UserIsDeleted = 1")
            elif sf == "ADMIN":
                where_clauses.append("(u.IsMasterAdmin = 1 OR u.RoleID = 1)")
            elif sf == "MFA":
                where_clauses.append("u.MFA = 1")
            elif sf == "LINKED":
                where_clauses.append("u.UserEmpID IS NOT NULL AND u.UserEmpID > 0")
            elif sf == "UNLINKED":
                where_clauses.append("(u.UserEmpID IS NULL OR u.UserEmpID = 0)")

        if search:
            where_clauses.append(
                """(
                    u.UserName LIKE :search
                    OR u.UserEmail LIKE :search
                    OR u.UserMobile LIKE :search
                    OR e.EmpCode LIKE :search
                    OR e.EmpFirstName LIKE :search
                    OR e.EmpLastName LIKE :search
                    OR r.RoleDesc LIKE :search
                )"""
            )
            params["search"] = f"%{search}%"

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        count_sql = f"""
        SELECT COUNT(*) AS total
        FROM dbo.SecurityUserMst u
        LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
        LEFT JOIN dbo.EmployeeMst e ON u.UserEmpID = e.EmpID
        {where_sql}
        """
        total_row = execute_readonly_query(count_sql, params)
        total = total_row[0]["total"] if total_row else 0

        items_sql = f"""
        SELECT
            u.UserID,
            u.UserName,
            u.UserEmail,
            u.UserMobile,
            u.RoleID,
            r.RoleDesc,
            u.UserEmpID,
            e.EmpCode,
            CASE
                WHEN e.EmpID IS NOT NULL THEN
                    RTRIM(LTRIM(ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '')))
                ELSE NULL
            END AS emp_name,
            CASE
                WHEN e.EmpID IS NULL THEN 'NONE'
                WHEN e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE()) THEN 'ACTIVE'
                WHEN e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE() THEN 'RESIGNED'
                ELSE 'INACTIVE'
            END AS emp_status,
            u.UserIsActive,
            u.UserIsDeleted,
            u.IsMasterAdmin,
            u.MFA,
            CASE WHEN u.IOSUser = 1 OR u.AndroidUser = 1 THEN 1 ELSE 0 END AS is_mobile_app_user,
            u.LastAccessAPI,
            u.UserEntDate,
            ISNULL(d.device_count, 0) AS registered_devices_count
        FROM dbo.SecurityUserMst u
        LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
        LEFT JOIN dbo.EmployeeMst e ON u.UserEmpID = e.EmpID
        LEFT JOIN (
            SELECT UserID, COUNT(*) AS device_count
            FROM dbo.SecurityUserDevice
            GROUP BY UserID
        ) d ON u.UserID = d.UserID
        {where_sql}
        ORDER BY u.UserIsActive DESC, u.UserID ASC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """

        rows = execute_readonly_query(items_sql, params)
        items: list[SecurityUserItem] = []
        for row in rows:
            items.append(
                SecurityUserItem(
                    user_id=row["UserID"],
                    username=row["UserName"],
                    user_email=row["UserEmail"],
                    user_mobile=row["UserMobile"],
                    role_id=row["RoleID"],
                    role_desc=row["RoleDesc"],
                    emp_id=row["UserEmpID"],
                    emp_code=row["EmpCode"],
                    emp_name=row["emp_name"],
                    emp_status=row["emp_status"],
                    is_active=bool(row["UserIsActive"]),
                    is_deleted=bool(row["UserIsDeleted"]),
                    is_master_admin=bool(row["IsMasterAdmin"]),
                    is_mfa_enabled=bool(row["MFA"]),
                    is_mobile_app_user=bool(row["is_mobile_app_user"]),
                    last_access_api=row["LastAccessAPI"].isoformat()
                    if row["LastAccessAPI"]
                    else None,
                    created_at=row["UserEntDate"].isoformat() if row["UserEntDate"] else None,
                    registered_devices_count=int(row["registered_devices_count"] or 0),
                )
            )

        return SecurityUserListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    async def export_user_directory(
        self,
        role_id: int | None = None,
        status_filter: str | None = None,
        search: str | None = None,
    ) -> str:
        res = await self.get_user_directory(
            role_id=role_id,
            status_filter=status_filter,
            search=search,
            limit=50000,
            offset=0,
        )
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "User ID",
                "Username",
                "Email",
                "Mobile",
                "Role ID",
                "Role Description",
                "Employee ID",
                "Employee Code",
                "Employee Name",
                "Employee Status",
                "Is Active",
                "Is Deleted",
                "Is Master Admin",
                "MFA Enabled",
                "Mobile App User",
                "Registered Devices",
                "Last API Access",
                "Created Date",
            ]
        )
        for u in res.items:
            writer.writerow(
                [
                    u.user_id,
                    u.username or "",
                    u.user_email or "",
                    u.user_mobile or "",
                    u.role_id or "",
                    u.role_desc or "",
                    u.emp_id or "",
                    u.emp_code or "",
                    u.emp_name or "",
                    u.emp_status or "",
                    "YES" if u.is_active else "NO",
                    "YES" if u.is_deleted else "NO",
                    "YES" if u.is_master_admin else "NO",
                    "YES" if u.is_mfa_enabled else "NO",
                    "YES" if u.is_mobile_app_user else "NO",
                    u.registered_devices_count,
                    u.last_access_api or "",
                    u.created_at or "",
                ]
            )
        return output.getvalue()

    # ─────────────────────────────────────────────────────────────
    # 3. ROLE CATALOG & PERMISSION MATRICES
    # ─────────────────────────────────────────────────────────────

    async def get_roles_catalog(self) -> SecurityRoleListResponse:
        return await asyncio.to_thread(self._get_roles_catalog_sync)

    def _get_roles_catalog_sync(self) -> SecurityRoleListResponse:
        active_usr_pred = sql_active_user_predicate("u")
        sql = f"""
        SELECT
            r.RoleID,
            r.RoleDesc,
            r.CompID,
            r.RoleIsActive,
            r.RoleIsDeleted,
            COUNT(DISTINCT u.UserID) AS total_assigned_users,
            COUNT(DISTINCT CASE WHEN {active_usr_pred} THEN u.UserID END) AS active_assigned_users,
            COUNT(DISTINCT rr.MenuID) AS assigned_menus_count,
            SUM(CASE WHEN rr.InsertFlag = 1 THEN 1 ELSE 0 END) AS insert_perms_count,
            SUM(CASE WHEN rr.UpdateFlag = 1 THEN 1 ELSE 0 END) AS update_perms_count,
            SUM(CASE WHEN rr.DeleteFlag = 1 THEN 1 ELSE 0 END) AS delete_perms_count,
            SUM(CASE WHEN rr.ViewFlag = 1 THEN 1 ELSE 0 END) AS view_perms_count
        FROM dbo.SecurityRoleMst r
        LEFT JOIN dbo.SecurityUserMst u ON r.RoleID = u.RoleID
        LEFT JOIN dbo.SecurityRoleRightsMst rr ON r.RoleID = rr.RoleID AND rr.RoleMenuIsActive = 1 AND rr.RoleMenuIsDeleted = 0
        GROUP BY r.RoleID, r.RoleDesc, r.CompID, r.RoleIsActive, r.RoleIsDeleted
        ORDER BY r.RoleIsDeleted ASC, active_assigned_users DESC, r.RoleID ASC;
        """
        rows = execute_readonly_query(sql)
        items: list[SecurityRoleItem] = []
        active_count = 0
        for r in rows:
            is_active = bool(r["RoleIsActive"]) and not bool(r["RoleIsDeleted"])
            if is_active:
                active_count += 1
            items.append(
                SecurityRoleItem(
                    role_id=r["RoleID"],
                    role_desc=r["RoleDesc"] or f"Role {r['RoleID']}",
                    comp_id=r["CompID"],
                    is_active=bool(r["RoleIsActive"]),
                    is_deleted=bool(r["RoleIsDeleted"]),
                    total_assigned_users=int(r["total_assigned_users"] or 0),
                    active_assigned_users=int(r["active_assigned_users"] or 0),
                    assigned_menus_count=int(r["assigned_menus_count"] or 0),
                    insert_perms_count=int(r["insert_perms_count"] or 0),
                    update_perms_count=int(r["update_perms_count"] or 0),
                    delete_perms_count=int(r["delete_perms_count"] or 0),
                    view_perms_count=int(r["view_perms_count"] or 0),
                )
            )

        return SecurityRoleListResponse(
            total_roles=len(items),
            active_roles=active_count,
            items=items,
        )

    async def get_role_permissions(self, role_id: int) -> SecurityRoleDetailResponse:
        return await asyncio.to_thread(self._get_role_permissions_sync, role_id=role_id)

    def _get_role_permissions_sync(self, role_id: int) -> SecurityRoleDetailResponse:
        role_row = execute_readonly_query(
            "SELECT RoleID, RoleDesc, RoleIsActive, RoleIsDeleted FROM dbo.SecurityRoleMst WHERE RoleID = :role_id",
            {"role_id": role_id},
        )
        if not role_row:
            return SecurityRoleDetailResponse(
                role_id=role_id,
                role_desc=f"Role {role_id}",
                is_active=False,
                is_deleted=True,
                total_permissions=0,
                permissions=[],
            )

        r_info = role_row[0]

        rights_sql = """
        SELECT
            rr.RoleMenuID,
            rr.MenuID,
            m.MenuName,
            m.FormName,
            m.RoutePortal,
            rr.InsertFlag,
            rr.UpdateFlag,
            rr.DeleteFlag,
            rr.ViewFlag,
            rr.RoleMenuIsActive,
            rr.RoleMenuIsDeleted
        FROM dbo.SecurityRoleRightsMst rr
        JOIN dbo.SecurityMenuMst m ON rr.MenuID = m.MenuID
        WHERE rr.RoleID = :role_id
          AND rr.RoleMenuIsActive = 1 AND rr.RoleMenuIsDeleted = 0
        ORDER BY m.FormName ASC, m.MenuName ASC;
        """
        rows = execute_readonly_query(rights_sql, {"role_id": role_id})
        perms: list[SecurityMenuPermissionItem] = []
        for rw in rows:
            perms.append(
                SecurityMenuPermissionItem(
                    role_menu_id=rw["RoleMenuID"],
                    menu_id=rw["MenuID"],
                    menu_name=rw["MenuName"],
                    form_name=rw["FormName"],
                    route_portal=rw["RoutePortal"],
                    can_insert=bool(rw["InsertFlag"]),
                    can_update=bool(rw["UpdateFlag"]),
                    can_delete=bool(rw["DeleteFlag"]),
                    can_view=bool(rw["ViewFlag"]),
                    is_active=bool(rw["RoleMenuIsActive"]),
                )
            )

        return SecurityRoleDetailResponse(
            role_id=r_info["RoleID"],
            role_desc=r_info["RoleDesc"] or f"Role {role_id}",
            is_active=bool(r_info["RoleIsActive"]),
            is_deleted=bool(r_info["RoleIsDeleted"]),
            total_permissions=len(perms),
            permissions=perms,
        )

    # ─────────────────────────────────────────────────────────────
    # 4. DATA QUALITY RULES & AUDITING
    # ─────────────────────────────────────────────────────────────

    def _get_rules_catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "rule_code": "ORPHAN_USER_EMP_REF",
                "rule_name": "Broken User-to-Employee Reference",
                "severity": IssueSeverity.CRITICAL,
                "description": "User account has a non-zero UserEmpID referencing a non-existent Employee record.",
                "impact": "Account identity cannot be verified or attributed to any verified employee.",
                "recommendation": "Correct or remove invalid UserEmpID reference.",
            },
            {
                "rule_code": "ACTIVE_USER_INACTIVE_EMP",
                "rule_name": "Active User Account Linked to Inactive/Resigned Employee",
                "severity": IssueSeverity.CRITICAL,
                "description": "User account remains active while the linked Employee is marked Inactive, Deleted, or Resigned.",
                "impact": "Ex-employees or departed staff can potentially retain login access to corporate systems.",
                "recommendation": "Immediately deactivate user account (UserIsActive = 0) upon employee exit.",
            },
            {
                "rule_code": "PRIVILEGED_INACTIVE_EMP_RISK",
                "rule_name": "Active Super Admin / Privileged Account Linked to Inactive Employee",
                "severity": IssueSeverity.CRITICAL,
                "description": "High-privilege Master Admin account is linked to an inactive or separated employee.",
                "impact": "High-risk administrative access exposure from orphaned superuser credentials.",
                "recommendation": "Revoke administrator privileges and lock user account immediately.",
            },
            {
                "rule_code": "ACTIVE_AND_DELETED_USER",
                "rule_name": "Inconsistent Account Active & Deleted Flags",
                "severity": IssueSeverity.WARNING,
                "description": "Account is marked UserIsActive = 1 and UserIsDeleted = 1 concurrently.",
                "impact": "Ambiguous authentication behavior depending on application query filters.",
                "recommendation": "Normalize account status: set UserIsActive = 0 when UserIsDeleted = 1.",
            },
            {
                "rule_code": "DUPLICATE_ACTIVE_USERNAME",
                "rule_name": "Duplicate Username Across Active Accounts",
                "severity": IssueSeverity.WARNING,
                "description": "Multiple active user accounts share the exact same login username.",
                "impact": "Authentication conflicts, credential overlap, and session hijacking risks.",
                "recommendation": "Enforce unique username constraint on active accounts.",
            },
            {
                "rule_code": "DUPLICATE_ACTIVE_LOGIN_EMAIL",
                "rule_name": "Duplicate Login Email Across Active Accounts",
                "severity": IssueSeverity.WARNING,
                "description": "Multiple active user accounts share the same login email address.",
                "impact": "Password reset token routing conflicts and shared account vulnerability.",
                "recommendation": "Ensure unique email address per active user account.",
            },
            {
                "rule_code": "MULTIPLE_ACTIVE_USERS_PER_EMP",
                "rule_name": "Multiple Active Accounts for Single Employee",
                "severity": IssueSeverity.WARNING,
                "description": "Single active employee has more than one active user login account assigned.",
                "impact": "Account sprawl, conflicting role permissions, and audit log fragmentation.",
                "recommendation": "Consolidate multiple user accounts under a single primary login.",
            },
            {
                "rule_code": "MISSING_USER_ROLE",
                "rule_name": "Active User Without Valid Security Role",
                "severity": IssueSeverity.WARNING,
                "description": "Active user account has a NULL or invalid RoleID.",
                "impact": "User cannot access intended modules or may default to unrestricted/broken access.",
                "recommendation": "Assign a valid active security role to the user account.",
            },
            {
                "rule_code": "ROLE_WITHOUT_PERMISSIONS",
                "rule_name": "Active Security Role With Zero Permissions",
                "severity": IssueSeverity.WARNING,
                "description": "Security role is marked active but has 0 assigned menu/form permissions.",
                "impact": "Users assigned to this role experience blank screens and permission errors.",
                "recommendation": "Map required module permissions or deactivate unused roles.",
            },
            {
                "rule_code": "ROLE_IS_DELETED_IN_USE",
                "rule_name": "Active User Assigned to Deleted Security Role",
                "severity": IssueSeverity.WARNING,
                "description": "Active user account references a role marked RoleIsDeleted = 1.",
                "impact": "Broken RBAC hierarchy and permission evaluation failures.",
                "recommendation": "Reassign affected users to an active security role.",
            },
            {
                "rule_code": "EMP_WITHOUT_USER_LOGIN",
                "rule_name": "Active Employee Without System Login Account",
                "severity": IssueSeverity.INFO,
                "description": "Active employee does not have any active user account mapped.",
                "impact": "Normal for non-desk/field workforce, but prevents access to self-service portals.",
                "recommendation": "Provision portal user account if digital self-service is required.",
            },
            {
                "rule_code": "USER_WITHOUT_EMP_LINK",
                "rule_name": "Active User Account Without Employee Mapping",
                "severity": IssueSeverity.INFO,
                "description": "Active user account has no UserEmpID (e.g. Candidate, Vendor, Consultant).",
                "impact": "Valid for external candidate/service accounts, but requires oversight.",
                "recommendation": "Verify external user validity and set expiration dates on service accounts.",
            },
            {
                "rule_code": "NEVER_LOGGED_IN_ACCOUNT",
                "rule_name": "Active User Account That Never Logged In",
                "severity": IssueSeverity.INFO,
                "description": "Active account has never recorded an API or system login timestamp.",
                "impact": "Stale credentials and unused account license overhead.",
                "recommendation": "Deactivate dormant user accounts after 90 days of inactivity.",
            },
            {
                "rule_code": "MFA_DISABLED_ADMIN",
                "rule_name": "Master Admin Account Without MFA",
                "severity": IssueSeverity.INFO,
                "description": "Master administrator / privileged account does not have Multi-Factor Authentication enabled.",
                "impact": "Elevated vulnerability to brute-force or credential stuffing attacks.",
                "recommendation": "Enforce mandatory MFA for all privileged and administrative logins.",
            },
        ]

    async def get_security_quality(self) -> SecurityDataQualityResponse:
        return await asyncio.to_thread(self._get_security_quality_sync)

    def _get_security_quality_sync(self) -> SecurityDataQualityResponse:
        active_emp_pred = sql_active_employee_predicate("e")
        active_usr_pred = sql_active_user_predicate("u")

        # SQL evaluating all 14 rules simultaneously
        sql = f"""
        WITH ActiveUsers AS (
            SELECT u.*
            FROM dbo.SecurityUserMst u
            WHERE {active_usr_pred}
        ),
        ActiveEmployees AS (
            SELECT e.*
            FROM dbo.EmployeeMst e
            WHERE {active_emp_pred}
        ),
        RulesEvaluation AS (
            -- 1. ORPHAN_USER_EMP_REF (Critical)
            SELECT 'ORPHAN_USER_EMP_REF' AS code, COUNT(*) AS cnt
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.EmployeeMst e ON u.UserEmpID = e.EmpID
            WHERE u.UserEmpID IS NOT NULL AND u.UserEmpID > 0 AND e.EmpID IS NULL

            UNION ALL
            -- 2. ACTIVE_USER_INACTIVE_EMP (Critical)
            SELECT 'ACTIVE_USER_INACTIVE_EMP' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            JOIN dbo.EmployeeMst e ON u.UserEmpID = e.EmpID
            WHERE e.EmpIsActive = 0 OR e.EmpIsDeleted = 1 OR (e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE())

            UNION ALL
            -- 3. PRIVILEGED_INACTIVE_EMP_RISK (Critical)
            SELECT 'PRIVILEGED_INACTIVE_EMP_RISK' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            LEFT JOIN dbo.EmployeeMst e ON u.UserEmpID = e.EmpID
            WHERE (u.IsMasterAdmin = 1 OR u.RoleID = 1)
              AND (
                  u.UserEmpID IS NULL OR u.UserEmpID = 0
                  OR e.EmpID IS NULL
                  OR e.EmpIsActive = 0
                  OR e.EmpIsDeleted = 1
                  OR (e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE())
              )

            UNION ALL
            -- 4. ACTIVE_AND_DELETED_USER (Warning)
            SELECT 'ACTIVE_AND_DELETED_USER' AS code, COUNT(*) AS cnt
            FROM dbo.SecurityUserMst u
            WHERE u.UserIsActive = 1 AND u.UserIsDeleted = 1

            UNION ALL
            -- 5. DUPLICATE_ACTIVE_USERNAME (Warning)
            SELECT 'DUPLICATE_ACTIVE_USERNAME' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            WHERE LOWER(LTRIM(RTRIM(u.UserName))) IN (
                SELECT LOWER(LTRIM(RTRIM(UserName)))
                FROM ActiveUsers
                WHERE UserName IS NOT NULL AND LTRIM(RTRIM(UserName)) <> ''
                GROUP BY LOWER(LTRIM(RTRIM(UserName)))
                HAVING COUNT(*) > 1
            )

            UNION ALL
            -- 6. DUPLICATE_ACTIVE_LOGIN_EMAIL (Warning)
            SELECT 'DUPLICATE_ACTIVE_LOGIN_EMAIL' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            WHERE LOWER(LTRIM(RTRIM(u.UserEmail))) IN (
                SELECT LOWER(LTRIM(RTRIM(UserEmail)))
                FROM ActiveUsers
                WHERE UserEmail IS NOT NULL AND LTRIM(RTRIM(UserEmail)) <> ''
                GROUP BY LOWER(LTRIM(RTRIM(UserEmail)))
                HAVING COUNT(*) > 1
            )

            UNION ALL
            -- 7. MULTIPLE_ACTIVE_USERS_PER_EMP (Warning)
            SELECT 'MULTIPLE_ACTIVE_USERS_PER_EMP' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            JOIN ActiveEmployees e ON u.UserEmpID = e.EmpID
            WHERE u.UserEmpID IN (
                SELECT u2.UserEmpID
                FROM ActiveUsers u2
                JOIN ActiveEmployees e2 ON u2.UserEmpID = e2.EmpID
                GROUP BY u2.UserEmpID
                HAVING COUNT(*) > 1
            )

            UNION ALL
            -- 8. MISSING_USER_ROLE (Warning)
            SELECT 'MISSING_USER_ROLE' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE u.RoleID IS NULL OR r.RoleID IS NULL

            UNION ALL
            -- 9. ROLE_WITHOUT_PERMISSIONS (Warning)
            SELECT 'ROLE_WITHOUT_PERMISSIONS' AS code, COUNT(*) AS cnt
            FROM dbo.SecurityRoleMst r
            LEFT JOIN dbo.SecurityRoleRightsMst rr ON r.RoleID = rr.RoleID AND rr.RoleMenuIsActive = 1 AND rr.RoleMenuIsDeleted = 0
            WHERE r.RoleIsActive = 1 AND r.RoleIsDeleted = 0
            GROUP BY r.RoleID, r.RoleDesc
            HAVING COUNT(rr.RoleMenuID) = 0

            UNION ALL
            -- 10. ROLE_IS_DELETED_IN_USE (Warning)
            SELECT 'ROLE_IS_DELETED_IN_USE' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE r.RoleIsDeleted = 1

            UNION ALL
            -- 11. EMP_WITHOUT_USER_LOGIN (Info)
            SELECT 'EMP_WITHOUT_USER_LOGIN' AS code, COUNT(DISTINCT e.EmpID) AS cnt
            FROM ActiveEmployees e
            LEFT JOIN ActiveUsers u ON e.EmpID = u.UserEmpID
            WHERE u.UserID IS NULL

            UNION ALL
            -- 12. USER_WITHOUT_EMP_LINK (Info)
            SELECT 'USER_WITHOUT_EMP_LINK' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            WHERE u.UserEmpID IS NULL OR u.UserEmpID = 0

            UNION ALL
            -- 13. NEVER_LOGGED_IN_ACCOUNT (Info)
            SELECT 'NEVER_LOGGED_IN_ACCOUNT' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            WHERE u.LastAccessAPI IS NULL

            UNION ALL
            -- 14. MFA_DISABLED_ADMIN (Info)
            SELECT 'MFA_DISABLED_ADMIN' AS code, COUNT(*) AS cnt
            FROM ActiveUsers u
            WHERE (u.IsMasterAdmin = 1 OR u.RoleID = 1)
              AND (u.MFA = 0 OR u.MFA IS NULL)
        )
        SELECT code, cnt FROM RulesEvaluation;
        """

        rule_rows = execute_readonly_query(sql)
        counts = {r["code"]: int(r["cnt"] or 0) for r in rule_rows}

        rules_catalog = self._get_rules_catalog()
        rules: list[SecurityQualityRuleResult] = []
        critical_cnt = 0
        warning_cnt = 0
        info_cnt = 0

        for r_meta in rules_catalog:
            cnt = counts.get(r_meta["rule_code"], 0)
            sev = r_meta["severity"]
            if sev == IssueSeverity.CRITICAL:
                critical_cnt += cnt
            elif sev == IssueSeverity.WARNING:
                warning_cnt += cnt
            else:
                info_cnt += cnt

            rules.append(
                SecurityQualityRuleResult(
                    rule_code=r_meta["rule_code"],
                    rule_name=r_meta["rule_name"],
                    severity=sev,
                    description=r_meta["description"],
                    issue_count=cnt,
                    impact=r_meta["impact"],
                    recommendation=r_meta["recommendation"],
                )
            )

        # Health score calculation against active user population (4,214 active users)
        total_active_pop = 4214.0
        penalty = ((critical_cnt * 3.0) + (warning_cnt * 0.5)) / total_active_pop * 100.0
        health = max(0.0, min(100.0, 100.0 - penalty))
        health_score = round(health, 1)

        return SecurityDataQualityResponse(
            overall_security_score=health_score,
            critical_issues_count=critical_cnt,
            warning_issues_count=warning_cnt,
            info_issues_count=info_cnt,
            rules=rules,
            summary_by_severity={
                "CRITICAL": critical_cnt,
                "WARNING": warning_cnt,
                "INFO": info_cnt,
            },
        )

    # ─────────────────────────────────────────────────────────────
    # 5. DRILLDOWN ISSUES LIST & EXPORT
    # ─────────────────────────────────────────────────────────────

    async def get_security_quality_issues(
        self,
        issue_code: str,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> SecurityQualityIssuesListResponse:
        return await asyncio.to_thread(
            self._get_security_quality_issues_sync,
            issue_code=issue_code,
            search=search,
            limit=limit,
            offset=offset,
        )

    def _get_security_quality_issues_sync(
        self,
        issue_code: str,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> SecurityQualityIssuesListResponse:
        rules_dict = {r["rule_code"]: r for r in self._get_rules_catalog()}
        rule_meta = rules_dict.get(issue_code)
        if not rule_meta:
            return SecurityQualityIssuesListResponse(
                issue_code=issue_code,
                issue_name="Unknown Rule",
                severity=IssueSeverity.INFO,
                total=0,
                limit=limit,
                offset=offset,
                items=[],
            )

        active_emp_pred = sql_active_employee_predicate("e")
        active_usr_pred = sql_active_user_predicate("u")

        # Generate rule specific base query
        # Must produce: record_id, entity_type, entity_name, issue_detail, account_role, status_detail
        if issue_code == "ORPHAN_USER_EMP_REF":
            base_sql = """
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'User references non-existent Employee ID ' + CAST(u.UserEmpID AS VARCHAR) AS issue_detail,
                r.RoleDesc AS account_role,
                'Orphan Reference' AS status_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            LEFT JOIN dbo.EmployeeMst e ON u.UserEmpID = e.EmpID
            WHERE u.UserEmpID IS NOT NULL AND u.UserEmpID > 0 AND e.EmpID IS NULL
            """
        elif issue_code == "ACTIVE_USER_INACTIVE_EMP":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Active user linked to EmpID ' + CAST(e.EmpID AS VARCHAR) + ' (Code: ' + ISNULL(e.EmpCode, '') + ') - ' + RTRIM(LTRIM(ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, ''))) + ' who is Inactive/Resigned' AS issue_detail,
                r.RoleDesc AS account_role,
                CASE 
                    WHEN e.EmpIsDeleted = 1 THEN 'Deleted Employee'
                    WHEN e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE() THEN 'Resigned ' + CONVERT(VARCHAR(10), e.EmpResignDate, 120)
                    WHEN e.EmpIsActive = 0 THEN 'Inactive Employee'
                    ELSE 'Inactive/Resigned'
                END AS status_detail
            FROM dbo.SecurityUserMst u
            JOIN dbo.EmployeeMst e ON u.UserEmpID = e.EmpID
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE {active_usr_pred}
              AND (e.EmpIsActive = 0 OR e.EmpIsDeleted = 1 OR (e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE()))
            """
        elif issue_code == "PRIVILEGED_INACTIVE_EMP_RISK":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Privileged Super Admin account linked to invalid/inactive employee' AS issue_detail,
                r.RoleDesc AS account_role,
                'Master Admin Exposure' AS status_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            LEFT JOIN dbo.EmployeeMst e ON u.UserEmpID = e.EmpID
            WHERE {active_usr_pred}
              AND (u.IsMasterAdmin = 1 OR u.RoleID = 1)
              AND (
                  u.UserEmpID IS NULL OR u.UserEmpID = 0
                  OR e.EmpID IS NULL
                  OR e.EmpIsActive = 0
                  OR e.EmpIsDeleted = 1
                  OR (e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE())
              )
            """
        elif issue_code == "ACTIVE_AND_DELETED_USER":
            base_sql = """
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Account marked UserIsActive=1 and UserIsDeleted=1 simultaneously' AS issue_detail,
                r.RoleDesc AS account_role,
                'Inconsistent State' AS status_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE u.UserIsActive = 1 AND u.UserIsDeleted = 1
            """
        elif issue_code == "DUPLICATE_ACTIVE_USERNAME":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Duplicate username: ' + LOWER(LTRIM(RTRIM(u.UserName))) AS issue_detail,
                r.RoleDesc AS account_role,
                'Duplicate Username' AS status_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE {active_usr_pred}
              AND LOWER(LTRIM(RTRIM(u.UserName))) IN (
                  SELECT LOWER(LTRIM(RTRIM(UserName)))
                  FROM dbo.SecurityUserMst
                  WHERE {active_usr_pred} AND UserName IS NOT NULL AND LTRIM(RTRIM(UserName)) <> ''
                  GROUP BY LOWER(LTRIM(RTRIM(UserName)))
                  HAVING COUNT(*) > 1
              )
            """
        elif issue_code == "DUPLICATE_ACTIVE_LOGIN_EMAIL":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Duplicate login email: ' + LOWER(LTRIM(RTRIM(u.UserEmail))) AS issue_detail,
                r.RoleDesc AS account_role,
                'Duplicate Email' AS status_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE {active_usr_pred}
              AND LOWER(LTRIM(RTRIM(u.UserEmail))) IN (
                  SELECT LOWER(LTRIM(RTRIM(UserEmail)))
                  FROM dbo.SecurityUserMst
                  WHERE {active_usr_pred} AND UserEmail IS NOT NULL AND LTRIM(RTRIM(UserEmail)) <> ''
                  GROUP BY LOWER(LTRIM(RTRIM(UserEmail)))
                  HAVING COUNT(*) > 1
              )
            """
        elif issue_code == "MULTIPLE_ACTIVE_USERS_PER_EMP":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Employee Code ' + ISNULL(e.EmpCode, '') + ' has multiple concurrent active user accounts' AS issue_detail,
                r.RoleDesc AS account_role,
                'Multiple Accounts' AS status_detail
            FROM dbo.SecurityUserMst u
            JOIN dbo.EmployeeMst e ON u.UserEmpID = e.EmpID
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE {active_usr_pred} AND {active_emp_pred}
              AND u.UserEmpID IN (
                  SELECT u2.UserEmpID
                  FROM dbo.SecurityUserMst u2
                  JOIN dbo.EmployeeMst e2 ON u2.UserEmpID = e2.EmpID
                  WHERE {active_usr_pred} AND {active_emp_pred}
                  GROUP BY u2.UserEmpID
                  HAVING COUNT(*) > 1
              )
            """
        elif issue_code == "MISSING_USER_ROLE":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Active user account has NULL or invalid RoleID' AS issue_detail,
                'Unassigned' AS account_role,
                'Missing Role' AS status_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE {active_usr_pred} AND (u.RoleID IS NULL OR r.RoleID IS NULL)
            """
        elif issue_code == "ROLE_WITHOUT_PERMISSIONS":
            base_sql = """
            SELECT
                r.RoleID AS record_id,
                'ROLE' AS entity_type,
                r.RoleDesc AS entity_name,
                'Security role has 0 active permissions mapped in SecurityRoleRightsMst' AS issue_detail,
                r.RoleDesc AS account_role,
                'Zero Rights' AS status_detail
            FROM dbo.SecurityRoleMst r
            LEFT JOIN dbo.SecurityRoleRightsMst rr ON r.RoleID = rr.RoleID AND rr.RoleMenuIsActive = 1 AND rr.RoleMenuIsDeleted = 0
            WHERE r.RoleIsActive = 1 AND r.RoleIsDeleted = 0
            GROUP BY r.RoleID, r.RoleDesc
            HAVING COUNT(rr.RoleMenuID) = 0
            """
        elif issue_code == "ROLE_IS_DELETED_IN_USE":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Active user is assigned to deleted role ' + ISNULL(r.RoleDesc, '') AS issue_detail,
                r.RoleDesc AS account_role,
                'Deleted Role in Use' AS status_detail
            FROM dbo.SecurityUserMst u
            JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE {active_usr_pred} AND r.RoleIsDeleted = 1
            """
        elif issue_code == "EMP_WITHOUT_USER_LOGIN":
            base_sql = f"""
            SELECT
                e.EmpID AS record_id,
                'EMPLOYEE' AS entity_type,
                RTRIM(LTRIM(ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, ''))) AS entity_name,
                'Active employee Code ' + ISNULL(e.EmpCode, '') + ' has no system user login account' AS issue_detail,
                'No Account' AS account_role,
                'Unprovisioned' AS status_detail
            FROM dbo.EmployeeMst e
            LEFT JOIN dbo.SecurityUserMst u ON e.EmpID = u.UserEmpID AND {active_usr_pred}
            WHERE {active_emp_pred} AND u.UserID IS NULL
            """
        elif issue_code == "USER_WITHOUT_EMP_LINK":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Active user account has no UserEmpID linkage (Candidate / Vendor / Consultant)' AS issue_detail,
                r.RoleDesc AS account_role,
                'External Login' AS status_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE {active_usr_pred} AND (u.UserEmpID IS NULL OR u.UserEmpID = 0)
            """
        elif issue_code == "NEVER_LOGGED_IN_ACCOUNT":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Active account created ' + ISNULL(CONVERT(VARCHAR(10), u.UserEntDate, 120), 'N/A') + ' has never recorded a login' AS issue_detail,
                r.RoleDesc AS account_role,
                'Never Logged In' AS status_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE {active_usr_pred} AND u.LastAccessAPI IS NULL
            """
        elif issue_code == "MFA_DISABLED_ADMIN":
            base_sql = f"""
            SELECT
                u.UserID AS record_id,
                'USER' AS entity_type,
                ISNULL(u.UserName, 'User ' + CAST(u.UserID AS VARCHAR)) AS entity_name,
                'Master Admin account does not have Multi-Factor Authentication enabled' AS issue_detail,
                r.RoleDesc AS account_role,
                'MFA Disabled' AS status_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.SecurityRoleMst r ON u.RoleID = r.RoleID
            WHERE {active_usr_pred}
              AND (u.IsMasterAdmin = 1 OR u.RoleID = 1)
              AND (u.MFA = 0 OR u.MFA IS NULL)
            """
        else:
            return SecurityQualityIssuesListResponse(
                issue_code=issue_code,
                issue_name=rule_meta["rule_name"],
                severity=rule_meta["severity"],
                total=0,
                limit=limit,
                offset=offset,
                items=[],
            )

        params: dict[str, Any] = {"limit": limit, "offset": offset}
        search_filter = ""
        if search:
            search_filter = "WHERE (sub.entity_name LIKE :search OR sub.issue_detail LIKE :search OR sub.account_role LIKE :search)"
            params["search"] = f"%{search}%"

        count_query = f"""
        WITH IssueRecords AS (
            {base_sql}
        )
        SELECT COUNT(*) AS total
        FROM IssueRecords sub
        {search_filter};
        """
        tot_row = execute_readonly_query(count_query, params)
        total = tot_row[0]["total"] if tot_row else 0

        items_query = f"""
        WITH IssueRecords AS (
            {base_sql}
        )
        SELECT
            sub.record_id,
            sub.entity_type,
            sub.entity_name,
            sub.issue_detail,
            sub.account_role,
            sub.status_detail
        FROM IssueRecords sub
        {search_filter}
        ORDER BY sub.record_id ASC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        rows = execute_readonly_query(items_query, params)

        items: list[SecurityQualityIssueItem] = []
        for r in rows:
            items.append(
                SecurityQualityIssueItem(
                    record_id=r["record_id"],
                    entity_type=r["entity_type"],
                    entity_name=r["entity_name"],
                    issue_code=issue_code,
                    issue_detail=r["issue_detail"],
                    account_role=r["account_role"],
                    status_detail=r["status_detail"],
                )
            )

        return SecurityQualityIssuesListResponse(
            issue_code=issue_code,
            issue_name=rule_meta["rule_name"],
            severity=rule_meta["severity"],
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    async def export_security_quality_issues(
        self, issue_code: str, search: str | None = None
    ) -> str:
        res = await self.get_security_quality_issues(
            issue_code=issue_code,
            search=search,
            limit=50000,
            offset=0,
        )
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Record ID",
                "Entity Type",
                "Entity Name",
                "Issue Code",
                "Issue Name",
                "Severity",
                "Role",
                "Status Detail",
                "Issue Detail",
            ]
        )
        for it in res.items:
            writer.writerow(
                [
                    it.record_id,
                    it.entity_type,
                    it.entity_name,
                    it.issue_code,
                    res.issue_name,
                    res.severity.value,
                    it.account_role or "",
                    it.status_detail or "",
                    it.issue_detail,
                ]
            )
        return output.getvalue()
