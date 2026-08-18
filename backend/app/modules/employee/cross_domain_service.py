import csv
import io
import logging
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.employee.cross_domain_schemas import (
    CrossDomainCategorySummary,
    CrossDomainIssueRecord,
    CrossDomainIssuesListResponse,
    CrossDomainModuleSummary,
    CrossDomainOverviewResponse,
    CrossDomainQualityRuleInfo,
)

logger = logging.getLogger(__name__)

RULE_DEFINITIONS = [
    {
        "code": "DUP_EMP_CODE",
        "name": "Duplicate Active Employee Code",
        "severity": "CRITICAL",
        "category": "MASTER",
        "module": "EmployeeMst",
        "description": "Multiple active employees sharing identical employee code.",
        "impact": "Causes cross-system identity ambiguity in attendance, payroll, and authentication.",
    },
    {
        "code": "ACTIVE_DELETED_CONFLICT",
        "name": "Active + Deleted Status Conflict",
        "severity": "CRITICAL",
        "category": "MASTER",
        "module": "EmployeeMst",
        "description": "Employee record flagged as both active (EmpIsActive=1) and soft-deleted (EmpIsDeleted=1).",
        "impact": "Conflicting status flags leading to unpredictable security access and calculations.",
    },
    {
        "code": "ACTIVE_PAST_RESIGNED",
        "name": "Active Employee with Past Resignation Date",
        "severity": "WARNING",
        "category": "MASTER",
        "module": "EmployeeMst",
        "description": "Active employee record with historical resignation date (EmpResignDate <= GETDATE()).",
        "impact": "Risk of unauthorized system access and stale active headcount calculations.",
    },
    {
        "code": "MISSING_OFFICIAL_RECORD",
        "name": "Missing Current Official Assignment Record",
        "severity": "CRITICAL",
        "category": "MASTER",
        "module": "EmployeeOfficialDet",
        "description": "Active employee with no active assignment record in EmployeeOfficialDet.",
        "impact": "Employee lacks official company, department, designation, and location linkages.",
    },
    {
        "code": "MISSING_ORG_ASSIGNMENT",
        "name": "Missing Company, Dept, Desig, or Location",
        "severity": "WARNING",
        "category": "ORG",
        "module": "OrgMasters",
        "description": "Active employee missing company, department, designation, or location linkage.",
        "impact": "Incomplete organizational taxonomy impairing reporting and security scoping.",
    },
    {
        "code": "MISSING_MANAGER",
        "name": "Missing Active Reporting Manager",
        "severity": "WARNING",
        "category": "HIERARCHY",
        "module": "EmployeeReportingDet",
        "description": "Active employee with no active reporting manager assigned.",
        "impact": "Unassigned reporting manager breaking approval workflows and organizational hierarchy.",
    },
    {
        "code": "INVALID_MANAGER_FK",
        "name": "Invalid Reporting Manager Reference",
        "severity": "CRITICAL",
        "category": "HIERARCHY",
        "module": "EmployeeReportingDet",
        "description": "Assigned reporting manager ID points to non-existent employee master row.",
        "impact": "Broken foreign key reference breaking hierarchy traversal.",
    },
    {
        "code": "SELF_REPORTING_EMPLOYEE",
        "name": "Self-Reporting Employee",
        "severity": "CRITICAL",
        "category": "HIERARCHY",
        "module": "EmployeeReportingDet",
        "description": "Employee assigned as their own reporting manager (EmpID = ReportingEmpID).",
        "impact": "Circular self-approval loop in reporting tree.",
    },
    {
        "code": "CIRCULAR_MANAGER_HIERARCHY",
        "name": "Circular Manager Loop",
        "severity": "CRITICAL",
        "category": "HIERARCHY",
        "module": "EmployeeReportingDet",
        "description": "Direct 2-level circular reporting loop (Manager A reports to Manager B and Vice Versa).",
        "impact": "Infinite recursion in hierarchy traversal algorithms.",
    },
    {
        "code": "ACTIVE_USER_INACTIVE_EMP",
        "name": "Active Security Login for Inactive Employee",
        "severity": "CRITICAL",
        "category": "SECURITY",
        "module": "SecurityUserMst",
        "description": "Active security user login linked to inactive, resigned, or deleted employee.",
        "impact": "High security risk — terminated employee retains active access.",
    },
    {
        "code": "ORPHAN_USER_LOGIN",
        "name": "Orphan Security User Login",
        "severity": "CRITICAL",
        "category": "SECURITY",
        "module": "SecurityUserMst",
        "description": "Security user record linked to non-existent employee ID.",
        "impact": "Orphan authentication credential with broken employee reference.",
    },
    {
        "code": "MULTIPLE_ACTIVE_USERS",
        "name": "Multiple Active User Logins for Single Employee",
        "severity": "WARNING",
        "category": "SECURITY",
        "module": "SecurityUserMst",
        "description": "Single employee assigned multiple active user authentication accounts.",
        "impact": "Account credential duplication and audit trail ambiguity.",
    },
    {
        "code": "ATTENDANCE_ORPHAN_EMP",
        "name": "Attendance Punch Linked to Non-Existent Employee",
        "severity": "CRITICAL",
        "category": "ATTENDANCE",
        "module": "PayAttendance",
        "description": "Attendance biometric punch event referencing non-existent employee ID.",
        "impact": "Orphan transaction logs in time & attendance subsystem.",
    },
    {
        "code": "LEAVE_ORPHAN_EMP",
        "name": "Leave Application Linked to Non-Existent Employee",
        "severity": "CRITICAL",
        "category": "LEAVE",
        "module": "LeaveRequest",
        "description": "Leave application referencing non-existent employee ID.",
        "impact": "Orphan transaction logs in leave application subsystem.",
    },
    {
        "code": "PAYROLL_CORRUPTED_NET_PAY",
        "name": "Corrupted Payroll Net Salary Output",
        "severity": "CRITICAL",
        "category": "PAYROLL",
        "module": "PayEarnedSalary",
        "description": "Salary header math discrepancy where NetPay != TotalEarned - TotalDeduction.",
        "impact": "Financial discrepancy in disbursed salary payments.",
    },
]


class CrossDomainQualityService:
    """
    Centralized cross-domain data quality and data-integrity service evaluating rules across
    Employee, Organization, Contact, Security, Manager Hierarchy, Attendance, Leave, and Payroll.
    """

    def _get_rule_sql(self, rule_code: str, comp_id: int | None = None) -> tuple[str, dict[str, Any]]:
        params: dict[str, Any] = {}
        comp_clause = ""
        if comp_id:
            params["comp_id"] = comp_id
            comp_clause = "AND e.CompID = :comp_id"

        if rule_code == "DUP_EMP_CODE":
            sql = f"""
            SELECT
                CONCAT('EMP-', e.EmpID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.EmployeeMst' as table_name,
                'DUP_EMP_CODE' as rule_failed,
                'CRITICAL' as severity,
                'MASTER' as category,
                CONCAT('Duplicate active EmployeeCode ', e.EmpCode, ' shared across multiple records.') as issue_detail
            FROM dbo.EmployeeMst e
            INNER JOIN (
                SELECT EmpCode
                FROM dbo.EmployeeMst
                WHERE EmpIsActive = 1 AND ISNULL(EmpIsDeleted, 0) = 0
                  AND (EmpResignDate IS NULL OR EmpResignDate > GETDATE())
                  AND EmpCode IS NOT NULL AND EmpCode <> ''
                GROUP BY EmpCode HAVING COUNT(*) > 1
            ) dup ON dup.EmpCode = e.EmpCode
            WHERE e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE()) {comp_clause}
            """
        elif rule_code == "ACTIVE_DELETED_CONFLICT":
            sql = f"""
            SELECT
                CONCAT('EMP-', e.EmpID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.EmployeeMst' as table_name,
                'ACTIVE_DELETED_CONFLICT' as rule_failed,
                'CRITICAL' as severity,
                'MASTER' as category,
                'Record flagged as both EmpIsActive=1 and EmpIsDeleted=1.' as issue_detail
            FROM dbo.EmployeeMst e
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 1 {comp_clause}
            """
        elif rule_code == "ACTIVE_PAST_RESIGNED":
            sql = f"""
            SELECT
                CONCAT('EMP-', e.EmpID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.EmployeeMst' as table_name,
                'ACTIVE_PAST_RESIGNED' as rule_failed,
                'WARNING' as severity,
                'MASTER' as category,
                CONCAT('Active employee has historical resignation date ', CONVERT(VARCHAR, e.EmpResignDate, 23)) as issue_detail
            FROM dbo.EmployeeMst e
            WHERE e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE() {comp_clause}
            """
        elif rule_code == "MISSING_OFFICIAL_RECORD":
            sql = f"""
            SELECT
                CONCAT('EMP-', e.EmpID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.EmployeeOfficialDet' as table_name,
                'MISSING_OFFICIAL_RECORD' as rule_failed,
                'CRITICAL' as severity,
                'MASTER' as category,
                'Active employee missing active assignment record in EmployeeOfficialDet.' as issue_detail
            FROM dbo.EmployeeMst e
            LEFT JOIN dbo.EmployeeOfficialDet o ON e.EmpID = o.EmpID AND o.EmpOfficeDetIsActive = 1 AND ISNULL(o.EmpOfficeDetIsDeleted, 0) = 0
            WHERE e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND o.EmpID IS NULL {comp_clause}
            """
        elif rule_code == "MISSING_ORG_ASSIGNMENT":
            sql = f"""
            SELECT
                CONCAT('OFF-', o.EmpOfficeDetID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.EmployeeOfficialDet' as table_name,
                'MISSING_ORG_ASSIGNMENT' as rule_failed,
                'WARNING' as severity,
                'ORG' as category,
                'Official record missing valid Company, Department, Designation, or Location linkage.' as issue_detail
            FROM dbo.EmployeeOfficialDet o
            INNER JOIN dbo.EmployeeMst e ON e.EmpID = o.EmpID
            WHERE o.EmpOfficeDetIsActive = 1 AND ISNULL(o.EmpOfficeDetIsDeleted, 0) = 0
              AND e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND (e.CompID IS NULL OR e.CompID = 0 OR o.DeptID IS NULL OR o.DeptID = 0 OR o.DesigID IS NULL OR o.DesigID = 0 OR o.LocID IS NULL OR o.LocID = 0) {comp_clause}
            """
        elif rule_code == "MISSING_MANAGER":
            sql = f"""
            SELECT
                CONCAT('EMP-', e.EmpID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.EmployeeReportingDet' as table_name,
                'MISSING_MANAGER' as rule_failed,
                'WARNING' as severity,
                'HIERARCHY' as category,
                'Active employee missing active reporting manager assignment.' as issue_detail
            FROM dbo.EmployeeMst e
            LEFT JOIN dbo.EmployeeReportingDet r ON e.EmpID = r.EmpID AND r.ReportingDetIsActive = 1 AND ISNULL(r.ReportingDetIsDeleted, 0) = 0
            WHERE e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND (r.ReportingEmpID IS NULL OR r.ReportingEmpID = 0) {comp_clause}
            """
        elif rule_code == "INVALID_MANAGER_FK":
            sql = f"""
            SELECT
                CONCAT('REP-', r.EmpReportingDetID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.EmployeeReportingDet' as table_name,
                'INVALID_MANAGER_FK' as rule_failed,
                'CRITICAL' as severity,
                'HIERARCHY' as category,
                CONCAT('Reporting manager ID ', r.ReportingEmpID, ' references non-existent employee master row.') as issue_detail
            FROM dbo.EmployeeReportingDet r
            INNER JOIN dbo.EmployeeMst e ON e.EmpID = r.EmpID
            LEFT JOIN dbo.EmployeeMst m ON m.EmpID = r.ReportingEmpID
            WHERE r.ReportingDetIsActive = 1 AND ISNULL(r.ReportingDetIsDeleted, 0) = 0
              AND e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND r.ReportingEmpID IS NOT NULL AND r.ReportingEmpID > 0 AND m.EmpID IS NULL {comp_clause}
            """
        elif rule_code == "SELF_REPORTING_EMPLOYEE":
            sql = f"""
            SELECT
                CONCAT('REP-', r.EmpReportingDetID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.EmployeeReportingDet' as table_name,
                'SELF_REPORTING_EMPLOYEE' as rule_failed,
                'CRITICAL' as severity,
                'HIERARCHY' as category,
                'Employee is assigned as their own reporting manager (EmpID = ReportingEmpID).' as issue_detail
            FROM dbo.EmployeeReportingDet r
            INNER JOIN dbo.EmployeeMst e ON e.EmpID = r.EmpID
            WHERE r.ReportingDetIsActive = 1 AND ISNULL(r.ReportingDetIsDeleted, 0) = 0
              AND e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND r.EmpID = r.ReportingEmpID {comp_clause}
            """
        elif rule_code == "CIRCULAR_MANAGER_HIERARCHY":
            sql = f"""
            SELECT
                CONCAT('REP-', r1.EmpReportingDetID) as record_id,
                e1.EmpID as emp_id,
                e1.EmpCode as emp_code,
                ISNULL(e1.EmpFirstName, '') + ' ' + ISNULL(e1.EmpLastName, '') as emp_name,
                'dbo.EmployeeReportingDet' as table_name,
                'CIRCULAR_MANAGER_HIERARCHY' as rule_failed,
                'CRITICAL' as severity,
                'HIERARCHY' as category,
                CONCAT('Circular reporting loop between Employee ', e1.EmpID, ' and Manager ', r1.ReportingEmpID) as issue_detail
            FROM dbo.EmployeeReportingDet r1
            INNER JOIN dbo.EmployeeReportingDet r2 ON r1.ReportingEmpID = r2.EmpID AND r2.ReportingEmpID = r1.EmpID
            INNER JOIN dbo.EmployeeMst e1 ON e1.EmpID = r1.EmpID
            WHERE r1.ReportingDetIsActive = 1 AND ISNULL(r1.ReportingDetIsDeleted, 0) = 0
              AND r2.ReportingDetIsActive = 1 AND ISNULL(r2.ReportingDetIsDeleted, 0) = 0
              AND e1.EmpIsActive = 1 AND ISNULL(e1.EmpIsDeleted, 0) = 0
              AND (e1.EmpResignDate IS NULL OR e1.EmpResignDate > GETDATE())
              AND r1.EmpID < r1.ReportingEmpID {comp_clause}
            """
        elif rule_code == "ACTIVE_USER_INACTIVE_EMP":
            sql = f"""
            SELECT
                CONCAT('USER-', u.UserID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.SecurityUserMst' as table_name,
                'ACTIVE_USER_INACTIVE_EMP' as rule_failed,
                'CRITICAL' as severity,
                'SECURITY' as category,
                CONCAT('Active user login (UserID: ', u.UserID, ', Login: ', ISNULL(u.UserName, ''), ') linked to inactive/deleted employee.') as issue_detail
            FROM dbo.SecurityUserMst u
            INNER JOIN dbo.EmployeeMst e ON e.EmpID = u.UserEmpID
            WHERE u.UserIsActive = 1 AND ISNULL(u.UserIsDeleted, 0) = 0
              AND (e.EmpIsActive = 0 OR e.EmpIsDeleted = 1 OR (e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE())) {comp_clause}
            """
        elif rule_code == "ORPHAN_USER_LOGIN":
            sql = """
            SELECT
                CONCAT('USER-', u.UserID) as record_id,
                u.UserEmpID as emp_id,
                'N/A' as emp_code,
                'N/A' as emp_name,
                'dbo.SecurityUserMst' as table_name,
                'ORPHAN_USER_LOGIN' as rule_failed,
                'CRITICAL' as severity,
                'SECURITY' as category,
                CONCAT('Security user login ID ', u.UserID, ' (Login: ', ISNULL(u.UserName, ''), ') references non-existent UserEmpID ', u.UserEmpID) as issue_detail
            FROM dbo.SecurityUserMst u
            LEFT JOIN dbo.EmployeeMst e ON e.EmpID = u.UserEmpID
            WHERE u.UserEmpID IS NOT NULL AND u.UserEmpID > 0 AND e.EmpID IS NULL
            """
        elif rule_code == "MULTIPLE_ACTIVE_USERS":
            sql = f"""
            SELECT
                CONCAT('EMP-', e.EmpID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.SecurityUserMst' as table_name,
                'MULTIPLE_ACTIVE_USERS' as rule_failed,
                'WARNING' as severity,
                'SECURITY' as category,
                'Single employee possesses multiple active authentication logins.' as issue_detail
            FROM dbo.EmployeeMst e
            INNER JOIN (
                SELECT UserEmpID
                FROM dbo.SecurityUserMst
                WHERE UserIsActive = 1 AND ISNULL(UserIsDeleted, 0) = 0 AND UserEmpID IS NOT NULL AND UserEmpID > 0
                GROUP BY UserEmpID HAVING COUNT(*) > 1
            ) dup ON dup.UserEmpID = e.EmpID
            WHERE e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE()) {comp_clause}
            """
        elif rule_code == "ATTENDANCE_ORPHAN_EMP":
            sql = """
            SELECT
                CONCAT('ATT-', a.AttID) as record_id,
                a.AttEmpID as emp_id,
                'N/A' as emp_code,
                'N/A' as emp_name,
                'dbo.PayAttendance' as table_name,
                'ATTENDANCE_ORPHAN_EMP' as rule_failed,
                'CRITICAL' as severity,
                'ATTENDANCE' as category,
                CONCAT('Attendance punch row ID ', a.AttID, ' references non-existent EmpID ', a.AttEmpID) as issue_detail
            FROM dbo.PayAttendance a
            LEFT JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID
            WHERE a.AttEmpID IS NOT NULL AND a.AttEmpID > 0 AND e.EmpID IS NULL
            """
        elif rule_code == "LEAVE_ORPHAN_EMP":
            sql = """
            SELECT
                CONCAT('LEAVE-', l.LeaveRequestID) as record_id,
                l.LeaveRequestByEmpID as emp_id,
                'N/A' as emp_code,
                'N/A' as emp_name,
                'dbo.LeaveRequest' as table_name,
                'LEAVE_ORPHAN_EMP' as rule_failed,
                'CRITICAL' as severity,
                'LEAVE' as category,
                CONCAT('Leave request ID ', l.LeaveRequestID, ' references non-existent EmpID ', l.LeaveRequestByEmpID) as issue_detail
            FROM dbo.LeaveRequest l
            LEFT JOIN dbo.EmployeeMst e ON e.EmpID = l.LeaveRequestByEmpID
            WHERE l.LeaveRequestByEmpID IS NOT NULL AND l.LeaveRequestByEmpID > 0 AND e.EmpID IS NULL
            """
        elif rule_code == "PAYROLL_CORRUPTED_NET_PAY":
            sql = """
            SELECT
                CONCAT('SAL-', s.EarnedSalID) as record_id,
                e.EmpID as emp_id,
                e.EmpCode as emp_code,
                ISNULL(e.EmpFirstName, '') + ' ' + ISNULL(e.EmpLastName, '') as emp_name,
                'dbo.PayEarnedSalary' as table_name,
                'PAYROLL_CORRUPTED_NET_PAY' as rule_failed,
                'CRITICAL' as severity,
                'PAYROLL' as category,
                CONCAT('Salary Header ID ', s.EarnedSalID, ' (Month: ', s.EarnedSalMonth, ') NetPay ', s.NetPay, ' != Earned ', s.TotalEarned, ' - Deduction ', s.TotalDeduction) as issue_detail
            FROM dbo.PayEarnedSalary s
            LEFT JOIN dbo.EmployeeMst e ON e.EmpID = s.EarnedSalEmpID
            WHERE ABS(ISNULL(s.NetPay, 0) - (ISNULL(s.TotalEarned, 0) - ISNULL(s.TotalDeduction, 0))) > 1.0
            """
        else:
            raise ValueError(f"Unknown rule code: {rule_code}")

        return sql, params

    def get_cross_domain_overview(self, comp_id: int | None = None) -> CrossDomainOverviewResponse:
        rules_matrix: list[CrossDomainQualityRuleInfo] = []
        tot_issues = 0
        crit_cnt = 0
        warn_cnt = 0
        info_cnt = 0
        affected_emp_set: set[int] = set()

        category_counts: dict[str, dict[str, int]] = {}
        module_counts: dict[str, int] = {}

        for rdef in RULE_DEFINITIONS:
            code = rdef["code"]
            sql, params = self._get_rule_sql(code, comp_id)

            cnt_sql = f"SELECT COUNT(*) as cnt, COUNT(DISTINCT emp_id) as emp_cnt FROM ({sql}) sub"
            res = execute_readonly_query(cnt_sql, params)
            cnt = res[0]["cnt"] if res else 0
            emp_cnt = res[0]["emp_cnt"] if res else 0

            # Extract distinct affected emp IDs for overall count
            if cnt > 0:
                emp_sql = f"SELECT DISTINCT emp_id FROM ({sql}) sub WHERE emp_id IS NOT NULL AND emp_id > 0"
                emp_res = execute_readonly_query(emp_sql, params)
                for er in emp_res:
                    if er["emp_id"]:
                        affected_emp_set.add(int(er["emp_id"]))

            sev = rdef["severity"]
            cat = rdef["category"]
            mod = rdef["module"]

            tot_issues += cnt
            if sev == "CRITICAL":
                crit_cnt += cnt
            elif sev == "WARNING":
                warn_cnt += cnt
            else:
                info_cnt += cnt

            if cat not in category_counts:
                category_counts[cat] = {"total": 0, "critical": 0, "warning": 0, "info": 0, "rules": 0}
            category_counts[cat]["total"] += cnt
            category_counts[cat]["rules"] += 1
            if sev == "CRITICAL":
                category_counts[cat]["critical"] += cnt
            elif sev == "WARNING":
                category_counts[cat]["warning"] += cnt
            else:
                category_counts[cat]["info"] += cnt

            module_counts[mod] = module_counts.get(mod, 0) + cnt

            rules_matrix.append(
                CrossDomainQualityRuleInfo(
                    rule_code=code,
                    rule_name=rdef["name"],
                    severity=sev,
                    category=cat,
                    description=rdef["description"],
                    impact=rdef["impact"],
                    issue_count=cnt,
                    affected_employees_count=emp_cnt,
                )
            )

        cat_name_map = {
            "MASTER": "Employee Master",
            "ORG": "Organization Assignment",
            "HIERARCHY": "Reporting Hierarchy",
            "SECURITY": "User & Security",
            "ATTENDANCE": "Attendance & Time",
            "LEAVE": "Leave & Balances",
            "PAYROLL": "Payroll & Salary",
        }

        categories_summary = [
            CrossDomainCategorySummary(
                category_code=cat_code,
                category_name=cat_name_map.get(cat_code, cat_code),
                rule_count=info["rules"],
                total_issues=info["total"],
                critical_issues=info["critical"],
                warning_issues=info["warning"],
                info_issues=info["info"],
            )
            for cat_code, info in category_counts.items()
        ]

        modules_summary = [
            CrossDomainModuleSummary(
                module_code=mod_code,
                module_name=f"dbo.{mod_code}",
                total_issues=issue_cnt,
            )
            for mod_code, issue_cnt in module_counts.items()
        ]

        # Calculate health score: 100 - penalty normalized
        failing_critical = sum(1 for r in rules_matrix if r.severity == "CRITICAL" and r.issue_count > 0)
        failing_warning = sum(1 for r in rules_matrix if r.severity == "WARNING" and r.issue_count > 0)
        penalty = (failing_critical * 12.0) + (failing_warning * 4.0)
        health_score = max(0.0, min(100.0, round(100.0 - penalty, 1)))

        return CrossDomainOverviewResponse(
            total_issues=tot_issues,
            critical_issues_count=crit_cnt,
            warning_issues_count=warn_cnt,
            info_issues_count=info_cnt,
            total_affected_employees=len(affected_emp_set),
            overall_health_score=health_score,
            rules=rules_matrix,
            categories=categories_summary,
            modules=modules_summary,
        )

    def get_cross_domain_issues(
        self,
        rule_code: str | None = None,
        category: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
        comp_id: int | None = None,
    ) -> CrossDomainIssuesListResponse:
        active_rules = [r for r in RULE_DEFINITIONS if (not rule_code or r["code"] == rule_code) and (not category or r["category"] == category)]

        queries: list[str] = []
        all_params: dict[str, Any] = {}

        for rdef in active_rules:
            sql, params = self._get_rule_sql(rdef["code"], comp_id)
            queries.append(sql)
            all_params.update(params)

        if not queries:
            return CrossDomainIssuesListResponse(
                items=[],
                total=0,
                limit=limit,
                offset=offset,
                rule_code=rule_code,
                category=category,
                search=search,
            )

        union_sql = " UNION ALL ".join(queries)

        search_clause = ""
        if search and search.strip():
            all_params["search"] = f"%{search.strip()}%"
            search_clause = """
            WHERE (emp_code LIKE :search OR emp_name LIKE :search OR issue_detail LIKE :search OR table_name LIKE :search OR record_id LIKE :search)
            """

        full_sql = f"""
        WITH all_issues AS (
            {union_sql}
        )
        SELECT *
        FROM all_issues
        {search_clause}
        ORDER BY
            CASE severity WHEN 'CRITICAL' THEN 1 WHEN 'WARNING' THEN 2 ELSE 3 END,
            emp_id, record_id
        OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY;
        """

        cnt_sql = f"""
        WITH all_issues AS (
            {union_sql}
        )
        SELECT COUNT(*) as total
        FROM all_issues
        {search_clause};
        """

        res_items = execute_readonly_query(full_sql, all_params)
        res_cnt = execute_readonly_query(cnt_sql, all_params)
        total = res_cnt[0]["total"] if res_cnt else 0

        items = [
            CrossDomainIssueRecord(
                record_id=str(r["record_id"]),
                emp_id=r["emp_id"],
                emp_code=r["emp_code"],
                emp_name=r["emp_name"],
                table_name=r["table_name"],
                rule_failed=r["rule_failed"],
                severity=r["severity"],
                category=r["category"],
                issue_detail=r["issue_detail"],
            )
            for r in res_items
        ]

        return CrossDomainIssuesListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            rule_code=rule_code,
            category=category,
            search=search,
        )

    def download_cross_domain_export(
        self,
        rule_code: str | None = None,
        category: str | None = None,
        search: str | None = None,
        comp_id: int | None = None,
    ) -> bytes:
        issues_resp = self.get_cross_domain_issues(
            rule_code=rule_code,
            category=category,
            search=search,
            limit=10000,
            offset=0,
            comp_id=comp_id,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Record ID",
            "Employee ID",
            "Employee Code",
            "Employee Name",
            "Target Table",
            "Rule Failed",
            "Severity",
            "Category",
            "Issue Detail",
        ])

        for item in issues_resp.items:
            writer.writerow([
                item.record_id,
                item.emp_id or "",
                item.emp_code or "",
                item.emp_name or "",
                item.table_name,
                item.rule_failed,
                item.severity,
                item.category,
                item.issue_detail,
            ])

        return output.getvalue().encode("utf-8")
