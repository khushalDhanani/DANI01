import io
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.employee.schemas import IssueSeverity
from app.modules.payroll.schemas import (
    EmployeePayrollHistoryResponse,
    EmployeePayslipItem,
    PayrollDataQualityResponse,
    PayrollMetadataResponse,
    PayrollMonthlySummaryItem,
    PayrollOverviewResponse,
    PayrollQualityIssueItem,
    PayrollQualityIssuesListResponse,
    PayrollQualityRuleInfo,
    PayrollRegisterItem,
    PayrollRegisterListResponse,
    PayrollRelationshipInfo,
    PayrollTableSchemaInfo,
)


class PayrollService:
    def get_payroll_metadata(self) -> PayrollMetadataResponse:
        tables = [
            PayrollTableSchemaInfo(
                table_name="dbo.PayEarnedSalary",
                table_type="HEADER",
                record_count=81899,
                primary_key="EarnedSalID",
                foreign_keys=["EarnedSalEmpID", "EarnedCompID", "EarnedDeptID"],
            ),
            PayrollTableSchemaInfo(
                table_name="dbo.PayEarnedSalaryDet",
                table_type="DETAIL_EARNING",
                record_count=706082,
                primary_key="EarnedSalDetID",
                foreign_keys=["EarnedSalID", "PayHeadID"],
            ),
            PayrollTableSchemaInfo(
                table_name="dbo.PayEarnedSalaryDeductionDet",
                table_type="DETAIL_DEDUCTION",
                record_count=75545,
                primary_key="EarnedSalDeuctionDetID",
                foreign_keys=["EarnedSalID", "DeductionHeadID"],
            ),
            PayrollTableSchemaInfo(
                table_name="dbo.PaySalaryStatement",
                table_type="PAYSLIP_BANK",
                record_count=10760,
                primary_key="PayStatementID",
                foreign_keys=["PayEarnedSalID", "EmpID"],
            ),
            PayrollTableSchemaInfo(
                table_name="dbo.PayHeadMst",
                table_type="MASTER",
                record_count=131,
                primary_key="PayHeadID",
                foreign_keys=[],
            ),
            PayrollTableSchemaInfo(
                table_name="dbo.PayDeductionHeadMst",
                table_type="MASTER",
                record_count=67,
                primary_key="DeductionHeadID",
                foreign_keys=[],
            ),
        ]

        relationships = [
            PayrollRelationshipInfo(
                source_table="dbo.EmployeeMst",
                target_table="dbo.PayEarnedSalary",
                cardinality="1:N",
                status="Confirmed",
                join_condition="dbo.EmployeeMst.EmpID = dbo.PayEarnedSalary.EarnedSalEmpID",
            ),
            PayrollRelationshipInfo(
                source_table="dbo.PayEarnedSalary",
                target_table="dbo.PayEarnedSalaryDet",
                cardinality="1:N",
                status="Confirmed",
                join_condition="dbo.PayEarnedSalary.EarnedSalID = dbo.PayEarnedSalaryDet.EarnedSalID",
            ),
            PayrollRelationshipInfo(
                source_table="dbo.PayEarnedSalary",
                target_table="dbo.PayEarnedSalaryDeductionDet",
                cardinality="1:N",
                status="Confirmed",
                join_condition="dbo.PayEarnedSalary.EarnedSalID = dbo.PayEarnedSalaryDeductionDet.EarnedSalID",
            ),
            PayrollRelationshipInfo(
                source_table="dbo.PayEarnedSalary",
                target_table="dbo.PaySalaryStatement",
                cardinality="1:1",
                status="Confirmed",
                join_condition="dbo.PayEarnedSalary.EarnedSalID = dbo.PaySalaryStatement.PayEarnedSalID",
            ),
            PayrollRelationshipInfo(
                source_table="dbo.PayEarnedSalaryDet",
                target_table="dbo.PayHeadMst",
                cardinality="N:1",
                status="Confirmed",
                join_condition="dbo.PayEarnedSalaryDet.PayHeadID = dbo.PayHeadMst.PayHeadID",
            ),
            PayrollRelationshipInfo(
                source_table="dbo.PayEarnedSalaryDeductionDet",
                target_table="dbo.PayDeductionHeadMst",
                cardinality="N:1",
                status="Confirmed",
                join_condition="dbo.PayEarnedSalaryDeductionDet.DeductionHeadID = dbo.PayDeductionHeadMst.DeductionHeadID",
            ),
        ]

        return PayrollMetadataResponse(tables=tables, relationships=relationships)

    def get_payroll_overview(self, comp_id: int | None = None) -> PayrollOverviewResponse:
        params: dict[str, Any] = {}
        comp_where = ""
        if comp_id:
            comp_where = "WHERE EarnedCompID = :comp_id"
            params["comp_id"] = comp_id

        # 1. Total records and aggregate totals
        q_tot = f"""
        SELECT
            COUNT(*) as total_payroll_records,
            COUNT(DISTINCT EarnedSalEmpID) as emps_with_payroll,
            SUM(ISNULL(NetPay, 0)) as lifetime_net_pay,
            SUM(ISNULL(TotalEarned, 0)) as lifetime_earned,
            SUM(ISNULL(TotalDeduction, 0)) as lifetime_deduction
        FROM dbo.PayEarnedSalary
        {comp_where};
        """
        r_tot = execute_readonly_query(q_tot, params)
        tot = r_tot[0] if r_tot else {}

        # 2. Total active employees without payroll
        emp_comp_where = "WHERE e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0"
        if comp_id:
            emp_comp_where += " AND e.CompID = :comp_id"

        q_no_pay = f"""
        SELECT COUNT(*) as emps_without_payroll
        FROM dbo.EmployeeMst e
        LEFT JOIN dbo.PayEarnedSalary s ON s.EarnedSalEmpID = e.EmpID
        {emp_comp_where}
          AND s.EarnedSalID IS NULL;
        """
        r_no_pay = execute_readonly_query(q_no_pay, params)
        no_pay_cnt = r_no_pay[0]["emps_without_payroll"] if r_no_pay else 0

        # 3. Monthly trends (top 12 months)
        m_comp_where = "WHERE EarnedSalMonth IS NOT NULL AND EarnedSalMonth <> ''"
        if comp_id:
            m_comp_where += " AND EarnedCompID = :comp_id"

        q_months = f"""
        SELECT TOP 12
            EarnedSalMonth as sal_month,
            COUNT(*) as record_count,
            SUM(ISNULL(TotalEarned, 0)) as total_earned,
            SUM(ISNULL(TotalDeduction, 0)) as total_deduction,
            SUM(ISNULL(NetPay, 0)) as total_net_pay
        FROM dbo.PayEarnedSalary
        {m_comp_where}
        GROUP BY EarnedSalMonth
        ORDER BY EarnedSalMonth DESC;
        """
        r_months = execute_readonly_query(q_months, params)

        monthly_trends = [
            PayrollMonthlySummaryItem(
                sal_month=str(m["sal_month"]),
                record_count=m["record_count"],
                total_earned=round(float(m["total_earned"] or 0.0), 2),
                total_deduction=round(float(m["total_deduction"] or 0.0), 2),
                total_net_pay=round(float(m["total_net_pay"] or 0.0), 2),
            )
            for m in r_months
        ]

        latest_month = monthly_trends[0].sal_month if monthly_trends else "N/A"
        latest_rec_cnt = monthly_trends[0].record_count if monthly_trends else 0
        latest_net = monthly_trends[0].total_net_pay if monthly_trends else 0.0

        return PayrollOverviewResponse(
            total_payroll_records=tot.get("total_payroll_records") or 0,
            total_employees_with_payroll=tot.get("emps_with_payroll") or 0,
            total_employees_without_payroll=no_pay_cnt,
            latest_payroll_month=latest_month,
            latest_month_record_count=latest_rec_cnt,
            latest_month_net_pay=latest_net,
            lifetime_total_net_pay=round(float(tot.get("lifetime_net_pay") or 0.0), 2),
            lifetime_total_earned=round(float(tot.get("lifetime_earned") or 0.0), 2),
            lifetime_total_deduction=round(float(tot.get("lifetime_deduction") or 0.0), 2),
            monthly_trends=monthly_trends,
        )

    def get_payroll_directory(
        self,
        status_filter: str | None = None,
        search: str | None = None,
        dept_id: int | None = None,
        comp_id: int | None = None,
        month: str | None = None,
        emp_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PayrollRegisterListResponse:
        where_clauses = ["1=1"]
        params: dict[str, Any] = {}

        if dept_id:
            where_clauses.append("s.EarnedDeptID = :dept_id")
            params["dept_id"] = dept_id
        if comp_id:
            where_clauses.append("s.EarnedCompID = :comp_id")
            params["comp_id"] = comp_id
        if emp_id:
            where_clauses.append("s.EarnedSalEmpID = :emp_id")
            params["emp_id"] = emp_id
        if month:
            where_clauses.append("s.EarnedSalMonth = :month")
            params["month"] = month

        if status_filter:
            sf = status_filter.upper()
            if sf == "CORRUPTED":
                where_clauses.append(
                    "ABS(ISNULL(s.NetPay, 0) - (ISNULL(s.TotalEarned, 0) - ISNULL(s.TotalDeduction, 0))) > 1.0"
                )
            elif sf == "NEGATIVE":
                where_clauses.append(
                    "(s.NetPay < 0 OR s.TotalEarned < 0 OR s.TotalDeduction < 0)"
                )
            elif sf == "ACTIVE":
                where_clauses.append("e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0")

        if search:
            where_clauses.append(
                "(e.EmpCode LIKE :search OR e.EmpFirstName LIKE :search OR e.EmpLastName LIKE :search OR s.EarnedSalMonth LIKE :search)"
            )
            params["search"] = f"%{search}%"

        where_sql = " AND ".join(where_clauses)

        q_count = f"""
        SELECT COUNT(*) as total
        FROM dbo.PayEarnedSalary s
        LEFT JOIN dbo.EmployeeMst e ON e.EmpID = s.EarnedSalEmpID
        LEFT JOIN dbo.OrgDepartmentMst d ON d.DeptID = s.EarnedDeptID
        WHERE {where_sql};
        """
        r_count = execute_readonly_query(q_count, params)
        total = r_count[0]["total"] if r_count else 0

        q_rows = f"""
        SELECT
            s.EarnedSalID,
            s.EarnedSalEmpID as emp_id,
            ISNULL(e.EmpCode, CONCAT('EMP-', s.EarnedSalEmpID)) as emp_code,
            CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name,
            d.DeptName as dept_name,
            s.EarnedSalMonth as sal_month,
            ISNULL(s.EarnedTotPaidDays, 0) as paid_days,
            ISNULL(s.EarnedPresent, 0) as present_days,
            ISNULL(s.TotalEarned, 0) as total_earned,
            ISNULL(s.TotalDeduction, 0) as total_deduction,
            ISNULL(s.NetPay, 0) as net_pay,
            ISNULL(s.CTCGross, 0) as ctc_gross,
            CONVERT(varchar(10), s.EarnedPayDate, 120) as pay_date,
            ISNULL(e.EmpIsActive, 1) as is_active
        FROM dbo.PayEarnedSalary s
        LEFT JOIN dbo.EmployeeMst e ON e.EmpID = s.EarnedSalEmpID
        LEFT JOIN dbo.OrgDepartmentMst d ON d.DeptID = s.EarnedDeptID
        WHERE {where_sql}
        ORDER BY s.EarnedSalMonth DESC, s.EarnedSalID DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        params["limit"] = limit
        params["offset"] = offset

        r_rows = execute_readonly_query(q_rows, params)
        items = [
            PayrollRegisterItem(
                earned_sal_id=r["EarnedSalID"],
                emp_id=r["emp_id"],
                emp_code=r["emp_code"] or "N/A",
                emp_name=r["emp_name"] or f"Employee #{r['emp_id']}",
                dept_name=r["dept_name"] or "Unassigned Department",
                sal_month=str(r["sal_month"] or "N/A"),
                paid_days=float(r["paid_days"] or 0.0),
                present_days=float(r["present_days"] or 0.0),
                total_earned=round(float(r["total_earned"] or 0.0), 2),
                total_deduction=round(float(r["total_deduction"] or 0.0), 2),
                net_pay=round(float(r["net_pay"] or 0.0), 2),
                ctc_gross=round(float(r["ctc_gross"] or 0.0), 2),
                pay_date=r["pay_date"],
                is_active=bool(r["is_active"]),
            )
            for r in r_rows
        ]

        return PayrollRegisterListResponse(total=total, limit=limit, offset=offset, items=items)

    def export_payroll_directory(
        self, status_filter: str | None = None, search: str | None = None
    ) -> str:
        data = self.get_payroll_directory(
            status_filter=status_filter, search=search, limit=5000, offset=0
        )
        output = io.StringIO()
        output.write(
            "EarnedSalID,EmpID,EmpCode,EmpName,Department,SalMonth,PaidDays,TotalEarned,TotalDeduction,NetPay,PayDate\n"
        )
        for item in data.items:
            output.write(
                f'"{item.earned_sal_id}","{item.emp_id}","{item.emp_code}","{item.emp_name}","{item.dept_name or ""}","{item.sal_month}",{item.paid_days},{item.total_earned},{item.total_deduction},{item.net_pay},"{item.pay_date or ""}"\n'
            )
        return output.getvalue()

    def get_payroll_quality(self) -> PayrollDataQualityResponse:
        dq_sql = """
        SELECT 'ORPHAN_PAYROLL_HEADER' AS code, COUNT(*) AS cnt
        FROM dbo.PayEarnedSalary s LEFT JOIN dbo.EmployeeMst e ON e.EmpID = s.EarnedSalEmpID WHERE e.EmpID IS NULL
        UNION ALL
        SELECT 'CORRUPTED_NET_PAY', COUNT(*)
        FROM dbo.PayEarnedSalary WHERE ABS(ISNULL(NetPay, 0) - (ISNULL(TotalEarned, 0) - ISNULL(TotalDeduction, 0))) > 1.0
        UNION ALL
        SELECT 'ORPHAN_PAYROLL_DETAIL', COUNT(*)
        FROM dbo.PayEarnedSalaryDet d LEFT JOIN dbo.PayEarnedSalary s ON s.EarnedSalID = d.EarnedSalID WHERE s.EarnedSalID IS NULL
        UNION ALL
        SELECT 'DUP_PAYROLL_PERIOD', COUNT(*)
        FROM (
            SELECT EarnedSalEmpID, EarnedSalMonth FROM dbo.PayEarnedSalary
            WHERE EarnedSalEmpID IS NOT NULL AND EarnedSalMonth IS NOT NULL
            GROUP BY EarnedSalEmpID, EarnedSalMonth HAVING COUNT(*) > 1
        ) sub
        UNION ALL
        SELECT 'NEGATIVE_SALARY', COUNT(*)
        FROM dbo.PayEarnedSalary WHERE NetPay < 0 OR TotalEarned < 0 OR TotalDeduction < 0
        UNION ALL
        SELECT 'MISSING_PAYROLL_RECORD', COUNT(*)
        FROM dbo.EmployeeMst e LEFT JOIN dbo.PayEarnedSalary s ON s.EarnedSalEmpID = e.EmpID
        WHERE e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0 AND s.EarnedSalID IS NULL;
        """
        rows = execute_readonly_query(dq_sql)
        counts = {r["code"]: r["cnt"] for r in rows}

        rules = [
            PayrollQualityRuleInfo(
                rule_code="ORPHAN_PAYROLL_HEADER",
                rule_name="Orphan Payroll Header",
                severity=IssueSeverity.CRITICAL,
                description="Payroll header record linked to non-existent employee",
                issue_count=counts.get("ORPHAN_PAYROLL_HEADER", 0),
                impact="Unattributed salary disbursement",
                recommendation="Investigate and link or purge orphaned payroll records",
            ),
            PayrollQualityRuleInfo(
                rule_code="CORRUPTED_NET_PAY",
                rule_name="Corrupted Net Pay Calculation",
                severity=IssueSeverity.CRITICAL,
                description="Net pay differs from (Total Earned - Total Deduction)",
                issue_count=counts.get("CORRUPTED_NET_PAY", 0),
                impact="Financial calculation discrepancy in salary register",
                recommendation="Recalculate and reconcile earned and deduction components",
            ),
            PayrollQualityRuleInfo(
                rule_code="ORPHAN_PAYROLL_DETAIL",
                rule_name="Orphan Payroll Detail Line",
                severity=IssueSeverity.CRITICAL,
                description="Earning or deduction detail row without header record",
                issue_count=counts.get("ORPHAN_PAYROLL_DETAIL", 0),
                impact="Unlinked financial line item",
                recommendation="Remove or map unlinked detail records to parent header",
            ),
            PayrollQualityRuleInfo(
                rule_code="DUP_PAYROLL_PERIOD",
                rule_name="Duplicate Payroll Period per Employee",
                severity=IssueSeverity.WARNING,
                description="Multiple payroll headers for same employee and salary month",
                issue_count=counts.get("DUP_PAYROLL_PERIOD", 0),
                impact="Risk of double salary payout",
                recommendation="Merge or deactivate duplicate salary period entries",
            ),
            PayrollQualityRuleInfo(
                rule_code="NEGATIVE_SALARY",
                rule_name="Negative Salary / Earnings Value",
                severity=IssueSeverity.WARNING,
                description="Negative values in net pay, earnings, or deductions",
                issue_count=counts.get("NEGATIVE_SALARY", 0),
                impact="Invalid negative payroll figures",
                recommendation="Inspect and correct negative salary component adjustments",
            ),
            PayrollQualityRuleInfo(
                rule_code="MISSING_PAYROLL_RECORD",
                rule_name="Active Employee Missing Payroll History",
                severity=IssueSeverity.INFO,
                description="Active employee with no historical payroll records",
                issue_count=counts.get("MISSING_PAYROLL_RECORD", 0),
                impact="Unprocessed salary eligibility",
                recommendation="Verify whether employee is newly onboarded or uncalculated",
            ),
        ]

        crit = sum(r.issue_count for r in rules if r.severity == IssueSeverity.CRITICAL)
        warn = sum(r.issue_count for r in rules if r.severity == IssueSeverity.WARNING)
        info = sum(r.issue_count for r in rules if r.severity == IssueSeverity.INFO)
        tot_issues = crit + warn + info

        health_score = max(0.0, round(100.0 - (crit * 5.0) - (warn * 2.0), 1))

        return PayrollDataQualityResponse(
            overall_health_score=health_score,
            total_issues_count=tot_issues,
            critical_issues_count=crit,
            warning_issues_count=warn,
            info_issues_count=info,
            rules=rules,
            summary_by_severity={"CRITICAL": crit, "WARNING": warn, "INFO": info},
        )

    def get_payroll_quality_issues(
        self, issue_code: str = "CORRUPTED_NET_PAY", limit: int = 20, offset: int = 0
    ) -> PayrollQualityIssuesListResponse:
        code = issue_code.upper()

        if code == "CORRUPTED_NET_PAY":
            base_sql = """
            FROM dbo.PayEarnedSalary s
            LEFT JOIN dbo.EmployeeMst e ON e.EmpID = s.EarnedSalEmpID
            WHERE ABS(ISNULL(s.NetPay, 0) - (ISNULL(s.TotalEarned, 0) - ISNULL(s.TotalDeduction, 0))) > 1.0
            """
            detail_expr = "'NetPay (' + CAST(s.NetPay AS varchar) + ') != TotalEarned (' + CAST(s.TotalEarned AS varchar) + ') - TotalDeduction (' + CAST(s.TotalDeduction AS varchar) + ')'"
            sev = IssueSeverity.CRITICAL
        elif code == "ORPHAN_PAYROLL_HEADER":
            base_sql = """
            FROM dbo.PayEarnedSalary s
            LEFT JOIN dbo.EmployeeMst e ON e.EmpID = s.EarnedSalEmpID
            WHERE e.EmpID IS NULL
            """
            detail_expr = "'Payroll header linked to non-existent EmpID ' + CAST(s.EarnedSalEmpID AS varchar)"
            sev = IssueSeverity.CRITICAL
        elif code == "NEGATIVE_SALARY":
            base_sql = """
            FROM dbo.PayEarnedSalary s
            LEFT JOIN dbo.EmployeeMst e ON e.EmpID = s.EarnedSalEmpID
            WHERE s.NetPay < 0 OR s.TotalEarned < 0 OR s.TotalDeduction < 0
            """
            detail_expr = "'Negative payroll value detected'"
            sev = IssueSeverity.WARNING
        else:
            base_sql = """
            FROM dbo.EmployeeMst e
            LEFT JOIN dbo.PayEarnedSalary s ON s.EarnedSalEmpID = e.EmpID
            WHERE e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0 AND s.EarnedSalID IS NULL
            """
            detail_expr = "'Active employee has no payroll records'"
            sev = IssueSeverity.INFO

        q_count = f"SELECT COUNT(*) as total {base_sql};"
        r_cnt = execute_readonly_query(q_count)
        total = r_cnt[0]["total"] if r_cnt else 0

        q_rows = f"""
        SELECT
            ISNULL(s.EarnedSalID, e.EmpID) as record_id,
            e.EmpID as emp_id,
            ISNULL(e.EmpCode, CONCAT('EMP-', e.EmpID)) as emp_code,
            CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name,
            s.EarnedSalMonth as sal_month,
            {detail_expr} as issue_detail
        {base_sql}
        ORDER BY record_id DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        r_rows = execute_readonly_query(q_rows, {"limit": limit, "offset": offset})
        items = [
            PayrollQualityIssueItem(
                record_id=r["record_id"],
                rule_code=code,
                severity=sev,
                emp_id=r["emp_id"],
                emp_code=r["emp_code"],
                emp_name=r["emp_name"],
                sal_month=str(r["sal_month"] or "N/A"),
                issue_detail=r["issue_detail"] or "Data quality violation detected",
            )
            for r in r_rows
        ]

        return PayrollQualityIssuesListResponse(total=total, limit=limit, offset=offset, items=items)

    def export_payroll_quality_issues(self, issue_code: str = "CORRUPTED_NET_PAY") -> str:
        data = self.get_payroll_quality_issues(issue_code=issue_code, limit=5000, offset=0)
        output = io.StringIO()
        output.write("RecordID,RuleCode,Severity,EmpID,EmpCode,EmpName,SalMonth,IssueDetail\n")
        for item in data.items:
            output.write(
                f'"{item.record_id}","{item.rule_code}","{item.severity.value}","{item.emp_id or ""}","{item.emp_code or ""}","{item.emp_name or ""}","{item.sal_month or ""}","{item.issue_detail}"\n'
            )
        return output.getvalue()

    def get_employee_payroll_history(self, emp_id: int) -> EmployeePayrollHistoryResponse:
        # 1. Employee Info
        q_emp = """
        SELECT
            e.EmpID,
            e.EmpCode,
            CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name,
            d.DeptName as dept_name,
            e.EmpIsActive
        FROM dbo.EmployeeMst e
        LEFT JOIN dbo.OrgDepartmentMst d ON d.DeptID = e.EmpTypeID
        WHERE e.EmpID = :emp_id;
        """
        r_emp = execute_readonly_query(q_emp, {"emp_id": emp_id})
        if not r_emp:
            return EmployeePayrollHistoryResponse(
                emp_id=emp_id, emp_code=f"EMP-{emp_id}", emp_name=f"Employee #{emp_id}"
            )

        e_info = r_emp[0]

        # 2. Payslip History
        q_slips = """
        SELECT
            s.EarnedSalID,
            s.EarnedSalMonth as sal_month,
            ISNULL(s.EarnedTotPaidDays, 0) as paid_days,
            ISNULL(s.EarnedPresent, 0) as present_days,
            ISNULL(s.EarnedAbsent, 0) as absent_days,
            ISNULL(s.TotalEarned, 0) as total_earned,
            ISNULL(s.TotalDeduction, 0) as total_deduction,
            ISNULL(s.NetPay, 0) as net_pay,
            st.BankName as bank_name,
            st.RMFFolioNo as bank_acc_no,
            CONVERT(varchar(10), s.EarnedPayDate, 120) as pay_date
        FROM dbo.PayEarnedSalary s
        LEFT JOIN dbo.PaySalaryStatement st ON st.PayEarnedSalID = s.EarnedSalID
        WHERE s.EarnedSalEmpID = :emp_id
        ORDER BY s.EarnedSalMonth DESC;
        """
        r_slips = execute_readonly_query(q_slips, {"emp_id": emp_id})
        history = [
            EmployeePayslipItem(
                earned_sal_id=s["EarnedSalID"],
                sal_month=str(s["sal_month"] or "N/A"),
                paid_days=float(s["paid_days"] or 0.0),
                present_days=float(s["present_days"] or 0.0),
                absent_days=float(s["absent_days"] or 0.0),
                total_earned=round(float(s["total_earned"] or 0.0), 2),
                total_deduction=round(float(s["total_deduction"] or 0.0), 2),
                net_pay=round(float(s["net_pay"] or 0.0), 2),
                bank_name=s["bank_name"],
                bank_account_no=s["bank_acc_no"],
                pay_date=s["pay_date"],
            )
            for s in r_slips
        ]

        tot_net = sum(h.net_pay for h in history)
        latest_m = history[0].sal_month if history else "N/A"

        return EmployeePayrollHistoryResponse(
            emp_id=emp_id,
            emp_code=e_info["EmpCode"] or f"EMP-{emp_id}",
            emp_name=e_info["emp_name"] or f"Employee #{emp_id}",
            dept_name=e_info["dept_name"] or "Unassigned Department",
            is_active=bool(e_info["EmpIsActive"]),
            total_payslips_count=len(history),
            lifetime_net_pay=round(tot_net, 2),
            latest_month=latest_m,
            history_items=history,
        )
