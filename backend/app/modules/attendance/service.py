import csv
import io
import logging
from datetime import datetime
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.attendance.schemas import (
    AttendanceDataQualityResponse,
    AttendanceDirectoryResponse,
    AttendanceLogItem,
    AttendanceMetrics,
    AttendanceOrgHierarchyResponse,
    AttendanceOverviewResponse,
    AttendanceQualityIssueItem,
    AttendanceQualityIssuesListResponse,
    AttendanceQualityRuleResult,
    DepartmentDetailResponse,
    EmployeeLifetimeAttendanceResponse,
    EmployeeLifetimeLeaveTypeBreakdown,
    LeaveApplicationItem,
    LeaveApplicationsListResponse,
    LeaveBalanceItem,
    LeaveBalancesListResponse,
    LeaveOverviewResponse,
    OrgHierarchyAttendanceNode,
    PunchMetrics,
    ShiftDistributionItem,
)
from app.modules.employee.schemas import IssueSeverity

logger = logging.getLogger(__name__)


class AttendanceService:
    """Single-Source-of-Truth Domain Service for Attendance & Leave Intelligence."""

    def get_attendance_overview(
        self, dept_id: int | None = None, comp_id: int | None = None
    ) -> AttendanceOverviewResponse:
        where_clauses = ["1=1"]
        params: dict[str, Any] = {}
        if dept_id:
            where_clauses.append("AttDeptID = :dept_id")
            params["dept_id"] = dept_id
        if comp_id:
            where_clauses.append("AttCompID = :comp_id")
            params["comp_id"] = comp_id
        where_sql = " AND ".join(where_clauses)

        # 1. Total counts from PayAttendance using AttLeaveLabelID and punch timestamps
        q_totals = f"""
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT AttEmpID) as total_emps,
            SUM(CASE WHEN AttLeaveLabelID = 6 OR AttActInTime IS NOT NULL OR AttActOutTime IS NOT NULL THEN 1 ELSE 0 END) as present_days,
            SUM(CASE WHEN AttLeaveLabelID = 7 OR (AttActInTime IS NULL AND AttActOutTime IS NULL AND ISNULL(AttLeaveLabelID, 0) NOT IN (6, 8, 10, 9)) THEN 1 ELSE 0 END) as absent_days,
            SUM(CASE WHEN AttLeaveLabelID IN (11, 12, 14, 15, 16, 17, 18, 19, 22, 23, 25, 28, 30, 32, 33) THEN 1 ELSE 0 END) as half_days,
            SUM(CASE WHEN ISNULL(AttLeaveLabelID, 0) IN (1, 2, 9, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 25, 28, 30, 32, 33) THEN 1 ELSE 0 END) as leave_days,
            SUM(CASE WHEN AttLeaveLabelID = 10 THEN 1 ELSE 0 END) as weekly_offs,
            SUM(CASE WHEN AttLeaveLabelID = 8 THEN 1 ELSE 0 END) as paid_holidays
        FROM dbo.PayAttendance
        WHERE {where_sql};
        """
        totals = execute_readonly_query(q_totals, params)[0]

        tot = totals["total_records"] or 1

        att_metrics = AttendanceMetrics(
            total_attendance_records=totals["total_records"] or 0,
            employees_with_attendance=totals["total_emps"] or 0,
            present_days=totals["present_days"] or 0,
            present_pct=round(((totals["present_days"] or 0) / tot) * 100.0, 1),
            absent_days=totals["absent_days"] or 0,
            absent_pct=round(((totals["absent_days"] or 0) / tot) * 100.0, 1),
            half_days=totals["half_days"] or 0,
            half_days_pct=round(((totals["half_days"] or 0) / tot) * 100.0, 1),
            leave_days=totals["leave_days"] or 0,
            leave_days_pct=round(((totals["leave_days"] or 0) / tot) * 100.0, 1),
            weekly_offs=totals["weekly_offs"] or 0,
            paid_holidays=totals["paid_holidays"] or 0,
        )

        # 2. Punch metrics
        q_punches = f"""
        SELECT
            COUNT(*) as total_punches,
            SUM(CASE WHEN AttActInTime IS NOT NULL AND AttActOutTime IS NOT NULL THEN 1 ELSE 0 END) as valid_pairs,
            SUM(CASE WHEN AttActInTime IS NOT NULL AND AttActOutTime IS NULL THEN 1 ELSE 0 END) as missing_out,
            SUM(CASE WHEN AttActInTime IS NULL AND AttActOutTime IS NOT NULL THEN 1 ELSE 0 END) as missing_in,
            SUM(CASE WHEN AttLateComeMins > 0 THEN 1 ELSE 0 END) as late_arrivals,
            SUM(CASE WHEN AttEarlyGoneMins > 0 THEN 1 ELSE 0 END) as early_departures,
            SUM(CASE WHEN AttActOTMins > 0 THEN 1 ELSE 0 END) as ot_records,
            COALESCE(SUM(AttActOTMins), 0) / 60.0 as total_ot_hours
        FROM dbo.PayAttendance
        WHERE {where_sql};
        """
        pm = execute_readonly_query(q_punches, params)[0]
        punch_metrics = PunchMetrics(
            total_punches_logged=pm["total_punches"] or 0,
            valid_punch_pairs=pm["valid_pairs"] or 0,
            missing_punch_out_count=pm["missing_out"] or 0,
            missing_punch_in_count=pm["missing_in"] or 0,
            late_arrivals_count=pm["late_arrivals"] or 0,
            early_departures_count=pm["early_departures"] or 0,
            overtime_records_count=pm["ot_records"] or 0,
            total_overtime_hours=round(float(pm["total_ot_hours"] or 0.0), 1),
        )

        # 3. Shift distribution
        q_shifts = f"""
        SELECT
            s.ShiftID as shift_id,
            s.ShiftCode as shift_code,
            s.ShiftDescription as shift_description,
            CAST(s.FromTime AS VARCHAR) as from_time,
            CAST(s.ToTime AS VARCHAR) as to_time,
            COUNT(a.AttID) as assigned_attendance_count
        FROM dbo.PayAttendance a
        LEFT JOIN dbo.PayShiftMst s ON s.ShiftID = a.AttShiftID
        WHERE {where_sql}
        GROUP BY s.ShiftID, s.ShiftCode, s.ShiftDescription, s.FromTime, s.ToTime
        ORDER BY assigned_attendance_count DESC;
        """
        shift_rows = execute_readonly_query(q_shifts, params)
        shift_dist: list[ShiftDistributionItem] = []
        for sr in shift_rows:
            cnt = sr.get("assigned_attendance_count") or sr.get("assigned_cnt") or 0
            pct = round((cnt / tot) * 100.0, 1)
            shift_dist.append(
                ShiftDistributionItem(
                    shift_id=sr.get("shift_id") or sr.get("ShiftID") or 0,
                    shift_code=sr.get("shift_code") or sr.get("ShiftCode") or "GS",
                    shift_description=sr.get("shift_description") or sr.get("ShiftDescription") or "General Shift",
                    from_time=str(sr.get("from_time") or sr.get("FromTime") or "09:00:00")[:8],
                    to_time=str(sr.get("to_time") or sr.get("ToTime") or "18:00:00")[:8],
                    assigned_attendance_count=cnt,
                    percentage=pct,
                )
            )

        return AttendanceOverviewResponse(
            attendance_metrics=att_metrics,
            punch_metrics=punch_metrics,
            shift_distribution=shift_dist,
        )

    def get_attendance_directory(
        self,
        status_filter: str | None = None,
        search: str | None = None,
        dept_id: int | None = None,
        comp_id: int | None = None,
        emp_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> AttendanceDirectoryResponse:
        where_clauses = ["1=1"]
        params: dict[str, Any] = {}

        if dept_id:
            where_clauses.append("a.AttDeptID = :dept_id")
            params["dept_id"] = dept_id
        if comp_id:
            where_clauses.append("a.AttCompID = :comp_id")
            params["comp_id"] = comp_id
        if emp_id:
            where_clauses.append("a.AttEmpID = :emp_id")
            params["emp_id"] = emp_id

        if status_filter:
            sf = status_filter.upper()
            if sf == "PRESENT":
                where_clauses.append(
                    "(a.AttActInTime IS NOT NULL OR a.AttActOutTime IS NOT NULL OR a.AttSalType IN ('P', 'PRESENT'))"
                )
            elif sf == "ABSENT":
                where_clauses.append(
                    "(a.AttActInTime IS NULL AND a.AttActOutTime IS NULL AND (s.ShiftCode IS NULL OR s.ShiftCode NOT IN ('WO', 'PH')))"
                )
            elif sf == "LATE":
                where_clauses.append("a.AttLateComeMins > 0")
            elif sf == "EARLY":
                where_clauses.append("a.AttEarlyGoneMins > 0")
            elif sf == "OT":
                where_clauses.append("a.AttActOTMins > 0")
            elif sf == "LEAVE":
                where_clauses.append(
                    "(a.AttSalType IN ('PL', 'CL', 'SL', 'CO', 'ML', 'LWP') OR a.AttLeaveLabelID IS NOT NULL)"
                )
            elif sf in ("WO", "WEEKLY_OFF"):
                where_clauses.append("s.ShiftCode = 'WO'")
            elif sf in ("PH", "HOLIDAY"):
                where_clauses.append("s.ShiftCode = 'PH'")

        # Noise reduction: Unless explicitly searching for off-days, filter out unpunched Weekly Off / Public Holiday noise rows
        if not status_filter or status_filter.upper() not in ("WO", "WEEKLY_OFF", "PH", "HOLIDAY"):
            where_clauses.append(
                "NOT (s.ShiftCode IN ('WO', 'PH') AND a.AttActInTime IS NULL AND a.AttActOutTime IS NULL)"
            )

        if search:
            where_clauses.append(
                "(e.EmpCode LIKE :search OR e.EmpFirstName LIKE :search OR e.EmpLastName LIKE :search OR s.ShiftCode LIKE :search OR a.AttSalType LIKE :search)"
            )
            params["search"] = f"%{search}%"

        where_sql = " AND ".join(where_clauses)

        q_count = f"""
        SELECT COUNT(*) as total
        FROM dbo.PayAttendance a
        LEFT JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID
        LEFT JOIN dbo.PayShiftMst s ON s.ShiftID = a.AttShiftID
        WHERE {where_sql};
        """
        total = execute_readonly_query(q_count, params)[0]["total"]

        q_items = f"""
        SELECT
            a.AttID,
            a.AttEmpID,
            e.EmpCode,
            CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name,
            CONVERT(varchar(10), a.AttDate, 120) as att_date,
            a.AttSalType,
            CONVERT(varchar(8), a.AttActInTime, 108) as in_time,
            CONVERT(varchar(8), a.AttActOutTime, 108) as out_time,
            CONVERT(varchar(8), a.AttOffInTime, 108) as off_in_time,
            CONVERT(varchar(8), a.AttOffOutTime, 108) as off_out_time,
            s.ShiftCode,
            s.ShiftDescription,
            COALESCE(a.AttLateComeMins, 0) as late_mins,
            COALESCE(a.AttEarlyGoneMins, 0) as early_mins,
            COALESCE(a.AttActOTMins, 0) as ot_mins,
            CASE
                WHEN e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 THEN 'ACTIVE'
                WHEN e.EmpResignDate IS NOT NULL AND e.EmpResignDate <= GETDATE() THEN 'RESIGNED'
                ELSE 'INACTIVE'
            END as emp_status
        FROM dbo.PayAttendance a
        LEFT JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID
        LEFT JOIN dbo.PayShiftMst s ON s.ShiftID = a.AttShiftID
        WHERE {where_sql}
        ORDER BY a.AttDate DESC, a.AttID DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        params["limit"] = limit
        params["offset"] = offset

        rows = execute_readonly_query(q_items, params)
        items: list[AttendanceLogItem] = []
        for r in rows:
            in_t = r["in_time"]
            out_t = r["out_time"]
            shift = (r["ShiftCode"] or "").strip().upper()
            sal_t = (r["AttSalType"] or "").strip().upper()
            late = r["late_mins"] or 0
            early = r["early_mins"] or 0
            ot = r["ot_mins"] or 0

            if in_t is not None or out_t is not None:
                if late > 0 and early > 0:
                    status_label = "Late & Early Exit"
                elif late > 0:
                    status_label = "Late Coming"
                elif early > 0:
                    status_label = "Early Exit"
                elif ot > 0:
                    status_label = "Overtime"
                else:
                    status_label = "Present"
            elif shift == "WO":
                status_label = "Weekly Off"
            elif shift == "PH":
                status_label = "Public Holiday"
            elif sal_t in ("PL", "CL", "SL", "CO", "ML", "LWP"):
                status_label = "Leave"
            elif sal_t in ("A", "ABSENT"):
                status_label = "Absent"
            else:
                status_label = "Absent / Unpunched"

            items.append(
                AttendanceLogItem(
                    att_id=r["AttID"],
                    emp_id=r["AttEmpID"],
                    emp_code=r["EmpCode"],
                    emp_name=(r["emp_name"] or "").strip() or "Unnamed Employee",
                    att_date=r["att_date"] or "",
                    att_sal_type=r["AttSalType"] or "P",
                    status_label=status_label,
                    in_time=r["in_time"],
                    out_time=r["out_time"],
                    off_in_time=r["off_in_time"],
                    off_out_time=r["off_out_time"],
                    shift_code=r["ShiftCode"],
                    shift_desc=r["ShiftDescription"],
                    late_mins=r["late_mins"],
                    early_mins=r["early_mins"],
                    ot_mins=r["ot_mins"],
                    emp_status=r["emp_status"],
                )
            )

        return AttendanceDirectoryResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    def export_attendance_directory(
        self, status_filter: str | None = None, search: str | None = None
    ) -> str:
        data = self.get_attendance_directory(
            status_filter=status_filter, search=search, limit=10000, offset=0
        )
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Attendance ID",
                "Employee ID",
                "Employee Code",
                "Employee Name",
                "Attendance Date",
                "Status Code",
                "Status Label",
                "Actual Punch In",
                "Actual Punch Out",
                "Shift Code",
                "Late Arrival (Mins)",
                "Early Exit (Mins)",
                "Overtime (Mins)",
                "Employee Status",
            ]
        )
        for it in data.items:
            writer.writerow(
                [
                    it.att_id,
                    it.emp_id,
                    it.emp_code or "",
                    it.emp_name,
                    it.att_date,
                    it.att_sal_type,
                    it.status_label,
                    it.in_time or "",
                    it.out_time or "",
                    it.shift_code or "",
                    it.late_mins,
                    it.early_mins,
                    it.ot_mins,
                    it.emp_status,
                ]
            )
        return output.getvalue()

    def get_leave_overview(self) -> LeaveOverviewResponse:
        # 1. Total counts from LeaveRequest
        q_totals = """
        SELECT
            COUNT(*) as total_requests,
            SUM(CASE WHEN LeaveStatusID IN (13, 290) AND (LeaveCancel = 0 OR LeaveCancel IS NULL) AND LeaveRequestIsDeleted = 0 THEN 1 ELSE 0 END) as approved_cnt,
            SUM(CASE WHEN LeaveStatusID = 15 AND (LeaveCancel = 0 OR LeaveCancel IS NULL) AND LeaveRequestIsDeleted = 0 THEN 1 ELSE 0 END) as pending_cnt,
            SUM(CASE WHEN LeaveStatusID = 14 AND LeaveRequestIsDeleted = 0 THEN 1 ELSE 0 END) as rejected_cnt,
            SUM(CASE WHEN LeaveCancel = 1 OR LeaveRequestIsDeleted = 1 THEN 1 ELSE 0 END) as cancelled_cnt
        FROM dbo.LeaveRequest;
        """
        totals = execute_readonly_query(q_totals)[0]
        tot = totals["total_requests"] or 1

        # 2. Employees currently on active leave
        q_on_leave = """
        SELECT COUNT(DISTINCT LeaveRequestByEmpID) as active_on_leave
        FROM dbo.LeaveRequest
        WHERE LeaveStatusID IN (13, 290)
          AND (LeaveCancel = 0 OR LeaveCancel IS NULL)
          AND LeaveRequestIsDeleted = 0
          AND GETDATE() BETWEEN LeaveRequestFromDate AND LeaveRequestToDate;
        """
        active_on_leave = execute_readonly_query(q_on_leave)[0]["active_on_leave"] or 0

        # 3. Total employees with leave balance ledger
        q_bal_emps = """
        SELECT COUNT(DISTINCT EmpID) as total_bal_emps
        FROM dbo.PayMonthlyLeaveBalance;
        """
        total_bal_emps = execute_readonly_query(q_bal_emps)[0]["total_bal_emps"] or 0

        # 4. Leave type distribution
        q_types = """
        SELECT
            lt.LeaveTypeDesc,
            lt.LeaveTypeShortName,
            COUNT(lr.LeaveRequestID) as req_cnt
        FROM dbo.LeaveTypeMst lt
        LEFT JOIN dbo.LeaveRequest lr ON lr.LeaveTypeID = lt.LeaveTypeID
        WHERE lt.LeaveTypeIsActive = 1 AND lt.LeaveTypeIsDeleted = 0
        GROUP BY lt.LeaveTypeDesc, lt.LeaveTypeShortName
        ORDER BY req_cnt DESC;
        """
        type_rows = execute_readonly_query(q_types)
        type_dist = [
            {
                "leave_type": r["LeaveTypeDesc"] or "General Leave",
                "short_code": r["LeaveTypeShortName"] or "LV",
                "request_count": r["req_cnt"] or 0,
            }
            for r in type_rows
        ]

        return LeaveOverviewResponse(
            total_leave_requests=totals["total_requests"] or 0,
            approved_requests=totals["approved_cnt"] or 0,
            approved_pct=round(((totals["approved_cnt"] or 0) / tot) * 100.0, 1),
            pending_requests=totals["pending_cnt"] or 0,
            pending_pct=round(((totals["pending_cnt"] or 0) / tot) * 100.0, 1),
            rejected_requests=totals["rejected_cnt"] or 0,
            rejected_pct=round(((totals["rejected_cnt"] or 0) / tot) * 100.0, 1),
            cancelled_requests=totals["cancelled_cnt"] or 0,
            cancelled_pct=round(((totals["cancelled_cnt"] or 0) / tot) * 100.0, 1),
            active_employees_on_leave=active_on_leave,
            total_employees_with_leave_balance=total_bal_emps,
            leave_type_distribution=type_dist,
        )

    def get_leave_applications(
        self,
        status_filter: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> LeaveApplicationsListResponse:
        where_clauses = ["1=1"]
        params: dict[str, Any] = {}

        if status_filter:
            sf = status_filter.upper()
            if sf == "APPROVED":
                where_clauses.append(
                    "lr.LeaveStatusID IN (13, 290) AND (lr.LeaveCancel = 0 OR lr.LeaveCancel IS NULL) AND lr.LeaveRequestIsDeleted = 0"
                )
            elif sf == "PENDING":
                where_clauses.append(
                    "lr.LeaveStatusID = 15 AND (lr.LeaveCancel = 0 OR lr.LeaveCancel IS NULL) AND lr.LeaveRequestIsDeleted = 0"
                )
            elif sf == "REJECTED":
                where_clauses.append("lr.LeaveStatusID = 14 AND lr.LeaveRequestIsDeleted = 0")
            elif sf == "CANCELLED":
                where_clauses.append("(lr.LeaveCancel = 1 OR lr.LeaveRequestIsDeleted = 1)")

        if search:
            where_clauses.append(
                "(e.EmpCode LIKE :search OR e.EmpFirstName LIKE :search OR e.EmpLastName LIKE :search OR lt.LeaveTypeDesc LIKE :search OR lr.LeaveReason LIKE :search)"
            )
            params["search"] = f"%{search}%"

        where_sql = " AND ".join(where_clauses)

        q_count = f"""
        SELECT COUNT(*) as total
        FROM dbo.LeaveRequest lr
        LEFT JOIN dbo.EmployeeMst e ON e.EmpID = lr.LeaveRequestByEmpID
        LEFT JOIN dbo.LeaveTypeMst lt ON lt.LeaveTypeID = lr.LeaveTypeID
        WHERE {where_sql};
        """
        total = execute_readonly_query(q_count, params)[0]["total"]

        q_items = f"""
        SELECT
            lr.LeaveRequestID,
            lr.LeaveRequestByEmpID,
            e.EmpCode,
            CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name,
            CONVERT(varchar(10), lr.LeaveRequestDate, 120) as req_date,
            CONVERT(varchar(10), lr.LeaveRequestFromDate, 120) as from_date,
            CONVERT(varchar(10), lr.LeaveRequestToDate, 120) as to_date,
            lt.LeaveTypeShortName,
            lt.LeaveTypeDesc,
            COALESCE(lr.LeaveDays, 0) as leave_days,
            lr.LeaveApproveDays,
            lr.LeaveStatusID,
            COALESCE(lr.LeaveCancel, 0) as is_cancelled,
            lr.LeaveReason
        FROM dbo.LeaveRequest lr
        LEFT JOIN dbo.EmployeeMst e ON e.EmpID = lr.LeaveRequestByEmpID
        LEFT JOIN dbo.LeaveTypeMst lt ON lt.LeaveTypeID = lr.LeaveTypeID
        WHERE {where_sql}
        ORDER BY lr.LeaveRequestDate DESC, lr.LeaveRequestID DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        params["limit"] = limit
        params["offset"] = offset

        rows = execute_readonly_query(q_items, params)
        items: list[LeaveApplicationItem] = []
        for r in rows:
            st_id = r["LeaveStatusID"]
            canc = bool(r["is_cancelled"])
            status_desc = (
                "Cancelled"
                if canc
                else "Approved"
                if st_id in (13, 290)
                else "Rejected"
                if st_id == 14
                else "Pending"
                if st_id == 15
                else f"Status #{st_id}"
            )

            items.append(
                LeaveApplicationItem(
                    leave_request_id=r["LeaveRequestID"],
                    emp_id=r["LeaveRequestByEmpID"],
                    emp_code=r["EmpCode"],
                    emp_name=(r["emp_name"] or "").strip() or "Unnamed Employee",
                    request_date=r["req_date"] or "",
                    from_date=r["from_date"] or "",
                    to_date=r["to_date"] or "",
                    leave_type_code=r["LeaveTypeShortName"],
                    leave_type_desc=r["LeaveTypeDesc"] or "General Leave",
                    leave_days=float(r["leave_days"]),
                    approve_days=float(r["LeaveApproveDays"])
                    if r["LeaveApproveDays"] is not None
                    else None,
                    status_id=st_id,
                    status_desc=status_desc,
                    is_cancelled=canc,
                    reason=r["LeaveReason"],
                )
            )

        return LeaveApplicationsListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    def export_leave_applications(
        self, status_filter: str | None = None, search: str | None = None
    ) -> str:
        data = self.get_leave_applications(
            status_filter=status_filter, search=search, limit=10000, offset=0
        )
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Leave Request ID",
                "Employee ID",
                "Employee Code",
                "Employee Name",
                "Application Date",
                "From Date",
                "To Date",
                "Leave Type",
                "Requested Days",
                "Approved Days",
                "Status",
                "Reason",
            ]
        )
        for it in data.items:
            writer.writerow(
                [
                    it.leave_request_id,
                    it.emp_id,
                    it.emp_code or "",
                    it.emp_name,
                    it.request_date,
                    it.from_date,
                    it.to_date,
                    it.leave_type_desc or "",
                    it.leave_days,
                    it.approve_days if it.approve_days is not None else "",
                    it.status_desc,
                    it.reason or "",
                ]
            )
        return output.getvalue()

    def get_leave_balances(
        self,
        year_month: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> LeaveBalancesListResponse:
        where_clauses = ["1=1"]
        params: dict[str, Any] = {}

        if year_month:
            where_clauses.append("b.YearMonth = :year_month")
            params["year_month"] = year_month

        if search:
            where_clauses.append(
                "(e.EmpCode LIKE :search OR e.EmpFirstName LIKE :search OR e.EmpLastName LIKE :search OR b.YearMonth LIKE :search)"
            )
            params["search"] = f"%{search}%"

        where_sql = " AND ".join(where_clauses)

        q_count = f"""
        SELECT COUNT(*) as total
        FROM dbo.PayMonthlyLeaveBalance b
        LEFT JOIN dbo.EmployeeMst e ON e.EmpID = b.EmpID
        WHERE {where_sql};
        """
        total = execute_readonly_query(q_count, params)[0]["total"]

        q_items = f"""
        SELECT
            b.BalID,
            b.EmpID,
            e.EmpCode,
            CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name,
            b.YearMonth,
            COALESCE(b.TotalPresent, 0) as total_present,
            COALESCE(b.TotalAbsent, 0) as total_absent,
            COALESCE(b.OpPL, 0) as op_pl,
            COALESCE(b.EarnedPL, 0) as earned_pl,
            COALESCE(b.AvailedPL, 0) as availed_pl,
            COALESCE(b.EncashedPL, 0) as encashed_pl,
            COALESCE(b.OpCL, 0) as op_cl,
            COALESCE(b.EarnedCL, 0) as earned_cl,
            COALESCE(b.AvailedCL, 0) as availed_cl,
            COALESCE(b.OpSL, 0) as op_sl,
            COALESCE(b.EarnedSL, 0) as earned_sl,
            COALESCE(b.AvailedSL, 0) as availed_sl
        FROM dbo.PayMonthlyLeaveBalance b
        LEFT JOIN dbo.EmployeeMst e ON e.EmpID = b.EmpID
        WHERE {where_sql}
        ORDER BY b.YearMonth DESC, b.BalID DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        params["limit"] = limit
        params["offset"] = offset

        rows = execute_readonly_query(q_items, params)
        items: list[LeaveBalanceItem] = []
        for r in rows:
            net_pl = float(r["op_pl"] + r["earned_pl"] - r["availed_pl"] - r["encashed_pl"])
            net_cl = float(r["op_cl"] + r["earned_cl"] - r["availed_cl"])
            net_sl = float(r["op_sl"] + r["earned_sl"] - r["availed_sl"])

            items.append(
                LeaveBalanceItem(
                    bal_id=r["BalID"],
                    emp_id=r["EmpID"],
                    emp_code=r["EmpCode"],
                    emp_name=(r["emp_name"] or "").strip() or "Unnamed Employee",
                    year_month=r["YearMonth"],
                    total_present=float(r["total_present"]),
                    total_absent=float(r["total_absent"]),
                    op_pl=float(r["op_pl"]),
                    earned_pl=float(r["earned_pl"]),
                    availed_pl=float(r["availed_pl"]),
                    encashed_pl=float(r["encashed_pl"]),
                    net_pl_bal=round(net_pl, 1),
                    op_cl=float(r["op_cl"]),
                    earned_cl=float(r["earned_cl"]),
                    availed_cl=float(r["availed_cl"]),
                    net_cl_bal=round(net_cl, 1),
                    op_sl=float(r["op_sl"]),
                    earned_sl=float(r["earned_sl"]),
                    availed_sl=float(r["availed_sl"]),
                    net_sl_bal=round(net_sl, 1),
                )
            )

        return LeaveBalancesListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    def get_attendance_quality(self) -> AttendanceDataQualityResponse:
        q_rules = """
        SELECT
            -- Critical
            (SELECT COUNT(*) FROM dbo.PayAttendance a WHERE NOT EXISTS (SELECT 1 FROM dbo.EmployeeMst e WHERE e.EmpID = a.AttEmpID)) as orphan_att_emp,
            (SELECT COUNT(*) FROM dbo.LeaveRequest lr WHERE NOT EXISTS (SELECT 1 FROM dbo.EmployeeMst e WHERE e.EmpID = lr.LeaveRequestByEmpID)) as orphan_leave_emp,
            (SELECT COUNT(*) FROM dbo.LeaveRequest WHERE LeaveRequestToDate < LeaveRequestFromDate) as invalid_leave_dates,
            (SELECT COUNT(*) FROM dbo.PayMonthlyLeaveBalance WHERE (OpPL + EarnedPL - AvailedPL - EncashedPL) < 0 OR (OpCL + EarnedCL - AvailedCL) < 0 OR (OpSL + EarnedSL - AvailedSL) < 0) as negative_calculated_leave_balances,
            (SELECT COUNT(*) FROM dbo.PayAttendance a JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID WHERE (e.EmpIsActive = 0 OR e.EmpIsDeleted = 1) AND a.AttDate >= '2025-01-01') as recent_att_inactive_emp,

            -- Warning
            (SELECT COUNT(*) FROM (
                SELECT AttEmpID, AttDate FROM dbo.PayAttendance GROUP BY AttEmpID, AttDate HAVING COUNT(*) > 1
            ) t) as dup_att_emp_date,
            (SELECT COUNT(*) FROM dbo.PayAttendance WHERE AttActInTime IS NOT NULL AND AttActOutTime IS NOT NULL AND AttActOutTime < AttActInTime) as punch_out_before_in,
            (SELECT COUNT(*) FROM dbo.PayAttendance WHERE AttActInTime IS NOT NULL AND AttActOutTime IS NULL AND AttDate < DATEADD(day, -2, GETDATE())) as missing_punch_out,
            (SELECT COUNT(*) FROM dbo.PayAttendance WHERE AttActInTime IS NULL AND AttActOutTime IS NOT NULL) as missing_punch_in,
            (SELECT COUNT(*) FROM dbo.PayAttendance a WHERE a.AttShiftID IS NOT NULL AND NOT EXISTS (SELECT 1 FROM dbo.PayShiftMst s WHERE s.ShiftID = a.AttShiftID)) as orphan_att_shift,
            (SELECT COUNT(*) FROM dbo.LeaveRequest lr WHERE lr.LeaveTypeID IS NOT NULL AND NOT EXISTS (SELECT 1 FROM dbo.LeaveTypeMst lt WHERE lt.LeaveTypeID = lr.LeaveTypeID AND lt.LeaveTypeIsDeleted = 0)) as orphan_leave_type,
            (SELECT COUNT(*) FROM (
                SELECT lr1.LeaveRequestID
                FROM dbo.LeaveRequest lr1
                JOIN dbo.LeaveRequest lr2 ON lr1.LeaveRequestByEmpID = lr2.LeaveRequestByEmpID
                                         AND lr1.LeaveRequestID != lr2.LeaveRequestID
                                         AND lr1.LeaveRequestIsDeleted = 0 AND lr2.LeaveRequestIsDeleted = 0
                                         AND (lr1.LeaveCancel = 0 OR lr1.LeaveCancel IS NULL) AND (lr2.LeaveCancel = 0 OR lr2.LeaveCancel IS NULL)
                                         AND lr1.LeaveRequestFromDate <= lr2.LeaveRequestToDate
                                         AND lr1.LeaveRequestToDate >= lr2.LeaveRequestFromDate
            ) t) as overlapping_leave_requests,

            -- Info
            (SELECT COUNT(*) FROM dbo.PayAttendance a JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID WHERE (e.EmpIsActive = 0 OR e.EmpIsDeleted = 1) AND a.AttDate < '2025-01-01') as historical_att_inactive,
            (SELECT COUNT(*) FROM dbo.LeaveRequest WHERE LeaveStatusID IN (13, 15, 290) AND (LeaveReason IS NULL OR LTRIM(RTRIM(LeaveReason)) = '')) as leave_without_reason;
        """
        row = execute_readonly_query(q_rules)[0]

        rules: list[AttendanceQualityRuleResult] = [
            AttendanceQualityRuleResult(
                rule_code="ORPHAN_ATTENDANCE_EMP",
                rule_name="Orphan Attendance Record (Missing Employee)",
                severity=IssueSeverity.CRITICAL,
                description="Daily attendance entry references an EmpID that does not exist in Employee master.",
                issue_count=row["orphan_att_emp"] or 0,
                impact="Unattributable workforce attendance logs.",
                recommendation="Clean up orphan records or restore missing employee master entry.",
            ),
            AttendanceQualityRuleResult(
                rule_code="ORPHAN_LEAVE_EMP",
                rule_name="Orphan Leave Request (Missing Employee)",
                severity=IssueSeverity.CRITICAL,
                description="Leave application submitted for an employee ID that does not exist in Employee master.",
                issue_count=row["orphan_leave_emp"] or 0,
                impact="Broken leave records affecting payroll reconciliation.",
                recommendation="Investigate and re-map leave application to valid Employee ID.",
            ),
            AttendanceQualityRuleResult(
                rule_code="IMPOSSIBLE_LEAVE_DATES",
                rule_name="Impossible Leave Date Range (End Date Before Start Date)",
                severity=IssueSeverity.CRITICAL,
                description="Leave application has an End Date occurring strictly before its Start Date.",
                issue_count=row["invalid_leave_dates"] or 0,
                impact="Corrupted duration math and invalid date calculations.",
                recommendation="Fix start and end date boundaries in leave request.",
            ),
            AttendanceQualityRuleResult(
                rule_code="CORRUPTED_LEAVE_BALANCE",
                rule_name="Negative Calculated Leave Balance",
                severity=IssueSeverity.CRITICAL,
                description="Calculated net leave balance (Opening + Earned - Availed - Encashed) is negative.",
                issue_count=row["negative_calculated_leave_balances"] or 0,
                impact="Overdrawn leave balances causing payroll deduction discrepancies.",
                recommendation="Reconcile monthly leave balances and correct availed days.",
            ),
            AttendanceQualityRuleResult(
                rule_code="ACTIVE_ATTENDANCE_DELETED_EMP",
                rule_name="Recent Attendance Logged for Inactive/Deleted Employee",
                severity=IssueSeverity.CRITICAL,
                description="Attendance entries logged (2025+) for staff marked as Inactive or Resigned.",
                issue_count=row["recent_att_inactive_emp"] or 0,
                impact="Ghost attendance logging for departed personnel.",
                recommendation="Revoke biometric swipe access for separated staff immediately.",
            ),
            AttendanceQualityRuleResult(
                rule_code="DUPLICATE_ATTENDANCE_ROW",
                rule_name="Duplicate Attendance Rows (Same Employee + Date)",
                severity=IssueSeverity.CRITICAL if False else IssueSeverity.WARNING,
                description="Multiple attendance records created for the exact same Employee ID and Attendance Date.",
                issue_count=row["dup_att_emp_date"] or 0,
                impact="Risk of double-counting working days or overtime.",
                recommendation="Deduplicate attendance entries keeping the latest valid punch log.",
            ),
            AttendanceQualityRuleResult(
                rule_code="PUNCH_OUT_BEFORE_IN",
                rule_name="Punch Out Timestamp Earlier Than Punch In",
                severity=IssueSeverity.WARNING,
                description="Recorded Actual Punch Out timestamp is strictly earlier than Actual Punch In.",
                issue_count=row["punch_out_before_in"] or 0,
                impact="Negative working hours calculation and corrupted shift duration.",
                recommendation="Verify night-shift punch rollover logic or biometric clock times.",
            ),
            AttendanceQualityRuleResult(
                rule_code="MISSING_PUNCH_OUT",
                rule_name="Missing Punch Out (Unclosed Punch Log)",
                severity=IssueSeverity.WARNING,
                description="Punch In exists but Actual Punch Out timestamp is missing for past days.",
                issue_count=row["missing_punch_out"] or 0,
                impact="Incomplete daily work duration and automated attendance auto-absence.",
                recommendation="Prompt employee or HR for manual punch regularization.",
            ),
            AttendanceQualityRuleResult(
                rule_code="MISSING_PUNCH_IN",
                rule_name="Missing Punch In (Unstarted Punch Log)",
                severity=IssueSeverity.WARNING,
                description="Punch Out recorded but Actual Punch In timestamp is missing.",
                issue_count=row["missing_punch_in"] or 0,
                impact="Incomplete arrival timestamp preventing late-coming calculation.",
                recommendation="Submit attendance regularization for missing arrival time.",
            ),
            AttendanceQualityRuleResult(
                rule_code="ORPHAN_ATTENDANCE_SHIFT",
                rule_name="Invalid / Missing Shift Reference",
                severity=IssueSeverity.WARNING,
                description="Attendance entry assigned to a ShiftID that does not exist in PayShiftMst.",
                issue_count=row["orphan_att_shift"] or 0,
                impact="Inability to evaluate late arrival or early exit grace minutes.",
                recommendation="Re-assign attendance entries to valid active shift master.",
            ),
            AttendanceQualityRuleResult(
                rule_code="ORPHAN_LEAVE_TYPE",
                rule_name="Invalid / Deleted Leave Type Mapped",
                severity=IssueSeverity.WARNING,
                description="Leave application references a LeaveTypeID that is deleted or missing.",
                issue_count=row["orphan_leave_type"] or 0,
                impact="Unclassified leave type categorization.",
                recommendation="Map leave applications to active leave type catalog.",
            ),
            AttendanceQualityRuleResult(
                rule_code="OVERLAPPING_LEAVE_REQUESTS",
                rule_name="Overlapping Active Leave Applications",
                severity=IssueSeverity.WARNING,
                description="Multiple active approved/pending leave requests submitted for overlapping date ranges.",
                issue_count=row["overlapping_leave_requests"] or 0,
                impact="Double-counting leave days and duplicate balance deductions.",
                recommendation="Cancel redundant leave application.",
            ),
            AttendanceQualityRuleResult(
                rule_code="HISTORICAL_ATTENDANCE_INACTIVE",
                rule_name="Historical Attendance Records for Inactive Employees",
                severity=IssueSeverity.INFO,
                description="Archived attendance records for employees who have since resigned or left.",
                issue_count=row["historical_att_inactive"] or 0,
                impact="Informational audit trace for past workforce activity.",
                recommendation="No action required; valid historical retention.",
            ),
            AttendanceQualityRuleResult(
                rule_code="LEAVE_REQUEST_WITHOUT_REASON",
                rule_name="Leave Request Submitted Without Stated Reason",
                severity=IssueSeverity.INFO,
                description="Approved or pending leave application submitted with blank reason or remarks.",
                issue_count=row["leave_without_reason"] or 0,
                impact="Informational governance gap in leave documentation.",
                recommendation="Encourage employees to provide brief reason during submission.",
            ),
        ]

        crit = sum(1 for r in rules if r.severity == IssueSeverity.CRITICAL and r.issue_count > 0)
        warn = sum(1 for r in rules if r.severity == IssueSeverity.WARNING and r.issue_count > 0)
        info = sum(1 for r in rules if r.severity == IssueSeverity.INFO and r.issue_count > 0)

        penalty = (crit * 6.0) + (warn * 2.0)
        health_score = max(0.0, min(100.0, round(100.0 - penalty, 1)))

        return AttendanceDataQualityResponse(
            overall_health_score=health_score,
            critical_issues_count=sum(
                r.issue_count for r in rules if r.severity == IssueSeverity.CRITICAL
            ),
            warning_issues_count=sum(
                r.issue_count for r in rules if r.severity == IssueSeverity.WARNING
            ),
            info_issues_count=sum(r.issue_count for r in rules if r.severity == IssueSeverity.INFO),
            rules=rules,
            summary_by_severity={"CRITICAL": crit, "WARNING": warn, "INFO": info},
        )

    def get_attendance_quality_issues(
        self,
        issue_code: str,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> AttendanceQualityIssuesListResponse:
        items: list[AttendanceQualityIssueItem] = []
        total = 0

        search_sql = (
            f" AND (CAST(a.AttID AS VARCHAR) LIKE '%{search}%' OR e.EmpFirstName LIKE '%{search}%' OR e.EmpLastName LIKE '%{search}%' OR e.EmpCode LIKE '%{search}%')"
            if search
            else ""
        )
        leave_search_sql = (
            f" AND (CAST(lr.LeaveRequestID AS VARCHAR) LIKE '%{search}%' OR e.EmpFirstName LIKE '%{search}%' OR e.EmpLastName LIKE '%{search}%' OR e.EmpCode LIKE '%{search}%')"
            if search
            else ""
        )

        if issue_code == "ORPHAN_ATTENDANCE_EMP":
            q_cnt = f"SELECT COUNT(*) as t FROM dbo.PayAttendance a WHERE NOT EXISTS (SELECT 1 FROM dbo.EmployeeMst e WHERE e.EmpID = a.AttEmpID) {search_sql}"
            total = execute_readonly_query(q_cnt)[0]["t"]
            q = f"SELECT TOP {limit} a.AttID, a.AttEmpID, CONVERT(varchar(10), a.AttDate, 120) as d FROM dbo.PayAttendance a WHERE NOT EXISTS (SELECT 1 FROM dbo.EmployeeMst e WHERE e.EmpID = a.AttEmpID) {search_sql} ORDER BY a.AttID DESC"
            for r in execute_readonly_query(q):
                items.append(
                    AttendanceQualityIssueItem(
                        record_id=str(r["AttID"]),
                        entity_name=f"Emp #{r['AttEmpID']}",
                        entity_type="PayAttendance",
                        context_info=r["d"],
                        issue_detail=f"Attendance record #{r['AttID']} references non-existent EmpID #{r['AttEmpID']}.",
                        status_detail="ORPHAN_EMP",
                    )
                )

        elif issue_code == "ORPHAN_LEAVE_EMP":
            q_cnt = f"SELECT COUNT(*) as t FROM dbo.LeaveRequest lr WHERE NOT EXISTS (SELECT 1 FROM dbo.EmployeeMst e WHERE e.EmpID = lr.LeaveRequestByEmpID) {leave_search_sql}"
            total = execute_readonly_query(q_cnt)[0]["t"]
            q = f"SELECT TOP {limit} lr.LeaveRequestID, lr.LeaveRequestByEmpID, CONVERT(varchar(10), lr.LeaveRequestDate, 120) as d FROM dbo.LeaveRequest lr WHERE NOT EXISTS (SELECT 1 FROM dbo.EmployeeMst e WHERE e.EmpID = lr.LeaveRequestByEmpID) {leave_search_sql} ORDER BY lr.LeaveRequestID DESC"
            for r in execute_readonly_query(q):
                items.append(
                    AttendanceQualityIssueItem(
                        record_id=str(r["LeaveRequestID"]),
                        entity_name=f"Emp #{r['LeaveRequestByEmpID']}",
                        entity_type="LeaveRequest",
                        context_info=r["d"],
                        issue_detail=f"Leave request #{r['LeaveRequestID']} references non-existent EmpID #{r['LeaveRequestByEmpID']}.",
                        status_detail="ORPHAN_EMP",
                    )
                )

        elif issue_code == "IMPOSSIBLE_LEAVE_DATES":
            q_cnt = f"SELECT COUNT(*) as t FROM dbo.LeaveRequest lr LEFT JOIN dbo.EmployeeMst e ON e.EmpID = lr.LeaveRequestByEmpID WHERE lr.LeaveRequestToDate < lr.LeaveRequestFromDate {leave_search_sql}"
            total = execute_readonly_query(q_cnt)[0]["t"]
            q = f"SELECT TOP {limit} lr.LeaveRequestID, CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name, CONVERT(varchar(10), lr.LeaveRequestFromDate, 120) as f, CONVERT(varchar(10), lr.LeaveRequestToDate, 120) as t FROM dbo.LeaveRequest lr LEFT JOIN dbo.EmployeeMst e ON e.EmpID = lr.LeaveRequestByEmpID WHERE lr.LeaveRequestToDate < lr.LeaveRequestFromDate {leave_search_sql} ORDER BY lr.LeaveRequestID DESC"
            for r in execute_readonly_query(q):
                items.append(
                    AttendanceQualityIssueItem(
                        record_id=str(r["LeaveRequestID"]),
                        entity_name=r["emp_name"] or "Unknown",
                        entity_type="LeaveRequest",
                        context_info=f"{r['f']} to {r['t']}",
                        issue_detail=f"Leave end date ({r['t']}) is earlier than start date ({r['f']}).",
                        status_detail="INVALID_DATES",
                    )
                )

        elif issue_code == "CORRUPTED_LEAVE_BALANCE":
            bal_search = (
                f" AND (e.EmpFirstName LIKE '%{search}%' OR e.EmpLastName LIKE '%{search}%' OR e.EmpCode LIKE '%{search}%')"
                if search
                else ""
            )
            q_cnt = f"SELECT COUNT(*) as t FROM dbo.PayMonthlyLeaveBalance b LEFT JOIN dbo.EmployeeMst e ON e.EmpID = b.EmpID WHERE ((b.OpPL + b.EarnedPL - b.AvailedPL - b.EncashedPL) < 0 OR (b.OpCL + b.EarnedCL - b.AvailedCL) < 0 OR (b.OpSL + b.EarnedSL - b.AvailedSL) < 0) {bal_search}"
            total = execute_readonly_query(q_cnt)[0]["t"]
            q = f"SELECT TOP {limit} b.BalID, b.YearMonth, CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name, (b.OpPL + b.EarnedPL - b.AvailedPL - b.EncashedPL) as net_pl, (b.OpCL + b.EarnedCL - b.AvailedCL) as net_cl FROM dbo.PayMonthlyLeaveBalance b LEFT JOIN dbo.EmployeeMst e ON e.EmpID = b.EmpID WHERE ((b.OpPL + b.EarnedPL - b.AvailedPL - b.EncashedPL) < 0 OR (b.OpCL + b.EarnedCL - b.AvailedCL) < 0 OR (b.OpSL + b.EarnedSL - b.AvailedSL) < 0) {bal_search} ORDER BY b.BalID DESC"
            for r in execute_readonly_query(q):
                items.append(
                    AttendanceQualityIssueItem(
                        record_id=str(r["BalID"]),
                        entity_name=r["emp_name"] or "Unknown",
                        entity_type="PayMonthlyLeaveBalance",
                        context_info=r["YearMonth"],
                        issue_detail=f"Negative calculated leave balance (PL: {r['net_pl']}, CL: {r['net_cl']}) for period {r['YearMonth']}.",
                        status_detail="NEGATIVE_BAL",
                    )
                )

        elif issue_code == "ACTIVE_ATTENDANCE_DELETED_EMP":
            q_cnt = f"SELECT COUNT(*) as t FROM dbo.PayAttendance a JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID WHERE (e.EmpIsActive = 0 OR e.EmpIsDeleted = 1) AND a.AttDate >= '2025-01-01' {search_sql}"
            total = execute_readonly_query(q_cnt)[0]["t"]
            q = f"SELECT TOP {limit} a.AttID, CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name, CONVERT(varchar(10), a.AttDate, 120) as d FROM dbo.PayAttendance a JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID WHERE (e.EmpIsActive = 0 OR e.EmpIsDeleted = 1) AND a.AttDate >= '2025-01-01' {search_sql} ORDER BY a.AttID DESC"
            for r in execute_readonly_query(q):
                items.append(
                    AttendanceQualityIssueItem(
                        record_id=str(r["AttID"]),
                        entity_name=r["emp_name"] or "Inactive Employee",
                        entity_type="PayAttendance",
                        context_info=r["d"],
                        issue_detail=f"Attendance logged on {r['d']} for inactive/deleted employee.",
                        status_detail="INACTIVE_STAFF",
                    )
                )

        elif issue_code == "PUNCH_OUT_BEFORE_IN":
            q_cnt = f"SELECT COUNT(*) as t FROM dbo.PayAttendance a LEFT JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID WHERE a.AttActInTime IS NOT NULL AND a.AttActOutTime IS NOT NULL AND a.AttActOutTime < a.AttActInTime {search_sql}"
            total = execute_readonly_query(q_cnt)[0]["t"]
            q = f"SELECT TOP {limit} a.AttID, CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name, CONVERT(varchar(10), a.AttDate, 120) as d, CONVERT(varchar(8), a.AttActInTime, 108) as in_t, CONVERT(varchar(8), a.AttActOutTime, 108) as out_t FROM dbo.PayAttendance a LEFT JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID WHERE a.AttActInTime IS NOT NULL AND a.AttActOutTime IS NOT NULL AND a.AttActOutTime < a.AttActInTime {search_sql} ORDER BY a.AttID DESC"
            for r in execute_readonly_query(q):
                items.append(
                    AttendanceQualityIssueItem(
                        record_id=str(r["AttID"]),
                        entity_name=r["emp_name"] or "Unknown",
                        entity_type="PayAttendance",
                        context_info=r["d"],
                        issue_detail=f"Punch out ({r['out_t']}) occurs before punch in ({r['in_t']}) on {r['d']}.",
                        status_detail="REVERSED_PUNCH",
                    )
                )

        elif issue_code == "MISSING_PUNCH_OUT":
            q_cnt = f"SELECT COUNT(*) as t FROM dbo.PayAttendance a LEFT JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID WHERE a.AttActInTime IS NOT NULL AND a.AttActOutTime IS NULL AND a.AttDate < DATEADD(day, -2, GETDATE()) {search_sql}"
            total = execute_readonly_query(q_cnt)[0]["t"]
            q = f"SELECT TOP {limit} a.AttID, CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name, CONVERT(varchar(10), a.AttDate, 120) as d, CONVERT(varchar(8), a.AttActInTime, 108) as in_t FROM dbo.PayAttendance a LEFT JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID WHERE a.AttActInTime IS NOT NULL AND a.AttActOutTime IS NULL AND a.AttDate < DATEADD(day, -2, GETDATE()) {search_sql} ORDER BY a.AttID DESC"
            for r in execute_readonly_query(q):
                items.append(
                    AttendanceQualityIssueItem(
                        record_id=str(r["AttID"]),
                        entity_name=r["emp_name"] or "Unknown",
                        entity_type="PayAttendance",
                        context_info=r["d"],
                        issue_detail=f"Punch in ({r['in_t']}) recorded on {r['d']} but punch out is missing.",
                        status_detail="NO_PUNCH_OUT",
                    )
                )

        else:
            # Fallback mock for clean rules
            total = 0
            items = []

        return AttendanceQualityIssuesListResponse(
            issue_code=issue_code,
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    def export_attendance_quality_issues(self, issue_code: str, search: str | None = None) -> str:
        data = self.get_attendance_quality_issues(
            issue_code=issue_code, search=search, limit=10000, offset=0
        )
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["Record ID", "Entity Name", "Entity Type", "Context Info", "Issue Detail", "Status"]
        )
        for it in data.items:
            writer.writerow(
                [
                    it.record_id,
                    it.entity_name,
                    it.entity_type,
                    it.context_info or "",
                    it.issue_detail,
                    it.status_detail or "VIOLATION",
                ]
            )
        return output.getvalue()

    def get_attendance_org_hierarchy(self) -> AttendanceOrgHierarchyResponse:
        # 1. Company Level
        q_comp = """
        WITH ActiveEmps AS (
            SELECT
                e.EmpID,
                ISNULL(e.CompID, 1) as CompID
            FROM dbo.EmployeeMst e
            WHERE e.EmpIsActive = 1
              AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND e.EmpCode NOT LIKE '9%'
              AND ISNULL(e.EmpTypeID, 1) IN (1, 2)
        ),
        CompHeadcount AS (
            SELECT CompID, COUNT(*) as headcount
            FROM ActiveEmps
            GROUP BY CompID
        ),
        CompAttendance AS (
            SELECT
                ISNULL(a.AttCompID, 1) as CompID,
                COUNT(a.AttID) as total_attendance,
                SUM(CASE WHEN a.AttLeaveLabelID = 6 OR a.AttActInTime IS NOT NULL OR a.AttActOutTime IS NOT NULL THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN a.AttLateComeMins > 0 THEN 1 ELSE 0 END) as late_count,
                SUM(ISNULL(a.AttActOTMins, 0)) / 60.0 as total_ot_hours
            FROM dbo.PayAttendance a
            INNER JOIN ActiveEmps ae ON ae.EmpID = a.AttEmpID
            GROUP BY ISNULL(a.AttCompID, 1)
        )
        SELECT
            c.CompID as id,
            ISNULL(c.CompName, 'Unassigned Company') as name,
            c.CompCode as code,
            ISNULL(hc.headcount, 0) as headcount,
            ISNULL(att.total_attendance, 0) as total_attendance,
            ISNULL(att.present_count, 0) as present_count,
            ISNULL(att.late_count, 0) as late_count,
            ISNULL(att.total_ot_hours, 0.0) as total_ot_hours
        FROM dbo.OrgCompanyMst c
        LEFT JOIN CompHeadcount hc ON hc.CompID = c.CompID
        LEFT JOIN CompAttendance att ON att.CompID = c.CompID
        WHERE ISNULL(hc.headcount, 0) > 0 OR ISNULL(att.total_attendance, 0) > 0
        ORDER BY headcount DESC, total_attendance DESC;
        """
        comp_rows = execute_readonly_query(q_comp)
        companies: list[OrgHierarchyAttendanceNode] = []
        comp_dict: dict[int, OrgHierarchyAttendanceNode] = {}
        for r in comp_rows:
            cid = r["id"] or 0
            tot = r["total_attendance"] or 1
            hc = r["headcount"] or 1
            node = OrgHierarchyAttendanceNode(
                id=cid,
                name=r["name"],
                code=r["code"] or ("AIL" if cid == 1 else "ASCL" if cid == 2 else "OTH"),
                level="COMPANY",
                headcount=r["headcount"] or 0,
                total_attendance_records=r["total_attendance"] or 0,
                present_count=r["present_count"] or 0,
                present_pct=round(((r["present_count"] or 0) / tot) * 100.0, 1),
                late_count=r["late_count"] or 0,
                late_pct=round(((r["late_count"] or 0) / tot) * 100.0, 1),
                total_ot_hours=round(float(r["total_ot_hours"] or 0.0), 1),
                avg_ot_hours_per_emp=round(float(r["total_ot_hours"] or 0.0) / hc, 1),
                children=[],
            )
            companies.append(node)
            comp_dict[cid] = node

        # 2. Location / Plant Level
        q_loc = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID,
                o.LocID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND ISNULL(o.EmpOfficeDetIsDeleted, 0) = 0
        ),
        ActiveEmps AS (
            SELECT
                e.EmpID,
                ISNULL(e.CompID, 1) as CompID,
                ISNULL(co.LocID, 0) as LocID
            FROM dbo.EmployeeMst e
            LEFT JOIN CurrentOfficial co ON co.EmpID = e.EmpID AND co.rn = 1
            WHERE e.EmpIsActive = 1
              AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND e.EmpCode NOT LIKE '9%'
              AND ISNULL(e.EmpTypeID, 1) IN (1, 2)
        ),
        LocHeadcount AS (
            SELECT CompID, LocID, COUNT(*) as headcount
            FROM ActiveEmps
            GROUP BY CompID, LocID
        ),
        LocAttendance AS (
            SELECT
                ISNULL(a.AttCompID, 1) as CompID,
                ISNULL(a.AttBranchID, 0) as LocID,
                COUNT(a.AttID) as total_attendance,
                SUM(CASE WHEN a.AttLeaveLabelID = 6 OR a.AttActInTime IS NOT NULL OR a.AttActOutTime IS NOT NULL THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN a.AttLateComeMins > 0 THEN 1 ELSE 0 END) as late_count,
                SUM(ISNULL(a.AttActOTMins, 0)) / 60.0 as total_ot_hours
            FROM dbo.PayAttendance a
            INNER JOIN ActiveEmps ae ON ae.EmpID = a.AttEmpID
            GROUP BY ISNULL(a.AttCompID, 1), ISNULL(a.AttBranchID, 0)
        )
        SELECT
            ISNULL(l.LocID, 0) as id,
            ISNULL(hc.CompID, att.CompID) as comp_id,
            ISNULL(l.LocName, 'Default Location') as name,
            l.ShortName as code,
            ISNULL(hc.headcount, 0) as headcount,
            ISNULL(att.total_attendance, 0) as total_attendance,
            ISNULL(att.present_count, 0) as present_count,
            ISNULL(att.late_count, 0) as late_count,
            ISNULL(att.total_ot_hours, 0.0) as total_ot_hours
        FROM dbo.OrgLocationMst l
        LEFT JOIN LocHeadcount hc ON hc.LocID = l.LocID
        LEFT JOIN LocAttendance att ON att.LocID = l.LocID AND att.CompID = hc.CompID
        WHERE ISNULL(hc.headcount, 0) > 0 OR ISNULL(att.total_attendance, 0) > 0
        ORDER BY headcount DESC, total_attendance DESC;
        """
        loc_rows = execute_readonly_query(q_loc)
        locations: list[OrgHierarchyAttendanceNode] = []
        loc_dict: dict[int, OrgHierarchyAttendanceNode] = {}
        for r in loc_rows:
            lid = r["id"] or 0
            cid = r["comp_id"] or 1
            tot = r["total_attendance"] or 1
            hc = r["headcount"] or 1
            node = OrgHierarchyAttendanceNode(
                id=lid,
                name=r["name"],
                code=r["code"] or "SITE",
                level="LOCATION",
                headcount=r["headcount"] or 0,
                total_attendance_records=r["total_attendance"] or 0,
                present_count=r["present_count"] or 0,
                present_pct=round(((r["present_count"] or 0) / tot) * 100.0, 1),
                late_count=r["late_count"] or 0,
                late_pct=round(((r["late_count"] or 0) / tot) * 100.0, 1),
                total_ot_hours=round(float(r["total_ot_hours"] or 0.0), 1),
                avg_ot_hours_per_emp=round(float(r["total_ot_hours"] or 0.0) / hc, 1),
                children=[],
            )
            locations.append(node)
            loc_dict[lid] = node
            if cid in comp_dict:
                comp_dict[cid].children.append(node)

        # 3. Department Level Summary (Unique per DeptID - Active Employees Only via EmployeeOfficialDet)
        q_dept_summary = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID,
                o.DeptID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND ISNULL(o.EmpOfficeDetIsDeleted, 0) = 0
        ),
        ActiveEmps AS (
            SELECT
                e.EmpID,
                ISNULL(co.DeptID, 0) as DeptID
            FROM dbo.EmployeeMst e
            LEFT JOIN CurrentOfficial co ON co.EmpID = e.EmpID AND co.rn = 1
            WHERE e.EmpIsActive = 1
              AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND e.EmpCode NOT LIKE '9%'
              AND ISNULL(e.EmpTypeID, 1) IN (1, 2)
        ),
        DeptHeadcount AS (
            SELECT DeptID, COUNT(*) as headcount
            FROM ActiveEmps
            GROUP BY DeptID
        ),
        DeptAttendance AS (
            SELECT
                a.AttDeptID as DeptID,
                COUNT(a.AttID) as total_attendance,
                SUM(CASE WHEN a.AttLeaveLabelID = 6 OR a.AttActInTime IS NOT NULL OR a.AttActOutTime IS NOT NULL THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN a.AttLateComeMins > 0 THEN 1 ELSE 0 END) as late_count,
                SUM(ISNULL(a.AttActOTMins, 0)) / 60.0 as total_ot_hours
            FROM dbo.PayAttendance a
            INNER JOIN ActiveEmps ae ON ae.EmpID = a.AttEmpID
            GROUP BY a.AttDeptID
        )
        SELECT
            d.DeptID as id,
            ISNULL(d.DeptName, 'Unassigned Dept') as name,
            CAST(d.CosecDeptId AS VARCHAR) as code,
            ISNULL(hc.headcount, 0) as headcount,
            ISNULL(att.total_attendance, 0) as total_attendance,
            ISNULL(att.present_count, 0) as present_count,
            ISNULL(att.late_count, 0) as late_count,
            ISNULL(att.total_ot_hours, 0.0) as total_ot_hours
        FROM dbo.OrgDepartmentMst d
        LEFT JOIN DeptHeadcount hc ON hc.DeptID = d.DeptID
        LEFT JOIN DeptAttendance att ON att.DeptID = d.DeptID
        WHERE d.DeptIsActive = 1 AND ISNULL(d.DeptIsDeleted, 0) = 0 AND (ISNULL(hc.headcount, 0) > 0 OR ISNULL(att.total_attendance, 0) > 0)
        ORDER BY headcount DESC, total_attendance DESC;
        """
        dept_rows = execute_readonly_query(q_dept_summary)
        departments: list[OrgHierarchyAttendanceNode] = []
        for r in dept_rows:
            did = r["id"] or 0
            tot = r["total_attendance"] or 1
            hc = r["headcount"] or 1
            node = OrgHierarchyAttendanceNode(
                id=did,
                name=r["name"],
                code=r["code"] or f"DEP-{did}",
                level="DEPARTMENT",
                headcount=r["headcount"] or 0,
                total_attendance_records=r["total_attendance"] or 0,
                present_count=r["present_count"] or 0,
                present_pct=round(((r["present_count"] or 0) / tot) * 100.0, 1),
                late_count=r["late_count"] or 0,
                late_pct=round(((r["late_count"] or 0) / tot) * 100.0, 1),
                total_ot_hours=round(float(r["total_ot_hours"] or 0.0), 1),
                avg_ot_hours_per_emp=round(float(r["total_ot_hours"] or 0.0) / hc, 1),
                children=[],
            )
            departments.append(node)

        # 4. Location-Level Department Children
        q_dept_loc = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID,
                o.LocID,
                o.DeptID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND ISNULL(o.EmpOfficeDetIsDeleted, 0) = 0
        ),
        ActiveEmps AS (
            SELECT
                e.EmpID,
                ISNULL(co.LocID, 0) as LocID,
                ISNULL(co.DeptID, 0) as DeptID
            FROM dbo.EmployeeMst e
            LEFT JOIN CurrentOfficial co ON co.EmpID = e.EmpID AND co.rn = 1
            WHERE e.EmpIsActive = 1
              AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND e.EmpCode NOT LIKE '9%'
              AND ISNULL(e.EmpTypeID, 1) IN (1, 2)
        ),
        DeptLocHeadcount AS (
            SELECT LocID, DeptID, COUNT(*) as headcount
            FROM ActiveEmps
            GROUP BY LocID, DeptID
        ),
        DeptLocAttendance AS (
            SELECT
                ISNULL(a.AttBranchID, 0) as LocID,
                a.AttDeptID as DeptID,
                COUNT(a.AttID) as total_attendance,
                SUM(CASE WHEN a.AttLeaveLabelID = 6 OR a.AttActInTime IS NOT NULL OR a.AttActOutTime IS NOT NULL THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN a.AttLateComeMins > 0 THEN 1 ELSE 0 END) as late_count,
                SUM(ISNULL(a.AttActOTMins, 0)) / 60.0 as total_ot_hours
            FROM dbo.PayAttendance a
            INNER JOIN ActiveEmps ae ON ae.EmpID = a.AttEmpID
            GROUP BY ISNULL(a.AttBranchID, 0), a.AttDeptID
        )
        SELECT
            ISNULL(hc.LocID, att.LocID) as loc_id,
            d.DeptID as id,
            ISNULL(d.DeptName, 'Unassigned Dept') as name,
            CAST(d.CosecDeptId AS VARCHAR) as code,
            ISNULL(hc.headcount, 0) as headcount,
            ISNULL(att.total_attendance, 0) as total_attendance,
            ISNULL(att.present_count, 0) as present_count,
            ISNULL(att.late_count, 0) as late_count,
            ISNULL(att.total_ot_hours, 0.0) as total_ot_hours
        FROM dbo.OrgDepartmentMst d
        LEFT JOIN DeptLocHeadcount hc ON hc.DeptID = d.DeptID
        LEFT JOIN DeptLocAttendance att ON att.DeptID = d.DeptID AND att.LocID = hc.LocID
        WHERE ISNULL(hc.headcount, 0) > 0 OR ISNULL(att.total_attendance, 0) > 0
        ORDER BY headcount DESC, total_attendance DESC;
        """
        loc_dept_rows = execute_readonly_query(q_dept_loc)
        for r in loc_dept_rows:
            did = r["id"] or 0
            lid = r["loc_id"] or 0
            tot = r["total_attendance"] or 1
            hc = r["headcount"] or 1
            child_node = OrgHierarchyAttendanceNode(
                id=did,
                name=r["name"],
                code=r["code"] or f"DEP-{did}",
                level="DEPARTMENT",
                headcount=r["headcount"] or 0,
                total_attendance_records=r["total_attendance"] or 0,
                present_count=r["present_count"] or 0,
                present_pct=round(((r["present_count"] or 0) / tot) * 100.0, 1),
                late_count=r["late_count"] or 0,
                late_pct=round(((r["late_count"] or 0) / tot) * 100.0, 1),
                total_ot_hours=round(float(r["total_ot_hours"] or 0.0), 1),
                avg_ot_hours_per_emp=round(float(r["total_ot_hours"] or 0.0) / hc, 1),
                children=[],
            )
            if lid in loc_dict:
                loc_dict[lid].children.append(child_node)

        return AttendanceOrgHierarchyResponse(
            companies=companies,
            locations=locations,
            departments=departments,
            hierarchy_tree=companies,
        )

    def get_department_attendance_detail(self, dept_id: int) -> DepartmentDetailResponse:
        """Fetch summary KPIs and attendance/leave stats for a specific department (Active employees only)."""
        q_dept = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID,
                o.DeptID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND ISNULL(o.EmpOfficeDetIsDeleted, 0) = 0
        ),
        ActiveEmps AS (
            SELECT
                e.EmpID,
                ISNULL(co.DeptID, 0) as DeptID
            FROM dbo.EmployeeMst e
            LEFT JOIN CurrentOfficial co ON co.EmpID = e.EmpID AND co.rn = 1
            WHERE e.EmpIsActive = 1
              AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND e.EmpCode NOT LIKE '9%'
              AND ISNULL(e.EmpTypeID, 1) IN (1, 2)
        )
        SELECT
            d.DeptID as id,
            ISNULL(d.DeptName, 'Unassigned Department') as name,
            CAST(d.CosecDeptId AS VARCHAR) as code,
            (SELECT COUNT(*) FROM ActiveEmps WHERE DeptID = d.DeptID) as headcount,
            COUNT(a.AttID) as total_attendance,
            SUM(CASE WHEN a.AttLeaveLabelID = 6 OR a.AttActInTime IS NOT NULL OR a.AttActOutTime IS NOT NULL THEN 1 ELSE 0 END) as present_count,
            SUM(CASE WHEN a.AttLeaveLabelID = 7 OR (a.AttActInTime IS NULL AND a.AttActOutTime IS NULL AND ISNULL(a.AttLeaveLabelID, 0) NOT IN (6, 8, 10, 9)) THEN 1 ELSE 0 END) as absent_count,
            SUM(CASE WHEN a.AttLateComeMins > 0 THEN 1 ELSE 0 END) as late_count,
            SUM(ISNULL(a.AttActOTMins, 0)) / 60.0 as total_ot_hours
        FROM dbo.PayAttendance a
        INNER JOIN ActiveEmps ae ON ae.EmpID = a.AttEmpID AND ae.DeptID = :dept_id
        LEFT JOIN dbo.OrgDepartmentMst d ON d.DeptID = ae.DeptID
        WHERE ae.DeptID = :dept_id
        GROUP BY d.DeptID, d.DeptName, d.CosecDeptId;
        """
        rows = execute_readonly_query(q_dept, {"dept_id": dept_id})

        if not rows:
            q_fallback = """
            WITH CurrentOfficial AS (
                SELECT
                    o.EmpID,
                    o.DeptID,
                    ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
                FROM dbo.EmployeeOfficialDet o
                WHERE o.EmpOfficeDetIsActive = 1 AND ISNULL(o.EmpOfficeDetIsDeleted, 0) = 0
            ),
            ActiveEmps AS (
                SELECT
                    e.EmpID,
                    ISNULL(co.DeptID, 0) as DeptID
                FROM dbo.EmployeeMst e
                LEFT JOIN CurrentOfficial co ON co.EmpID = e.EmpID AND co.rn = 1
                WHERE e.EmpIsActive = 1
                  AND ISNULL(e.EmpIsDeleted, 0) = 0
                  AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
                  AND e.EmpCode NOT LIKE '9%'
                  AND ISNULL(e.EmpTypeID, 1) IN (1, 2)
            )
            SELECT
                d.DeptID as id,
                ISNULL(d.DeptName, 'Unassigned Department') as name,
                CAST(d.CosecDeptId AS VARCHAR) as code,
                (SELECT COUNT(*) FROM ActiveEmps WHERE DeptID = d.DeptID) as headcount
            FROM dbo.OrgDepartmentMst d
            WHERE d.DeptID = :dept_id;
            """
            fallback_rows = execute_readonly_query(q_fallback, {"dept_id": dept_id})
            dept_name = fallback_rows[0]["name"] if fallback_rows else f"Department #{dept_id}"
            dept_code = fallback_rows[0]["code"] if fallback_rows else f"DEP-{dept_id}"
            dept_hc = fallback_rows[0]["headcount"] if fallback_rows else 0
            return DepartmentDetailResponse(
                dept_id=dept_id,
                dept_name=dept_name,
                dept_code=dept_code,
                headcount=dept_hc,
                total_attendance_records=0,
                present_count=0,
                present_pct=0.0,
                absent_count=0,
                absent_pct=0.0,
                late_count=0,
                late_pct=0.0,
                total_ot_hours=0.0,
                avg_ot_hours_per_emp=0.0,
                active_leaves_count=0,
                pending_leaves_count=0,
            )

        r = rows[0]
        tot = r["total_attendance"] or 0
        hc_val = r["headcount"] or 0
        present_count = r["present_count"] or 0
        absent_count = r["absent_count"] or 0
        late_count = r["late_count"] or 0
        total_ot = float(r["total_ot_hours"] or 0.0)

        # Count active & pending leaves for active employees in this department
        q_leaves_count = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID,
                o.DeptID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND ISNULL(o.EmpOfficeDetIsDeleted, 0) = 0
        ),
        ActiveEmps AS (
            SELECT
                e.EmpID,
                ISNULL(co.DeptID, 0) as DeptID
            FROM dbo.EmployeeMst e
            LEFT JOIN CurrentOfficial co ON co.EmpID = e.EmpID AND co.rn = 1
            WHERE e.EmpIsActive = 1
              AND ISNULL(e.EmpIsDeleted, 0) = 0
              AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
              AND e.EmpCode NOT LIKE '9%'
              AND ISNULL(e.EmpTypeID, 1) IN (1, 2)
        )
        SELECT
            SUM(CASE WHEN lr.LeaveStatusID = 13 THEN 1 ELSE 0 END) as active_leaves,
            SUM(CASE WHEN lr.LeaveStatusID IN (1, 0, 14) THEN 1 ELSE 0 END) as pending_leaves
        FROM dbo.LeaveRequest lr
        INNER JOIN ActiveEmps ae ON ae.EmpID = lr.LeaveRequestByEmpID
        WHERE ae.DeptID = :dept_id;
        """
        leave_cnt_rows = execute_readonly_query(q_leaves_count, {"dept_id": dept_id})
        active_leaves = 0
        pending_leaves = 0
        if leave_cnt_rows:
            active_leaves = leave_cnt_rows[0]["active_leaves"] or 0
            pending_leaves = leave_cnt_rows[0]["pending_leaves"] or 0

        return DepartmentDetailResponse(
            dept_id=dept_id,
            dept_name=r["name"] or f"Department #{dept_id}",
            dept_code=r["code"] or f"DEP-{dept_id}",
            headcount=hc_val,
            total_attendance_records=tot,
            present_count=present_count,
            present_pct=round((present_count / tot) * 100.0, 1) if tot > 0 else 0.0,
            absent_count=absent_count,
            absent_pct=round((absent_count / tot) * 100.0, 1) if tot > 0 else 0.0,
            late_count=late_count,
            late_pct=round((late_count / tot) * 100.0, 1) if tot > 0 else 0.0,
            total_ot_hours=round(total_ot, 1),
            avg_ot_hours_per_emp=round(total_ot / hc_val, 1) if hc_val > 0 else 0.0,
            active_leaves_count=active_leaves,
            pending_leaves_count=pending_leaves,
        )

    def get_employee_lifetime_attendance_analytics(
        self, emp_id: int
    ) -> EmployeeLifetimeAttendanceResponse:
        """Exhaustive 360-degree lifetime attendance, biometric, leave, and HR analytics for a specific employee."""
        q_emp = """
        SELECT
            e.EmpID,
            e.EmpCode,
            CONCAT(e.EmpFirstName, ' ', e.EmpLastName) as emp_name,
            CONVERT(varchar(10), e.EmpJoinDate, 120) as join_date,
            d.DeptName as dept_name,
            l.LocName as loc_name,
            e.EmpIsActive,
            e.EmpIsDeleted
        FROM dbo.EmployeeMst e
        LEFT JOIN dbo.EmployeeOfficialDet co
            ON co.EmpID = e.EmpID
            AND co.EmpOfficeDetIsActive = 1
            AND ISNULL(co.EmpOfficeDetIsDeleted, 0) = 0
        LEFT JOIN dbo.OrgDepartmentMst d ON d.DeptID = co.DeptID
        LEFT JOIN dbo.OrgLocationMst l ON l.LocID = co.LocID
        WHERE e.EmpID = :emp_id;
        """
        emp_rows = execute_readonly_query(q_emp, {"emp_id": emp_id})
        if not emp_rows:
            return EmployeeLifetimeAttendanceResponse(
                emp_id=emp_id,
                emp_code=f"EMP-{emp_id}",
                emp_name=f"Employee #{emp_id}",
                join_date=None,
                tenure_days=0,
                tenure_label="N/A",
                dept_name="Unassigned",
                loc_name="Unassigned",
                is_active=False,
            )

        e_row = emp_rows[0]
        join_dt_str = e_row["join_date"]
        tenure_days = 0
        tenure_label = "N/A"
        if join_dt_str:
            try:
                j_dt = datetime.strptime(join_dt_str, "%Y-%m-%d")
                tenure_days = (datetime.now() - j_dt).days
                years = tenure_days // 365
                months = (tenure_days % 365) // 30
                tenure_label = f"{years}y {months}m ({tenure_days} days)"
            except Exception:
                tenure_label = "N/A"

        # 2. Lifetime Attendance Totals
        # NOTE: This DB uses a single AttSalType='SAL' for all records.
        # We determine actual status from biometric punches and day-of-week:
        q_att = """
        SELECT
            COUNT(*) as total_attendance_records,
            SUM(CASE WHEN e.EmpJoinDate IS NOT NULL AND a.AttDate < e.EmpJoinDate THEN 1 ELSE 0 END) as pre_joining_days,
            SUM(CASE WHEN (e.EmpJoinDate IS NULL OR a.AttDate >= e.EmpJoinDate) THEN 1 ELSE 0 END) as post_joining_days,
            SUM(CASE WHEN a.AttActInTime IS NOT NULL THEN 1 ELSE 0 END) as present_days,
            SUM(CASE WHEN a.AttActInTime IS NULL
                      AND (e.EmpJoinDate IS NULL OR a.AttDate >= e.EmpJoinDate)
                      AND DATEPART(WEEKDAY, a.AttDate) NOT IN (1, 7)
                      AND h.OffsID IS NULL
                      THEN 1 ELSE 0 END) as absent_days,
            SUM(CASE WHEN a.AttSalType IN ('HD', 'HALF') THEN 1 ELSE 0 END) as half_days,
            0 as leave_days,
            SUM(CASE WHEN a.AttActInTime IS NULL
                      AND (e.EmpJoinDate IS NULL OR a.AttDate >= e.EmpJoinDate)
                      AND DATEPART(WEEKDAY, a.AttDate) IN (1, 7)
                      THEN 1 ELSE 0 END) as weekly_offs,
            SUM(CASE WHEN a.AttActInTime IS NULL
                      AND (e.EmpJoinDate IS NULL OR a.AttDate >= e.EmpJoinDate)
                      AND DATEPART(WEEKDAY, a.AttDate) NOT IN (1, 7)
                      AND h.OffsID IS NOT NULL
                      THEN 1 ELSE 0 END) as paid_holidays,
            SUM(CASE WHEN a.AttLateComeMins > 0 THEN 1 ELSE 0 END) as late_arrivals_count,
            SUM(ISNULL(a.AttLateComeMins, 0)) as total_late_mins,
            SUM(CASE WHEN a.AttEarlyGoneMins > 0 THEN 1 ELSE 0 END) as early_exits_count,
            SUM(ISNULL(a.AttEarlyGoneMins, 0)) as total_early_mins,
            SUM(CASE WHEN a.AttActOTMins > 0 THEN 1 ELSE 0 END) as overtime_records_count,
            SUM(ISNULL(a.AttActOTMins, 0)) / 60.0 as total_ot_hours,
            SUM(CASE WHEN a.AttActInTime IS NOT NULL AND a.AttActOutTime IS NULL THEN 1 ELSE 0 END) as missing_punch_outs,
            SUM(CASE WHEN a.AttActInTime IS NULL AND a.AttActOutTime IS NOT NULL THEN 1 ELSE 0 END) as missing_punch_ins,
            SUM(CASE WHEN a.AttActInTime IS NULL AND a.AttActOutTime IS NULL
                      AND DATEPART(WEEKDAY, a.AttDate) NOT IN (1, 7)
                      AND h.OffsID IS NULL
                      AND (e.EmpJoinDate IS NULL OR a.AttDate >= e.EmpJoinDate)
                      THEN 1 ELSE 0 END) as unpunched_salary_days
        FROM dbo.PayAttendance a
        INNER JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID
        LEFT JOIN dbo.PayCompanyOffsDet h
            ON h.OffsCompID = e.CompID
            AND CAST(h.OffsDate AS DATE) = CAST(a.AttDate AS DATE)
        WHERE a.AttEmpID = :emp_id;
        """
        att_rows = execute_readonly_query(q_att, {"emp_id": emp_id})
        att_tot = att_rows[0] if att_rows else {}

        present_cnt = att_tot.get("present_days") or 0
        absent_cnt = att_tot.get("absent_days") or 0
        late_cnt = att_tot.get("late_arrivals_count") or 0

        # 3. Unauthorized Absence Calculation
        # Only count weekday (Mon-Fri) unpunched days after joining,
        # excluding company holidays from PayCompanyOffsDet.
        q_unauth = """
        SELECT
            COUNT(CASE WHEN lr.LeaveRequestID IS NULL THEN 1 END) as unauthorized_absence_days,
            COUNT(CASE WHEN lr.LeaveRequestID IS NOT NULL THEN 1 END) as leave_covered_absence_days
        FROM dbo.PayAttendance a
        INNER JOIN dbo.EmployeeMst e ON e.EmpID = a.AttEmpID
        LEFT JOIN dbo.PayCompanyOffsDet h
            ON h.OffsCompID = e.CompID
            AND CAST(h.OffsDate AS DATE) = CAST(a.AttDate AS DATE)
        LEFT JOIN dbo.LeaveRequest lr ON lr.LeaveRequestByEmpID = a.AttEmpID
            AND CAST(a.AttDate AS DATE) BETWEEN CAST(lr.LeaveRequestFromDate AS DATE) AND CAST(lr.LeaveRequestToDate AS DATE)
            AND ISNULL(lr.LeaveRequestIsDeleted, 0) = 0
            AND lr.LeaveStatusID = 13
        WHERE a.AttEmpID = :emp_id
            AND a.AttActInTime IS NULL
            AND DATEPART(WEEKDAY, a.AttDate) NOT IN (1, 7)
            AND h.OffsID IS NULL
            AND (e.EmpJoinDate IS NULL OR a.AttDate >= e.EmpJoinDate);
        """
        unauth_rows = execute_readonly_query(q_unauth, {"emp_id": emp_id})
        unauth_data = unauth_rows[0] if unauth_rows else {}
        unauth_cnt = unauth_data.get("unauthorized_absence_days") or 0
        leave_covered_cnt = unauth_data.get("leave_covered_absence_days") or 0
        post_joining_cnt = att_tot.get("post_joining_days") or 0
        weekly_offs_cnt = att_tot.get("weekly_offs") or 0
        paid_holidays_cnt = att_tot.get("paid_holidays") or 0
        working_days = max(post_joining_cnt - weekly_offs_cnt - paid_holidays_cnt, 0)
        working_denom = max(working_days, present_cnt, 1)
        unauth_pct = round((unauth_cnt / working_denom) * 100.0, 1)

        absconding_risk = "LOW"
        if unauth_pct > 15.0:
            absconding_risk = "CRITICAL"
        elif unauth_pct > 8.0:
            absconding_risk = "HIGH"
        elif unauth_pct > 3.0:
            absconding_risk = "MEDIUM"

        # 4. Leaves Breakdown by Type
        # Combines monthly payroll leave balance ledger (dbo.PayMonthlyLeaveBalance) with formal online requests (dbo.LeaveRequest)
        q_bal = """
        SELECT
            SUM(COALESCE(AvailedPL, 0)) as PL,
            SUM(COALESCE(AvailedCL, 0)) as CL,
            SUM(COALESCE(AvailedSL, 0)) as SL,
            SUM(COALESCE(AvailedCO, 0)) as CO
        FROM dbo.PayMonthlyLeaveBalance
        WHERE EmpID = :emp_id;
        """
        bal_rows = execute_readonly_query(q_bal, {"emp_id": emp_id})
        bal = bal_rows[0] if bal_rows else {"PL": 0, "CL": 0, "SL": 0, "CO": 0}

        q_req = """
        SELECT
            COALESCE(lt.LeaveTypeShortName, 'PL') as leave_code,
            COUNT(lr.LeaveRequestID) as request_count,
            SUM(COALESCE(lr.LeaveDays, 0)) as total_days_taken,
            CONVERT(VARCHAR(10), MAX(lr.LeaveRequestToDate), 120) as last_availed_date
        FROM dbo.LeaveRequest lr
        LEFT JOIN dbo.LeaveTypeMst lt ON lt.LeaveTypeID = lr.LeaveTypeID
        WHERE lr.LeaveRequestByEmpID = :emp_id AND lr.LeaveStatusID = 13
        GROUP BY lt.LeaveTypeShortName;
        """
        req_rows = execute_readonly_query(q_req, {"emp_id": emp_id})
        req_map = {(r["leave_code"] or "PL").strip(): r for r in req_rows}

        cat_definitions = [
            ("PL", "Privilege/Paid Leave"),
            ("CL", "Casual Leave"),
            ("SL", "Sick/Medical Leave"),
            ("CO", "Comp Off/Special"),
        ]

        tot_bal_days = sum(float(bal.get(c[0]) or 0) for c in cat_definitions)
        tot_req_days = sum(float(r.get("total_days_taken") or 0) for r in req_rows)
        grand_total_leave_denom = max(tot_bal_days, tot_req_days, 1.0)

        leaves_breakdown = []
        for code, desc in cat_definitions:
            bal_days = float(bal.get(code) or 0.0)
            req_item = req_map.get(code, {})
            req_days = float(req_item.get("total_days_taken") or 0.0)
            final_days = max(bal_days, req_days)

            req_cnt = int(req_item.get("request_count") or (1 if final_days > 0 else 0))
            last_date = req_item.get("last_availed_date")

            avg_days = round(final_days / max(req_cnt, 1), 1) if req_cnt > 0 else 0.0
            share_pct = round((final_days / grand_total_leave_denom) * 100.0, 1)

            leaves_breakdown.append(
                EmployeeLifetimeLeaveTypeBreakdown(
                    leave_type=desc,
                    leave_code=code if code != "CO" else "CO/ML",
                    request_count=req_cnt,
                    total_days_taken=final_days,
                    avg_days_per_request=avg_days,
                    share_pct=share_pct,
                    last_availed_date=last_date,
                )
            )

        # 5. Generate Data Quality & HR Risk Signals
        risk_signals = []
        if unauth_cnt > 0:
            risk_signals.append(
                f"Unauthorized Absences without Leave Application ({unauth_cnt} days)"
            )
        if late_cnt > 20:
            risk_signals.append(f"High Late Arrival Frequency ({late_cnt} instances)")
        if absent_cnt > 10:
            risk_signals.append(f"High Absenteeism Risk ({absent_cnt} absent days)")
        if (att_tot.get("missing_punch_outs") or 0) > 5:
            risk_signals.append(
                f"Frequent Unclosed Punch-Outs ({att_tot.get('missing_punch_outs')} missing outs)"
            )
        if (att_tot.get("unpunched_salary_days") or 0) > 30:
            risk_signals.append(
                f"High Manual Salary Credit Volume without Biometric Swipes ({att_tot.get('unpunched_salary_days')} days)"
            )

        return EmployeeLifetimeAttendanceResponse(
            emp_id=emp_id,
            emp_code=e_row["EmpCode"] or f"EMP-{emp_id}",
            emp_name=e_row["emp_name"] or f"Employee #{emp_id}",
            join_date=join_dt_str,
            tenure_days=tenure_days,
            tenure_label=tenure_label,
            dept_name=e_row["dept_name"] or "Unassigned Department",
            loc_name=e_row["loc_name"] or "Corporate Location",
            is_active=bool(e_row["EmpIsActive"]),
            total_attendance_records=att_tot.get("total_attendance_records") or 0,
            present_days=present_cnt,
            present_pct=min(100.0, round((present_cnt / working_denom) * 100.0, 1)),
            absent_days=absent_cnt,
            absent_pct=min(100.0, round((absent_cnt / working_denom) * 100.0, 1)),
            half_days=att_tot.get("half_days") or 0,
            leave_days=leave_covered_cnt,
            weekly_offs=weekly_offs_cnt,
            paid_holidays=paid_holidays_cnt,
            late_arrivals_count=late_cnt,
            total_late_mins=att_tot.get("total_late_mins") or 0,
            early_exits_count=att_tot.get("early_exits_count") or 0,
            total_early_mins=att_tot.get("total_early_mins") or 0,
            overtime_records_count=att_tot.get("overtime_records_count") or 0,
            total_ot_hours=round(float(att_tot.get("total_ot_hours") or 0.0), 1),
            missing_punch_outs=att_tot.get("missing_punch_outs") or 0,
            missing_punch_ins=att_tot.get("missing_punch_ins") or 0,
            unpunched_salary_days=att_tot.get("unpunched_salary_days") or 0,
            unauthorized_absence_days=unauth_cnt,
            leave_covered_absence_days=leave_covered_cnt,
            unauthorized_absence_pct=unauth_pct,
            absconding_risk_level=absconding_risk,
            leaves_breakdown=leaves_breakdown,
            risk_signals=risk_signals,
        )
