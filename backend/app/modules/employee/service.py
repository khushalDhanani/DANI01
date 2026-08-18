import csv
import io
import logging
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.employee.schemas import (
    DistributionItem,
    EmployeeDataQualityResponse,
    EmployeeDetailResponse,
    EmployeeListItem,
    EmployeeListResponse,
    EmployeeOverviewResponse,
    EmployeeStatusCount,
    EmployeeStructureResponse,
    ExperienceItem,
    FamilyMemberItem,
    IssueSeverity,
    OfficialHistoryItem,
    QualificationItem,
    QualityIssueRecord,
    QualityIssuesListResponse,
    QualityRuleResult,
    RelationshipEdge,
    TableNodeMetadata,
)

logger = logging.getLogger(__name__)


class EmployeeService:
    """
    Centralized business logic and data-access service for the Employee & Workforce module.
    Enforces canonical active employee rules, position resolution, manager hierarchies,
    and single-source-of-truth data quality evaluations.
    """

    async def get_employee_overview(self, comp_id: int | None = None) -> EmployeeOverviewResponse:
        """
        Calculates and returns complete overview counts and demographic breakdowns.
        """
        params: dict[str, Any] = {}
        comp_clause = ""
        comp_where = ""
        if comp_id:
            params["comp_id"] = comp_id
            comp_clause = " AND CompID = :comp_id"
            comp_where = " AND e.CompID = :comp_id"

        # Status counts query
        status_sql = f"""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN EmpIsActive = 1 AND EmpIsDeleted = 0 AND (EmpResignDate IS NULL OR EmpResignDate > GETDATE()) THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN EmpIsActive = 0 AND EmpIsDeleted = 0 AND (EmpResignDate IS NULL OR EmpResignDate > GETDATE()) THEN 1 ELSE 0 END) AS inactive,
            SUM(CASE WHEN EmpResignDate IS NOT NULL AND EmpResignDate <= GETDATE() THEN 1 ELSE 0 END) AS resigned,
            SUM(CASE WHEN EmpIsDeleted = 1 THEN 1 ELSE 0 END) AS deleted
        FROM dbo.EmployeeMst
        WHERE 1=1 {comp_clause};
        """
        status_row = execute_readonly_query(status_sql, params)[0]

        status_counts = EmployeeStatusCount(
            total=status_row["total"] or 0,
            active=status_row["active"] or 0,
            inactive=status_row["inactive"] or 0,
            resigned=status_row["resigned"] or 0,
            deleted=status_row["deleted"] or 0,
        )

        # Gender breakdown (Active employees)
        gender_sql = """
        SELECT
            ISNULL(NULLIF(EmpGender, ''), 'Unspecified') AS label,
            COUNT(*) AS count
        FROM dbo.EmployeeMst
        WHERE EmpIsActive = 1 AND EmpIsDeleted = 0 AND (EmpResignDate IS NULL OR EmpResignDate > GETDATE())
        GROUP BY EmpGender
        ORDER BY count DESC;
        """
        gender_rows = execute_readonly_query(gender_sql)
        active_total = status_counts.active or 1
        gender_dist = [
            DistributionItem(
                label="Male"
                if r["label"] == "M"
                else ("Female" if r["label"] == "F" else r["label"]),
                count=r["count"],
                percentage=round((r["count"] / active_total) * 100, 1),
            )
            for r in gender_rows
        ]

        # Employment type breakdown
        type_sql = """
        SELECT
            ISNULL(t.EmpTypeDesc, 'Unassigned') AS label,
            COUNT(*) AS count
        FROM dbo.EmployeeMst e
        LEFT JOIN dbo.EmployeeTypeMst t ON e.EmpTypeID = t.EmpTypeID
        WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
        GROUP BY t.EmpTypeDesc
        ORDER BY count DESC;
        """
        type_rows = execute_readonly_query(type_sql)
        type_dist = [
            DistributionItem(
                label=r["label"],
                count=r["count"],
                percentage=round((r["count"] / active_total) * 100, 1),
            )
            for r in type_rows
        ]

        # Department breakdown (via active EmployeeOfficialDet)
        dept_sql = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID,
                o.DeptID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
        )
        SELECT
            ISNULL(d.DeptName, 'Unassigned') AS label,
            COUNT(*) AS count
        FROM dbo.EmployeeMst e
        LEFT JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID AND d.DeptIsActive = 1
        WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
        GROUP BY d.DeptName
        ORDER BY count DESC;
        """
        dept_rows = execute_readonly_query(dept_sql)
        dept_dist = [
            DistributionItem(
                label=r["label"],
                count=r["count"],
                percentage=round((r["count"] / active_total) * 100, 1),
            )
            for r in dept_rows[:10]
        ]

        # Company breakdown
        comp_sql = """
        SELECT
            ISNULL(c.CompName, 'Aether Industries Limited') AS label,
            COUNT(*) AS count
        FROM dbo.EmployeeMst e
        LEFT JOIN dbo.OrgCompanyMst c ON e.CompID = c.CompID AND c.CompIsActive = 1
        WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
        GROUP BY c.CompName
        ORDER BY count DESC;
        """
        comp_rows = execute_readonly_query(comp_sql)
        comp_dist = [
            DistributionItem(
                label=r["label"],
                count=r["count"],
                percentage=round((r["count"] / active_total) * 100, 1),
            )
            for r in comp_rows
        ]

        # Top Locations
        loc_sql = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID,
                o.LocID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
        )
        SELECT
            ISNULL(l.LocName, 'Unassigned') AS label,
            COUNT(*) AS count
        FROM dbo.EmployeeMst e
        LEFT JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID AND l.LocIsActive = 1
        WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
        GROUP BY l.LocName
        ORDER BY count DESC;
        """
        loc_rows = execute_readonly_query(loc_sql)
        loc_dist = [
            DistributionItem(
                label=r["label"],
                count=r["count"],
                percentage=round((r["count"] / active_total) * 100, 1),
            )
            for r in loc_rows[:6]
        ]

        # User coverage
        user_cov_sql = """
        SELECT
            COUNT(DISTINCT u.UserEmpID) AS users_linked,
            COUNT(*) AS total_active_users
        FROM dbo.SecurityUserMst u
        WHERE u.UserIsActive = 1 AND u.UserIsDeleted = 0;
        """
        user_cov_row = execute_readonly_query(user_cov_sql)[0]

        # Reporting coverage
        rep_cov_sql = """
        SELECT
            COUNT(DISTINCT r.EmpID) AS emps_with_active_mgr
        FROM dbo.EmployeeReportingDet r
        JOIN dbo.EmployeeMst e ON r.EmpID = e.EmpID
        WHERE r.ReportingDetIsActive = 1 AND r.ReportingDetIsDeleted = 0
          AND e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE());
        """
        rep_cov_row = execute_readonly_query(rep_cov_sql)[0]

        return EmployeeOverviewResponse(
            status_counts=status_counts,
            gender_distribution=gender_dist,
            employment_type_distribution=type_dist,
            department_distribution=dept_dist,
            company_distribution=comp_dist,
            top_locations=loc_dist,
            user_account_coverage={
                "active_employees_with_login": user_cov_row["users_linked"] or 0,
                "login_coverage_pct": round(
                    ((user_cov_row["users_linked"] or 0) / active_total) * 100, 1
                ),
                "total_active_logins": user_cov_row["total_active_users"] or 0,
            },
            reporting_coverage={
                "active_employees_with_manager": rep_cov_row["emps_with_active_mgr"] or 0,
                "manager_coverage_pct": round(
                    ((rep_cov_row["emps_with_active_mgr"] or 0) / active_total) * 100, 1
                ),
            },
        )

    async def get_employee_structure(self) -> EmployeeStructureResponse:
        """
        Returns the data structure and relationship graph with confidence ratings.
        """
        # Fetch live row counts for relevant tables
        row_counts_sql = """
        SELECT
            t.name AS table_name,
            p.rows AS row_count
        FROM sys.tables t
        LEFT JOIN (
            SELECT object_id, SUM(rows) AS rows
            FROM sys.partitions
            WHERE index_id IN (0, 1)
            GROUP BY object_id
        ) p ON t.object_id = p.object_id
        WHERE t.name IN (
            'EmployeeMst', 'EmployeeOfficialDet', 'EmployeeReportingDet', 'SecurityUserMst',
            'OrgCompanyMst', 'OrgDepartmentMst', 'OrgDesignationMst', 'OrgLocationMst',
            'EmployeeGradeMst', 'EmployeeTypeMst', 'EmployeeFamilyDet', 'EmployeeQualificationDet',
            'EmployeeExperienceDet', 'EmployeeAttendance', 'PayLogEarnedSalary', 'PayMonthlyLeaveBalance',
            'EmployeeResignDet', 'EmployeePhotoDet', 'EmployeeMedicalDet'
        );
        """
        rc_rows = {
            r["table_name"]: (r["row_count"] or 0) for r in execute_readonly_query(row_counts_sql)
        }

        tables = [
            TableNodeMetadata(
                schema="dbo",
                table="EmployeeMst",
                role="ROOT_MASTER",
                row_count=rc_rows.get("EmployeeMst", 3091),
                key_column="EmpID",
                confidence="CONFIRMED",
                description="Core master entity containing identity, contact, demographics, and active flags.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="EmployeeOfficialDet",
                role="POSITION_HISTORY",
                row_count=rc_rows.get("EmployeeOfficialDet", 4658),
                key_column="EmpOfficeDetID",
                confidence="CONFIRMED",
                description="SCD Type-2 official position history linking to Department, Designation, Location, and Grade.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="EmployeeReportingDet",
                role="HIERARCHY",
                row_count=rc_rows.get("EmployeeReportingDet", 10456),
                key_column="EmpReportingDetID",
                confidence="CONFIRMED",
                description="Reporting matrix linking employees to Functional and Administrative managers.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="SecurityUserMst",
                role="AUTHENTICATION",
                row_count=rc_rows.get("SecurityUserMst", 5420),
                key_column="UserID",
                confidence="CONFIRMED",
                description="Portal/ERP login accounts linked via UserEmpID.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="OrgDepartmentMst",
                role="LOOKUP",
                row_count=rc_rows.get("OrgDepartmentMst", 52),
                key_column="DeptID",
                confidence="CONFIRMED",
                description="Organizational departments and SAP cost centers.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="OrgDesignationMst",
                role="LOOKUP",
                row_count=rc_rows.get("OrgDesignationMst", 389),
                key_column="DesigID",
                confidence="CONFIRMED",
                description="Job designations, seniorities, and executive tags.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="OrgLocationMst",
                role="LOOKUP",
                row_count=rc_rows.get("OrgLocationMst", 22),
                key_column="LocID",
                confidence="CONFIRMED",
                description="Physical plant sites, office locations, and IP gateways.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="EmployeeAttendance",
                role="TIME_TRACKING",
                row_count=rc_rows.get("EmployeeAttendance", 829723),
                key_column="AttID",
                confidence="CONFIRMED",
                description="Daily biometric in/out swipes and present hour logs.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="PayLogEarnedSalary",
                role="PAYROLL",
                row_count=rc_rows.get("PayLogEarnedSalary", 3208209),
                key_column="EarnedSalID",
                confidence="CONFIRMED",
                description="Monthly gross, deductions, and net salary calculations.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="PayMonthlyLeaveBalance",
                role="LEAVE",
                row_count=rc_rows.get("PayMonthlyLeaveBalance", 86006),
                key_column="LeaveBalID",
                confidence="CONFIRMED",
                description="Accrued, taken, and closing monthly leave balances.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="EmployeeFamilyDet",
                role="DETAIL",
                row_count=rc_rows.get("EmployeeFamilyDet", 7852),
                key_column="EmpFamilyDetID",
                confidence="CONFIRMED",
                description="Family members, dependents, and emergency contact flags.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="EmployeeQualificationDet",
                role="DETAIL",
                row_count=rc_rows.get("EmployeeQualificationDet", 5155),
                key_column="EmpQualDetID",
                confidence="CONFIRMED",
                description="Degrees, universities, and academic history.",
            ),
            TableNodeMetadata(
                schema="dbo",
                table="EmployeeExperienceDet",
                role="DETAIL",
                row_count=rc_rows.get("EmployeeExperienceDet", 3140),
                key_column="EmpExpDetID",
                confidence="CONFIRMED",
                description="Prior work experience history and previous CTC.",
            ),
        ]

        relationships = [
            RelationshipEdge(
                source_table="dbo.EmployeeMst",
                target_table="dbo.EmployeeOfficialDet",
                source_key="EmpID",
                target_key="EmpID",
                relationship_type="ONE_TO_MANY",
                confidence="CONFIRMED",
                description="Maintains current and historical position postings.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeOfficialDet",
                target_table="dbo.OrgDepartmentMst",
                source_key="DeptID",
                target_key="DeptID",
                relationship_type="MANY_TO_ONE",
                confidence="CONFIRMED",
                description="Links employee position to organizational department.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeOfficialDet",
                target_table="dbo.OrgDesignationMst",
                source_key="DesigID",
                target_key="DesigID",
                relationship_type="MANY_TO_ONE",
                confidence="CONFIRMED",
                description="Links employee position to official job designation.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeOfficialDet",
                target_table="dbo.OrgLocationMst",
                source_key="LocID",
                target_key="LocID",
                relationship_type="MANY_TO_ONE",
                confidence="CONFIRMED",
                description="Links employee position to physical manufacturing site / plant.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeMst",
                target_table="dbo.EmployeeReportingDet",
                source_key="EmpID",
                target_key="EmpID",
                relationship_type="ONE_TO_MANY",
                confidence="CONFIRMED",
                description="Defines reporting hierarchy for team leadership and approvals.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeReportingDet",
                target_table="dbo.EmployeeMst",
                source_key="ReportingEmpID",
                target_key="EmpID",
                relationship_type="MANY_TO_ONE",
                confidence="CONFIRMED",
                description="Points to manager's EmployeeMst record.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeMst",
                target_table="dbo.SecurityUserMst",
                source_key="EmpID",
                target_key="UserEmpID",
                relationship_type="ONE_TO_ONE",
                confidence="CONFIRMED",
                description="Binds physical employee to web/mobile authentication login.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeMst",
                target_table="dbo.EmployeeAttendance",
                source_key="EmpID",
                target_key="AttEmpID",
                relationship_type="ONE_TO_MANY",
                confidence="CONFIRMED",
                description="Daily biometric attendance punch events.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeMst",
                target_table="dbo.PayLogEarnedSalary",
                source_key="EmpID",
                target_key="EarnedSalEmpID",
                relationship_type="ONE_TO_MANY",
                confidence="CONFIRMED",
                description="Monthly payroll compensation disbursement records.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeMst",
                target_table="dbo.PayMonthlyLeaveBalance",
                source_key="EmpID",
                target_key="EmpID",
                relationship_type="ONE_TO_MANY",
                confidence="CONFIRMED",
                description="Monthly leave balance ledger.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeMst",
                target_table="dbo.EmployeeFamilyDet",
                source_key="EmpID",
                target_key="EmpID",
                relationship_type="ONE_TO_MANY",
                confidence="CONFIRMED",
                description="Family members and emergency contacts.",
            ),
            RelationshipEdge(
                source_table="dbo.EmployeeMst",
                target_table="dbo.DLPersonMst",
                source_key="EmpID",
                target_key="PROwnerEmpID",
                relationship_type="ONE_TO_MANY",
                confidence="LIKELY",
                description="Internal PR Owner tracking for CRM contacts (Entities remain separate).",
            ),
        ]

        return EmployeeStructureResponse(
            master_table="dbo.EmployeeMst",
            canonical_key="EmpID",
            business_key="EmpCode",
            tables=tables,
            relationships=relationships,
            confidence_summary={"CONFIRMED": 11, "LIKELY": 1},
        )

    async def get_employee_quality(self) -> EmployeeDataQualityResponse:
        """
        Runs comprehensive data quality checks on Employee data, classified by severity.
        """
        dq_sql = """
        SELECT
            'DUP_EMP_CODE' AS code,
            COUNT(*) AS cnt
        FROM (
            SELECT EmpCode FROM dbo.EmployeeMst WHERE EmpIsActive = 1 AND ISNULL(EmpIsDeleted, 0) = 0 AND EmpCode IS NOT NULL AND EmpCode <> '' GROUP BY EmpCode HAVING COUNT(*) > 1
        ) sub

        UNION ALL
        SELECT
            'ACTIVE_PAST_RESIGN',
            COUNT(*)
        FROM dbo.EmployeeMst
        WHERE EmpIsActive = 1 AND EmpIsDeleted = 0 AND EmpResignDate IS NOT NULL AND EmpResignDate <= GETDATE()
        UNION ALL
        SELECT
            'MISSING_OFFICIAL_RECORD',
            COUNT(*)
        FROM dbo.EmployeeMst e
        LEFT JOIN dbo.EmployeeOfficialDet o ON e.EmpID = o.EmpID AND o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
        WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND o.EmpID IS NULL
        UNION ALL
        SELECT
            'MISSING_EMAIL',
            COUNT(*)
        FROM dbo.EmployeeMst
        WHERE EmpIsActive = 1 AND EmpIsDeleted = 0 AND (EmpResignDate IS NULL OR EmpResignDate > GETDATE())
          AND (EmpEmailIDCompany IS NULL OR EmpEmailIDCompany = '')
        UNION ALL
        SELECT
            'MISSING_DEPT',
            COUNT(*)
        FROM dbo.EmployeeMst e
        LEFT JOIN (
            SELECT EmpID, DeptID, ROW_NUMBER() OVER (PARTITION BY EmpID ORDER BY ApplicableFrDate DESC, EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet WHERE EmpOfficeDetIsActive = 1 AND EmpOfficeDetIsDeleted = 0
        ) co ON e.EmpID = co.EmpID AND co.rn = 1
        WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
          AND co.DeptID IS NULL
        UNION ALL
        SELECT
            'MISSING_DESIG',
            COUNT(*)
        FROM dbo.EmployeeMst e
        LEFT JOIN (
            SELECT EmpID, DesigID, ROW_NUMBER() OVER (PARTITION BY EmpID ORDER BY ApplicableFrDate DESC, EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet WHERE EmpOfficeDetIsActive = 1 AND EmpOfficeDetIsDeleted = 0
        ) co ON e.EmpID = co.EmpID AND co.rn = 1
        WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
          AND co.DesigID IS NULL
        UNION ALL
        SELECT
            'MISSING_MANAGER',
            COUNT(*)
        FROM dbo.EmployeeMst e
        LEFT JOIN dbo.EmployeeReportingDet r ON e.EmpID = r.EmpID AND r.ReportingDetIsActive = 1 AND r.ReportingDetIsDeleted = 0
        WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
          AND r.EmpID IS NULL
        UNION ALL
        SELECT
            'DUP_PAN',
            COUNT(*)
        FROM (
            SELECT EmpPANNo FROM dbo.EmployeeMst WHERE EmpPANNo IS NOT NULL AND EmpPANNo <> '' GROUP BY EmpPANNo HAVING COUNT(*) > 1
        ) sub
        UNION ALL
        SELECT
            'DUP_AADHAAR',
            COUNT(*)
        FROM (
            SELECT AadharCardNo FROM dbo.EmployeeMst WHERE AadharCardNo IS NOT NULL AND AadharCardNo <> '' GROUP BY AadharCardNo HAVING COUNT(*) > 1
        ) sub
        UNION ALL
        SELECT
            'DUP_PHONE',
            COUNT(*)
        FROM (
            SELECT EmpPhone1 FROM dbo.EmployeeMst WHERE EmpPhone1 IS NOT NULL AND EmpPhone1 <> '' GROUP BY EmpPhone1 HAVING COUNT(*) > 1
        ) sub
        UNION ALL
        SELECT
            'INACTIVE_NO_RESIGN_DATE',
            COUNT(*)
        FROM dbo.EmployeeMst
        WHERE EmpIsActive = 0 AND EmpIsDeleted = 0 AND EmpResignDate IS NULL
        UNION ALL
        SELECT
            'ORPHAN_REFERENCES',
            COUNT(*)
        FROM dbo.FriskingTransDet t
        LEFT JOIN dbo.EmployeeMst e ON t.EmpId = e.EmpID
        WHERE t.EmpId IS NOT NULL AND e.EmpID IS NULL;
        """
        counts = {r["code"]: r["cnt"] for r in execute_readonly_query(dq_sql)}

        rules = [
            # CRITICAL
            QualityRuleResult(
                rule_code="DUP_EMP_CODE",
                rule_name="Duplicate Employee Code",
                severity=IssueSeverity.CRITICAL,
                description="Multiple employee records share the same natural Employee Code (EmpCode).",
                issue_count=counts.get("DUP_EMP_CODE", 0),
                impact="High risk of payroll collision, badge punch misattribution, and profile overwriting.",
                recommendation="Enforce unique constraint on EmpCode and archive inactive duplicates with suffix.",
            ),
            QualityRuleResult(
                rule_code="ACTIVE_PAST_RESIGN",
                rule_name="Active Status with Past Resignation Date",
                severity=IssueSeverity.CRITICAL,
                description="Employee record has EmpIsActive=1 and EmpIsDeleted=0 despite having a resignation date in the past.",
                issue_count=counts.get("ACTIVE_PAST_RESIGN", 0),
                impact="Unauthorized active system access and potential payroll generation for ex-employees.",
                recommendation="Deactivate EmpIsActive flag and lock security user accounts.",
            ),
            QualityRuleResult(
                rule_code="MISSING_OFFICIAL_RECORD",
                rule_name="Active Employee Missing Official Record",
                severity=IssueSeverity.CRITICAL,
                description="Active employee has zero active position assignments in EmployeeOfficialDet.",
                issue_count=counts.get("MISSING_OFFICIAL_RECORD", 0),
                impact="Employee is unassigned to any department, designation, or site location.",
                recommendation="Create current official posting in EmployeeOfficialDet.",
            ),
            # WARNING
            QualityRuleResult(
                rule_code="MISSING_EMAIL",
                rule_name="Missing Company Email",
                severity=IssueSeverity.WARNING,
                description="Active employee lacks official corporate email address.",
                issue_count=counts.get("MISSING_EMAIL", 0),
                impact="Unable to receive system notifications, payslips, or security alerts.",
                recommendation="Populate corporate email from Active Directory / Office 365.",
            ),
            QualityRuleResult(
                rule_code="MISSING_DEPT",
                rule_name="Missing Department Assignment",
                severity=IssueSeverity.WARNING,
                description="Active employee has no department linked in official details.",
                issue_count=counts.get("MISSING_DEPT", 0),
                impact="Cost-center allocation and organizational hierarchy gaps.",
                recommendation="Assign official department in EmployeeOfficialDet.",
            ),
            QualityRuleResult(
                rule_code="MISSING_DESIG",
                rule_name="Missing Designation Assignment",
                severity=IssueSeverity.WARNING,
                description="Active employee has no job designation assigned.",
                issue_count=counts.get("MISSING_DESIG", 0),
                impact="Unclear role responsibilities and approval permission routing.",
                recommendation="Assign official designation in EmployeeOfficialDet.",
            ),
            QualityRuleResult(
                rule_code="MISSING_MANAGER",
                rule_name="Missing Reporting Manager",
                severity=IssueSeverity.WARNING,
                description="Active employee has no active reporting line configured.",
                issue_count=counts.get("MISSING_MANAGER", 0),
                impact="Leave, overtime, and appraisal workflows cannot find an approval manager.",
                recommendation="Configure reporting line in EmployeeReportingDet.",
            ),
            QualityRuleResult(
                rule_code="DUP_PAN",
                rule_name="Duplicate Income Tax PAN",
                severity=IssueSeverity.WARNING,
                description="Multiple employee records share identical PAN tax numbers.",
                issue_count=counts.get("DUP_PAN", 0),
                impact="TDS Form 16 tax filing discrepancies.",
                recommendation="Verify official PAN cards and resolve duplicate accounts.",
            ),
            QualityRuleResult(
                rule_code="DUP_AADHAAR",
                rule_name="Duplicate Aadhaar Number",
                severity=IssueSeverity.WARNING,
                description="Multiple employee records share identical national identity Aadhaar numbers.",
                issue_count=counts.get("DUP_AADHAAR", 0),
                impact="Statutory compliance audit failure and duplicate identity risk.",
                recommendation="Audit Aadhaar verification records and merge duplicate profiles.",
            ),
            QualityRuleResult(
                rule_code="DUP_PHONE",
                rule_name="Duplicate Primary Mobile",
                severity=IssueSeverity.WARNING,
                description="Multiple employee records share identical primary contact numbers.",
                issue_count=counts.get("DUP_PHONE", 0),
                impact="SMS alerts and OTP authentication collisions.",
                recommendation="Validate primary contact number with employee.",
            ),
            # INFO
            QualityRuleResult(
                rule_code="INACTIVE_NO_RESIGN_DATE",
                rule_name="Inactive Without Resignation Date",
                severity=IssueSeverity.INFO,
                description="Employee marked inactive (EmpIsActive=0) but lacks documented resignation date.",
                issue_count=counts.get("INACTIVE_NO_RESIGN_DATE", 0),
                impact="Incomplete separation lifecycle documentation.",
                recommendation="Record separation/termination date for historical completeness.",
            ),
            QualityRuleResult(
                rule_code="ORPHAN_REFERENCES",
                rule_name="Orphan Employee Keys in Transaction Tables",
                severity=IssueSeverity.INFO,
                description="Legacy physical security transaction logs point to non-existent EmpIDs.",
                issue_count=counts.get("ORPHAN_REFERENCES", 0),
                impact="Historic audit queries return NULL employee metadata.",
                recommendation="Retain transaction logs with fallback display as unknown former employee.",
            ),
        ]

        crit_count = sum(r.issue_count for r in rules if r.severity == IssueSeverity.CRITICAL)
        warn_count = sum(r.issue_count for r in rules if r.severity == IssueSeverity.WARNING)
        info_count = sum(r.issue_count for r in rules if r.severity == IssueSeverity.INFO)

        # Health score calculation (100 base, deductions for critical/warning)
        penalty = min((crit_count * 5.0) + (warn_count * 0.1), 40.0)
        health_score = round(max(100.0 - penalty, 60.0), 1)

        return EmployeeDataQualityResponse(
            overall_health_score=health_score,
            critical_issues_count=crit_count,
            warning_issues_count=warn_count,
            info_issues_count=info_count,
            rules=rules,
            summary_by_severity={
                "CRITICAL": crit_count,
                "WARNING": warn_count,
                "INFO": info_count,
            },
        )

    async def get_quality_issues_drilldown(
        self,
        issue_code: str,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> QualityIssuesListResponse:
        """
        Retrieves paginated records flagged with a specific quality issue code.
        """
        issue_code = issue_code.upper()

        # Build specific SQL per rule
        if issue_code == "DUP_EMP_CODE":
            base_sql = """
            FROM dbo.EmployeeMst e
            LEFT JOIN dbo.OrgCompanyMst c ON e.CompID = c.CompID
            WHERE e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND e.EmpCode IN (
                SELECT EmpCode FROM dbo.EmployeeMst WHERE EmpIsActive = 1 AND ISNULL(EmpIsDeleted, 0) = 0 AND EmpCode IS NOT NULL AND EmpCode <> '' GROUP BY EmpCode HAVING COUNT(*) > 1
            )
            """

            detail_expr = "'Duplicate EmpCode: ' + ISNULL(e.EmpCode, '')"
            severity = IssueSeverity.CRITICAL
            name = "Duplicate Employee Code"

        elif issue_code == "ACTIVE_PAST_RESIGN":
            base_sql = """
            FROM dbo.EmployeeMst e
            LEFT JOIN dbo.OrgCompanyMst c ON e.CompID = c.CompID
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE()
            """
            detail_expr = "'Active with Resign Date: ' + CONVERT(VARCHAR(10), e.EmpResignDate, 120)"
            severity = IssueSeverity.CRITICAL
            name = "Active Status with Past Resignation Date"

        elif issue_code == "MISSING_OFFICIAL_RECORD":
            base_sql = """
            FROM dbo.EmployeeMst e
            LEFT JOIN dbo.EmployeeOfficialDet o ON e.EmpID = o.EmpID AND o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND o.EmpID IS NULL
            """
            detail_expr = "'No active record in EmployeeOfficialDet'"
            severity = IssueSeverity.CRITICAL
            name = "Active Employee Missing Official Record"

        elif issue_code == "MISSING_EMAIL":
            base_sql = """
            FROM dbo.EmployeeMst e
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND (e.EmpEmailIDCompany IS NULL OR e.EmpEmailIDCompany = '')
            """
            detail_expr = "'Missing corporate email'"
            severity = IssueSeverity.WARNING
            name = "Missing Company Email"

        elif issue_code == "MISSING_DEPT":
            base_sql = """
            FROM dbo.EmployeeMst e
            LEFT JOIN (
                SELECT EmpID, DeptID, ROW_NUMBER() OVER (PARTITION BY EmpID ORDER BY ApplicableFrDate DESC, EmpOfficeDetID DESC) AS rn
                FROM dbo.EmployeeOfficialDet WHERE EmpOfficeDetIsActive = 1 AND EmpOfficeDetIsDeleted = 0
            ) co ON e.EmpID = co.EmpID AND co.rn = 1
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND co.DeptID IS NULL
            """
            detail_expr = "'No department assigned in official details'"
            severity = IssueSeverity.WARNING
            name = "Missing Department Assignment"

        elif issue_code == "MISSING_DESIG":
            base_sql = """
            FROM dbo.EmployeeMst e
            LEFT JOIN (
                SELECT EmpID, DesigID, ROW_NUMBER() OVER (PARTITION BY EmpID ORDER BY ApplicableFrDate DESC, EmpOfficeDetID DESC) AS rn
                FROM dbo.EmployeeOfficialDet WHERE EmpOfficeDetIsActive = 1 AND EmpOfficeDetIsDeleted = 0
            ) co ON e.EmpID = co.EmpID AND co.rn = 1
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND co.DesigID IS NULL
            """
            detail_expr = "'No designation assigned in official details'"
            severity = IssueSeverity.WARNING
            name = "Missing Designation Assignment"

        elif issue_code == "MISSING_MANAGER":
            base_sql = """
            FROM dbo.EmployeeMst e
            LEFT JOIN dbo.EmployeeReportingDet r ON e.EmpID = r.EmpID AND r.ReportingDetIsActive = 1 AND r.ReportingDetIsDeleted = 0
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND r.EmpID IS NULL
            """
            detail_expr = "'No active reporting line in EmployeeReportingDet'"
            severity = IssueSeverity.WARNING
            name = "Missing Reporting Manager"

        elif issue_code == "DUP_PAN":
            base_sql = """
            FROM dbo.EmployeeMst e
            WHERE e.EmpPANNo IN (
                SELECT EmpPANNo FROM dbo.EmployeeMst WHERE EmpPANNo IS NOT NULL AND EmpPANNo <> '' GROUP BY EmpPANNo HAVING COUNT(*) > 1
            )
            """
            detail_expr = "'Duplicate PAN: ' + ISNULL(e.EmpPANNo, '')"
            severity = IssueSeverity.WARNING
            name = "Duplicate Income Tax PAN"

        elif issue_code == "DUP_AADHAAR":
            base_sql = """
            FROM dbo.EmployeeMst e
            WHERE e.AadharCardNo IN (
                SELECT AadharCardNo FROM dbo.EmployeeMst WHERE AadharCardNo IS NOT NULL AND AadharCardNo <> '' GROUP BY AadharCardNo HAVING COUNT(*) > 1
            )
            """
            detail_expr = "'Duplicate Aadhaar: ' + ISNULL(e.AadharCardNo, '')"
            severity = IssueSeverity.WARNING
            name = "Duplicate Aadhaar Number"

        elif issue_code == "DUP_PHONE":
            base_sql = """
            FROM dbo.EmployeeMst e
            WHERE e.EmpPhone1 IN (
                SELECT EmpPhone1 FROM dbo.EmployeeMst WHERE EmpPhone1 IS NOT NULL AND EmpPhone1 <> '' GROUP BY EmpPhone1 HAVING COUNT(*) > 1
            )
            """
            detail_expr = "'Duplicate Mobile: ' + ISNULL(e.EmpPhone1, '')"
            severity = IssueSeverity.WARNING
            name = "Duplicate Primary Mobile"

        else:  # Default / INACTIVE_NO_RESIGN_DATE
            base_sql = """
            FROM dbo.EmployeeMst e
            WHERE e.EmpIsActive = 0 AND e.EmpIsDeleted = 0 AND e.EmpResignDate IS NULL
            """
            detail_expr = "'Inactive without documented resign date'"
            severity = IssueSeverity.INFO
            name = "Inactive Without Resignation Date"

        # Search filter
        search_filter = ""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if search and search.strip():
            search_filter = " AND (e.EmpFirstName LIKE :search OR e.EmpLastName LIKE :search OR e.EmpCode LIKE :search OR e.EmpEmailIDCompany LIKE :search)"
            params["search"] = f"%{search.strip()}%"

        count_sql = f"SELECT COUNT(*) AS total {base_sql} {search_filter}"
        total_res = execute_readonly_query(count_sql, params)
        total_count = total_res[0]["total"] if total_res else 0

        items_sql = f"""
        SELECT
            e.EmpID,
            e.EmpCode,
            e.EmpFirstName + ' ' + ISNULL(e.EmpLastName, '') AS full_name,
            e.EmpEmailIDCompany AS company_email,
            e.EmpPhone1 AS phone,
            e.EmpIsActive AS emp_is_active,
            e.EmpResignDate AS emp_resign_date,
            '{issue_code}' AS issue_code,
            {detail_expr} AS issue_detail
        {base_sql} {search_filter}
        ORDER BY e.EmpID DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        rows = execute_readonly_query(items_sql, params)

        items = [
            QualityIssueRecord(
                emp_id=r["EmpID"],
                emp_code=r["EmpCode"],
                full_name=r["full_name"],
                company_email=r["company_email"],
                phone=r["phone"],
                emp_is_active=r["emp_is_active"],
                emp_resign_date=r["emp_resign_date"],
                issue_code=r["issue_code"],
                issue_detail=r["issue_detail"],
            )
            for r in rows
        ]

        return QualityIssuesListResponse(
            issue_code=issue_code,
            issue_name=name,
            severity=severity,
            total=total_count,
            limit=limit,
            offset=offset,
            items=items,
        )

    async def get_employee_records(
        self,
        search: str | None = None,
        status_filter: str = "ACTIVE",
        dept_id: int | None = None,
        desig_id: int | None = None,
        loc_id: int | None = None,
        comp_id: int | None = None,
        limit: int = 25,
        offset: int = 0,
        sort_by: str = "EmpID",
        sort_order: str = "asc",
    ) -> EmployeeListResponse:
        """
        Retrieves paginated employees using canonical safe query pattern with zero duplicates.
        """
        # Status predicate
        status_upper = status_filter.upper()
        if status_upper == "ACTIVE":
            status_clause = "WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())"
        elif status_upper == "INACTIVE":
            status_clause = "WHERE e.EmpIsActive = 0 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())"
        elif status_upper == "RESIGNED":
            status_clause = "WHERE e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE()"
        elif status_upper == "DELETED":
            status_clause = "WHERE e.EmpIsDeleted = 1"
        else:  # ALL
            status_clause = "WHERE 1=1"

        params: dict[str, Any] = {"limit": limit, "offset": offset}

        extra_filters = []
        if search and search.strip():
            extra_filters.append(
                "(e.EmpFirstName LIKE :search OR e.EmpLastName LIKE :search OR e.EmpCode LIKE :search OR e.EmpEmailIDCompany LIKE :search)"
            )
            params["search"] = f"%{search.strip()}%"
        if comp_id:
            extra_filters.append("e.CompID = :comp_id")
            params["comp_id"] = comp_id
        if dept_id:
            extra_filters.append("co.DeptID = :dept_id")
            params["dept_id"] = dept_id

        if desig_id:
            extra_filters.append("co.DesigID = :desig_id")
            params["desig_id"] = desig_id
        if loc_id:
            extra_filters.append("co.LocID = :loc_id")
            params["loc_id"] = loc_id

        and_clause = (" AND " + " AND ".join(extra_filters)) if extra_filters else ""

        # Validate sorting column
        valid_sorts = {
            "empid": "e.EmpID",
            "empcode": "e.EmpCode",
            "empfirstname": "e.EmpFirstName",
            "emplastname": "e.EmpLastName",
            "empjoindate": "e.EmpJoinDate",
            "deptname": "d.DeptName",
            "designame": "des.DesigName",
        }
        order_col = valid_sorts.get(sort_by.lower(), "e.EmpID")
        order_dir = "DESC" if sort_order.lower() == "desc" else "ASC"

        base_cte = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID,
                o.LocID,
                o.DeptID,
                o.DesigID,
                o.EmpGradeID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
        ),
        FunctionalManager AS (
            SELECT
                r.EmpID,
                r.ReportingEmpID AS FunctionalMgrEmpID,
                ROW_NUMBER() OVER (PARTITION BY r.EmpID ORDER BY r.EmpReportingDetID DESC) AS rn
            FROM dbo.EmployeeReportingDet r
            LEFT JOIN dbo.OrgDesignationReportingDet odr
                ON r.DesigID = odr.DesigID AND r.ReportingDesigID = odr.ReportingDesigID AND odr.ReportingIsActive = 1 AND odr.ReportingIsDeleted = 0
            WHERE r.ReportingDetIsActive = 1 AND r.ReportingDetIsDeleted = 0
              AND (odr.ReportingType = 'F' OR odr.ReportingType IS NULL)
        ),
        AdminManager AS (
            SELECT
                r.EmpID,
                r.ReportingEmpID AS AdminMgrEmpID,
                ROW_NUMBER() OVER (PARTITION BY r.EmpID ORDER BY r.EmpReportingDetID DESC) AS rn
            FROM dbo.EmployeeReportingDet r
            JOIN dbo.OrgDesignationReportingDet odr
                ON r.DesigID = odr.DesigID AND r.ReportingDesigID = odr.ReportingDesigID AND odr.ReportingIsActive = 1 AND odr.ReportingIsDeleted = 0
            WHERE r.ReportingDetIsActive = 1 AND r.ReportingDetIsDeleted = 0 AND odr.ReportingType = 'A'
        )
        """

        count_sql = f"""
        {base_cte}
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE()) THEN 1 ELSE 0 END) AS active_cnt,
            SUM(CASE WHEN e.EmpIsActive = 0 OR e.EmpIsDeleted = 1 OR (e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE()) THEN 1 ELSE 0 END) AS inactive_cnt
        FROM dbo.EmployeeMst e
        LEFT JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID
        LEFT JOIN dbo.OrgDesignationMst des ON co.DesigID = des.DesigID
        {status_clause} {and_clause};
        """
        count_res = execute_readonly_query(count_sql, params)
        total = count_res[0]["total"] if count_res else 0
        active_cnt = count_res[0]["active_cnt"] if count_res else 0
        inactive_cnt = count_res[0]["inactive_cnt"] if count_res else 0

        items_sql = f"""
        {base_cte}
        SELECT
            e.EmpID,
            e.EmpCode,
            e.EmpFirstName,
            e.EmpMiddleName,
            e.EmpLastName,
            e.EmpFirstName + ' ' + ISNULL(e.EmpMiddleName + ' ', '') + ISNULL(e.EmpLastName, '') AS full_name,
            e.EmpGender,
            e.EmpBirthDate,
            e.EmpEmailIDCompany,
            e.EmpEmailIDPersonal,
            e.EmpPhone1,
            e.EmpPANNo,
            e.AadharCardNo,
            e.EmpJoinDate,
            e.EmpResignDate,
            e.EmpIsActive,
            e.EmpIsDeleted,
            t.EmpTypeDesc AS employment_type,
            c.CompName AS company_name,
            d.DeptName AS department_name,
            des.DesigName AS designation_name,
            loc.LocName AS location_name,
            g.EmpGradeDesc AS grade_desc,
            fm.FunctionalMgrEmpID,
            fm_emp.EmpFirstName + ' ' + ISNULL(fm_emp.EmpLastName,'') AS functional_mgr_name,
            am.AdminMgrEmpID,
            am_emp.EmpFirstName + ' ' + ISNULL(am_emp.EmpLastName,'') AS admin_mgr_name,
            u.UserID,
            u.UserName,
            u.UserIsActive,
            sr.RoleDesc AS role_desc
        FROM dbo.EmployeeMst e
        LEFT JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgCompanyMst c ON e.CompID = c.CompID
        LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID
        LEFT JOIN dbo.OrgDesignationMst des ON co.DesigID = des.DesigID
        LEFT JOIN dbo.OrgLocationMst loc ON co.LocID = loc.LocID
        LEFT JOIN dbo.EmployeeGradeMst g ON co.EmpGradeID = g.EmpGradeID
        LEFT JOIN dbo.EmployeeTypeMst t ON e.EmpTypeID = t.EmpTypeID
        LEFT JOIN FunctionalManager fm ON e.EmpID = fm.EmpID AND fm.rn = 1
        LEFT JOIN dbo.EmployeeMst fm_emp ON fm.FunctionalMgrEmpID = fm_emp.EmpID
        LEFT JOIN AdminManager am ON e.EmpID = am.EmpID AND am.rn = 1
        LEFT JOIN dbo.EmployeeMst am_emp ON am.AdminMgrEmpID = am_emp.EmpID
        LEFT JOIN dbo.SecurityUserMst u ON e.EmpID = u.UserEmpID AND u.UserIsDeleted = 0
        LEFT JOIN dbo.SecurityRoleMst sr ON u.RoleID = sr.RoleID
        {status_clause} {and_clause}
        ORDER BY {order_col} {order_dir}
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        rows = execute_readonly_query(items_sql, params)

        items = [
            EmployeeListItem(
                emp_id=r["EmpID"],
                emp_code=r["EmpCode"],
                full_name=r["full_name"],
                first_name=r["EmpFirstName"],
                middle_name=r["EmpMiddleName"],
                last_name=r["EmpLastName"],
                gender=r["EmpGender"],
                birth_date=r["EmpBirthDate"],
                company_email=r["EmpEmailIDCompany"],
                personal_email=r["EmpEmailIDPersonal"],
                phone=r["EmpPhone1"],
                pan_no=r["EmpPANNo"],
                aadhar_no=r["AadharCardNo"],
                joining_date=r["EmpJoinDate"],
                resign_date=r["EmpResignDate"],
                is_active=bool(r["EmpIsActive"]),
                is_deleted=bool(r["EmpIsDeleted"]),
                employment_type=r["employment_type"],
                company_name=r["company_name"],
                department_name=r["department_name"],
                designation_name=r["designation_name"],
                location_name=r["location_name"],
                grade_desc=r["grade_desc"],
                functional_mgr_id=r["FunctionalMgrEmpID"],
                functional_mgr_name=r["functional_mgr_name"],
                admin_mgr_id=r["AdminMgrEmpID"],
                admin_mgr_name=r["admin_mgr_name"],
                user_id=r["UserID"],
                user_name=r["UserName"],
                user_is_active=r["UserIsActive"],
                role_desc=r["role_desc"],
            )
            for r in rows
        ]

        return EmployeeListResponse(
            total=total,
            active_count=active_cnt,
            inactive_count=inactive_cnt,
            limit=limit,
            offset=offset,
            items=items,
        )

    async def get_employee_detail(self, emp_id: int) -> EmployeeDetailResponse | None:
        """
        Retrieves a complete 360° employee dossier with all child records.
        """
        master_sql = """
        SELECT
            e.EmpID, e.EmpCode, e.EmpTitle, e.EmpFirstName, e.EmpMiddleName, e.EmpLastName,
            e.EmpFirstName + ' ' + ISNULL(e.EmpMiddleName + ' ', '') + ISNULL(e.EmpLastName, '') AS full_name,
            e.EmpGender, e.EmpBirthDate, e.EmpBloodGroupID, e.EmpEmailIDCompany, e.EmpEmailIDPersonal,
            e.EmpPhone1, e.EmpPhone2, e.EmpDirectNumber, e.EmpExtentionNumber, e.EmpCUGNumber,
            e.EmpCorrAdd1, e.EmpCorrAdd2, e.EmpCorrAdd3, e.EmpCorrPincode,
            e.EmpPermAdd1, e.EmpPermAdd2, e.EmpPermAdd3, e.EmpPermPincode,
            e.EmpPANNo, e.AadharCardNo, e.EmpUANNo, e.EmpPFNo, e.EmpESICNo, e.VoterID,
            e.EmpDrivingLicenseNo, e.PRANNo, e.SapGLCode, e.MicrosoftObjectID,
            e.EmpJoinDate, e.EmpResignDate, e.EmpIsActive, e.EmpIsDeleted,
            t.EmpTypeDesc AS employment_type,
            c.CompName AS company_name,
            m.Status AS marital_status,
            rel.ReligionsName AS religion,
            cast.CastCategoryName AS caste_category,
            cntry.CountryName AS nationality
        FROM dbo.EmployeeMst e
        LEFT JOIN dbo.OrgCompanyMst c ON e.CompID = c.CompID
        LEFT JOIN dbo.EmployeeTypeMst t ON e.EmpTypeID = t.EmpTypeID
        LEFT JOIN dbo.MaritualStatus m ON e.MaritualStatusID = m.MaritualStatusID
        LEFT JOIN dbo.ReligionsMst rel ON e.ReligionsID = rel.ReligionsID
        LEFT JOIN dbo.EmpCastCategoryMst cast ON e.CastCategoryID = cast.CastCategoryID
        LEFT JOIN dbo.CountryMst cntry ON e.EmpNationalityID = cntry.CountryID
        WHERE e.EmpID = :emp_id;
        """
        rows = execute_readonly_query(master_sql, {"emp_id": emp_id})
        if not rows:
            return None
        m = rows[0]

        # Current Official & History
        history_sql = """
        SELECT
            o.EmpOfficeDetID,
            d.DeptName,
            des.DesigName,
            loc.LocName,
            g.EmpGradeDesc,
            o.ApplicableFrDate,
            o.JoiningDate,
            o.ResignDate,
            o.EmpOfficeDetIsActive
        FROM dbo.EmployeeOfficialDet o
        LEFT JOIN dbo.OrgDepartmentMst d ON o.DeptID = d.DeptID
        LEFT JOIN dbo.OrgDesignationMst des ON o.DesigID = des.DesigID
        LEFT JOIN dbo.OrgLocationMst loc ON o.LocID = loc.LocID
        LEFT JOIN dbo.EmployeeGradeMst g ON o.EmpGradeID = g.EmpGradeID
        WHERE o.EmpID = :emp_id AND o.EmpOfficeDetIsDeleted = 0
        ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC;
        """
        history_rows = execute_readonly_query(history_sql, {"emp_id": emp_id})
        official_history = [
            OfficialHistoryItem(
                office_det_id=r["EmpOfficeDetID"],
                dept_name=r["DeptName"],
                desig_name=r["DesigName"],
                loc_name=r["LocName"],
                grade_desc=r["EmpGradeDesc"],
                applicable_from=r["ApplicableFrDate"],
                joining_date=r["JoiningDate"],
                resign_date=r["ResignDate"],
                is_active=bool(r["EmpOfficeDetIsActive"]),
            )
            for r in history_rows
        ]

        current_off = official_history[0] if official_history else None

        # Managers
        mgr_sql = """
        SELECT
            r.ReportingEmpID,
            m.EmpCode AS mgr_code,
            m.EmpFirstName + ' ' + ISNULL(m.EmpLastName,'') AS mgr_name,
            odr.ReportingType
        FROM dbo.EmployeeReportingDet r
        JOIN dbo.EmployeeMst m ON r.ReportingEmpID = m.EmpID
        LEFT JOIN dbo.OrgDesignationReportingDet odr
            ON r.DesigID = odr.DesigID AND r.ReportingDesigID = odr.ReportingDesigID AND odr.ReportingIsActive = 1 AND odr.ReportingIsDeleted = 0
        WHERE r.EmpID = :emp_id AND r.ReportingDetIsActive = 1 AND r.ReportingDetIsDeleted = 0;
        """
        mgr_rows = execute_readonly_query(mgr_sql, {"emp_id": emp_id})
        f_mgr = next(
            (
                r
                for r in mgr_rows
                if r.get("ReportingType") == "F" or r.get("ReportingType") is None
            ),
            None,
        )
        a_mgr = next((r for r in mgr_rows if r.get("ReportingType") == "A"), None)

        # User Account
        user_sql = """
        SELECT u.UserID, u.UserName, u.UserEmail, u.UserADID, u.UserIsActive, sr.RoleDesc
        FROM dbo.SecurityUserMst u
        LEFT JOIN dbo.SecurityRoleMst sr ON u.RoleID = sr.RoleID
        WHERE u.UserEmpID = :emp_id AND u.UserIsDeleted = 0;
        """
        user_rows = execute_readonly_query(user_sql, {"emp_id": emp_id})
        user_acc = user_rows[0] if user_rows else None

        # Family
        family_sql = """
        SELECT EmpFamilyDetID, EmpFamilyMemberName, RelationID, EmpFamilyMemberDOB, EmpFamilyMemberPhone, EmpFamilyIsEmergencyContact
        FROM dbo.EmployeeFamilyDet
        WHERE EmpID = :emp_id;
        """
        fam_rows = execute_readonly_query(family_sql, {"emp_id": emp_id})
        family_items = [
            FamilyMemberItem(
                family_det_id=r["EmpFamilyDetID"],
                name=r["EmpFamilyMemberName"],
                birth_date=r["EmpFamilyMemberDOB"],
                phone=r["EmpFamilyMemberPhone"],
                is_emergency_contact=bool(r.get("EmpFamilyIsEmergencyContact", False)),
            )
            for r in fam_rows
        ]

        # Qualifications
        qual_sql = """
        SELECT EmpQualDetID, DegreeID, PassingYear, GradePercentage, InstituteName
        FROM dbo.EmployeeQualificationDet
        WHERE EmpID = :emp_id;
        """
        qual_rows = execute_readonly_query(qual_sql, {"emp_id": emp_id})
        qual_items = [
            QualificationItem(
                qual_det_id=r["EmpQualDetID"],
                passing_year=r["PassingYear"],
                percentage_grade=str(r["GradePercentage"]) if r.get("GradePercentage") else None,
                institute_name=r["InstituteName"],
            )
            for r in qual_rows
        ]

        # Experience
        exp_sql = """
        SELECT EmpExpDetID, CompanyName, Designation, FromDate, ToDate, LastDrawnCTC
        FROM dbo.EmployeeExperienceDet
        WHERE EmpID = :emp_id;
        """
        exp_rows = execute_readonly_query(exp_sql, {"emp_id": emp_id})
        exp_items = [
            ExperienceItem(
                exp_det_id=r["EmpExpDetID"],
                company_name=r["CompanyName"],
                designation=r["Designation"],
                from_date=r["FromDate"],
                to_date=r["ToDate"],
                last_drawn_ctc=str(r["LastDrawnCTC"]) if r.get("LastDrawnCTC") else None,
            )
            for r in exp_rows
        ]

        corr_addr = ", ".join(
            filter(None, [m.get("EmpCorrAdd1"), m.get("EmpCorrAdd2"), m.get("EmpCorrAdd3")])
        )
        perm_addr = ", ".join(
            filter(None, [m.get("EmpPermAdd1"), m.get("EmpPermAdd2"), m.get("EmpPermAdd3")])
        )

        return EmployeeDetailResponse(
            emp_id=m["EmpID"],
            emp_code=m["EmpCode"],
            title=m["EmpTitle"],
            first_name=m["EmpFirstName"],
            middle_name=m["EmpMiddleName"],
            last_name=m["EmpLastName"],
            full_name=m["full_name"],
            gender=m["EmpGender"],
            birth_date=m["EmpBirthDate"],
            blood_group=str(m["EmpBloodGroupID"]) if m.get("EmpBloodGroupID") else None,
            marital_status=m["marital_status"],
            religion=m["religion"],
            caste_category=m["caste_category"],
            nationality=m["nationality"],
            company_email=m["EmpEmailIDCompany"],
            personal_email=m["EmpEmailIDPersonal"],
            phone1=m["EmpPhone1"],
            phone2=m["EmpPhone2"],
            direct_number=m["EmpDirectNumber"],
            ext_number=m["EmpExtentionNumber"],
            cug_number=m["EmpCUGNumber"],
            correspondence_address=corr_addr,
            corr_pincode=m["EmpCorrPincode"],
            permanent_address=perm_addr,
            perm_pincode=m["EmpPermPincode"],
            pan_no=m["EmpPANNo"],
            aadhar_no=m["AadharCardNo"],
            uan_no=m["EmpUANNo"],
            pf_no=m["EmpPFNo"],
            esic_no=m["EmpESICNo"],
            voter_id=m["VoterID"],
            driving_license_no=m["EmpDrivingLicenseNo"],
            pran_no=m["PRANNo"],
            sap_gl_code=m["SapGLCode"],
            microsoft_object_id=m["MicrosoftObjectID"],
            joining_date=m["EmpJoinDate"],
            resign_date=m["EmpResignDate"],
            is_active=bool(m["EmpIsActive"]),
            is_deleted=bool(m["EmpIsDeleted"]),
            employment_type=m["employment_type"],
            company_name=m["company_name"],
            current_dept=current_off.dept_name if current_off else None,
            current_desig=current_off.desig_name if current_off else None,
            current_location=current_off.loc_name if current_off else None,
            current_grade=current_off.grade_desc if current_off else None,
            functional_mgr_id=f_mgr["ReportingEmpID"] if f_mgr else None,
            functional_mgr_code=f_mgr["mgr_code"] if f_mgr else None,
            functional_mgr_name=f_mgr["mgr_name"] if f_mgr else None,
            admin_mgr_id=a_mgr["ReportingEmpID"] if a_mgr else None,
            admin_mgr_code=a_mgr["mgr_code"] if a_mgr else None,
            admin_mgr_name=a_mgr["mgr_name"] if a_mgr else None,
            user_id=user_acc["UserID"] if user_acc else None,
            user_name=user_acc["UserName"] if user_acc else None,
            user_email=user_acc["UserEmail"] if user_acc else None,
            user_ad_id=user_acc["UserADID"] if user_acc else None,
            user_is_active=user_acc["UserIsActive"] if user_acc else None,
            role_desc=user_acc["RoleDesc"] if user_acc else None,
            official_history=official_history,
            family_members=family_items,
            qualifications=qual_items,
            experiences=exp_items,
        )

    async def export_employee_records(
        self,
        format: str = "csv",
        status_filter: str = "ACTIVE",
        search: str | None = None,
    ) -> tuple[bytes, str, str]:
        """
        Exports employee roster as CSV or Excel (.xlsx) using the canonical safe query.
        """
        list_res = await self.get_employee_records(
            search=search,
            status_filter=status_filter,
            limit=5000,
            offset=0,
        )

        filename = f"employees_{status_filter.lower()}_{format.lower()}"

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Employee ID",
                "Employee Code",
                "Full Name",
                "Gender",
                "Email",
                "Phone",
                "Company",
                "Department",
                "Designation",
                "Location",
                "Grade",
                "Employment Type",
                "Joining Date",
                "Resign Date",
                "Active",
                "Functional Manager",
                "Admin Manager",
                "User Account",
            ]
        )

        for item in list_res.items:
            writer.writerow(
                [
                    item.emp_id,
                    item.emp_code or "",
                    item.full_name,
                    item.gender or "",
                    item.company_email or "",
                    item.phone or "",
                    item.company_name or "",
                    item.department_name or "",
                    item.designation_name or "",
                    item.location_name or "",
                    item.grade_desc or "",
                    item.employment_type or "",
                    str(item.joining_date) if item.joining_date else "",
                    str(item.resign_date) if item.resign_date else "",
                    "YES" if item.is_active else "NO",
                    item.functional_mgr_name or "",
                    item.admin_mgr_name or "",
                    item.user_name or "",
                ]
            )

        csv_bytes = output.getvalue().encode("utf-8")
        return csv_bytes, "text/csv", f"{filename}.csv"

    async def export_quality_issues(
        self,
        issue_code: str,
        format: str = "csv",
        search: str | None = None,
    ) -> tuple[bytes, str, str]:
        """
        Exports quality issue records as CSV.
        """
        drilldown = await self.get_quality_issues_drilldown(
            issue_code=issue_code,
            search=search,
            limit=5000,
            offset=0,
        )

        filename = f"quality_issue_{issue_code.lower()}"
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Employee ID",
                "Employee Code",
                "Full Name",
                "Email",
                "Phone",
                "Active",
                "Resign Date",
                "Issue Code",
                "Issue Detail",
            ]
        )

        for item in drilldown.items:
            writer.writerow(
                [
                    item.emp_id or "",
                    item.emp_code or "",
                    item.full_name or "",
                    item.company_email or "",
                    item.phone or "",
                    "YES" if item.emp_is_active else "NO",
                    str(item.emp_resign_date) if item.emp_resign_date else "",
                    item.issue_code,
                    item.issue_detail,
                ]
            )

        csv_bytes = output.getvalue().encode("utf-8")
        return csv_bytes, "text/csv", f"{filename}.csv"
