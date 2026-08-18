from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.modules.employee.schemas import IssueSeverity


class SecurityAccountOverview(BaseModel):
    total_user_accounts: int = 0
    active_users: int = 0
    active_users_pct: float = 0.0
    inactive_users: int = 0
    inactive_users_pct: float = 0.0
    deleted_users: int = 0
    deleted_users_pct: float = 0.0
    linked_to_employee: int = 0
    linked_to_employee_pct: float = 0.0
    unlinked_users: int = 0
    unlinked_users_pct: float = 0.0


class SecurityEmpLinkOverview(BaseModel):
    total_active_employees: int = 0
    active_emps_with_active_user: int = 0
    active_emps_with_active_user_pct: float = 0.0
    active_emps_without_active_user: int = 0
    active_emps_without_active_user_pct: float = 0.0


class SecurityPostureOverview(BaseModel):
    master_admins_count: int = 0
    mfa_enabled_count: int = 0
    mfa_enabled_pct: float = 0.0
    mobile_app_users_count: int = 0
    sma_users_count: int = 0
    api_accessed_count: int = 0
    never_logged_in_count: int = 0
    total_registered_devices: int = 0


class SecurityRoleDistributionItem(BaseModel):
    role_id: int
    role_desc: str
    total_users: int = 0
    active_users: int = 0
    percentage: float = 0.0


class SecurityOverviewResponse(BaseModel):
    account_metrics: SecurityAccountOverview
    employee_link_metrics: SecurityEmpLinkOverview
    posture_metrics: SecurityPostureOverview
    role_distribution: list[SecurityRoleDistributionItem] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class SecurityUserItem(BaseModel):
    user_id: int
    username: str | None = None
    user_email: str | None = None
    user_mobile: str | None = None
    role_id: int | None = None
    role_desc: str | None = None
    emp_id: int | None = None
    emp_code: str | None = None
    emp_name: str | None = None
    emp_status: str | None = None
    is_active: bool = False
    is_deleted: bool = False
    is_master_admin: bool = False
    is_mfa_enabled: bool = False
    is_mobile_app_user: bool = False
    last_access_api: str | None = None
    created_at: str | None = None
    registered_devices_count: int = 0


class SecurityUserListResponse(BaseModel):
    total: int = 0
    limit: int = 25
    offset: int = 0
    items: list[SecurityUserItem] = Field(default_factory=list)


class SecurityRoleItem(BaseModel):
    role_id: int
    role_desc: str
    comp_id: int | None = None
    is_active: bool = True
    is_deleted: bool = False
    total_assigned_users: int = 0
    active_assigned_users: int = 0
    assigned_menus_count: int = 0
    insert_perms_count: int = 0
    update_perms_count: int = 0
    delete_perms_count: int = 0
    view_perms_count: int = 0


class SecurityRoleListResponse(BaseModel):
    total_roles: int = 0
    active_roles: int = 0
    items: list[SecurityRoleItem] = Field(default_factory=list)


class SecurityMenuPermissionItem(BaseModel):
    role_menu_id: int
    menu_id: int
    menu_name: str | None = None
    form_name: str | None = None
    route_portal: str | None = None
    can_insert: bool = False
    can_update: bool = False
    can_delete: bool = False
    can_view: bool = False
    is_active: bool = True


class SecurityRoleDetailResponse(BaseModel):
    role_id: int
    role_desc: str
    is_active: bool = True
    is_deleted: bool = False
    total_permissions: int = 0
    permissions: list[SecurityMenuPermissionItem] = Field(default_factory=list)


class SecurityQualityRuleResult(BaseModel):
    rule_code: str
    rule_name: str
    severity: IssueSeverity
    description: str
    issue_count: int = 0
    impact: str
    recommendation: str


class SecurityDataQualityResponse(BaseModel):
    overall_security_score: float = 100.0
    critical_issues_count: int = 0
    warning_issues_count: int = 0
    info_issues_count: int = 0
    rules: list[SecurityQualityRuleResult] = Field(default_factory=list)
    summary_by_severity: dict[str, int] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class SecurityQualityIssueItem(BaseModel):
    record_id: int
    entity_type: str = "USER"
    entity_name: str
    issue_code: str
    issue_detail: str
    account_role: str | None = None
    status_detail: str | None = None


class SecurityQualityIssuesListResponse(BaseModel):
    issue_code: str
    issue_name: str
    severity: IssueSeverity
    total: int = 0
    limit: int = 25
    offset: int = 0
    items: list[SecurityQualityIssueItem] = Field(default_factory=list)
