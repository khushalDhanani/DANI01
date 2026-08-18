from unittest.mock import MagicMock, patch

from app.modules.attendance.analyzer import AttendanceAnalyzer
from app.modules.attendance.schemas import (
    AttendanceDataQualityResponse,
    AttendanceDirectoryResponse,
    AttendanceLogItem,
    AttendanceMetrics,
    AttendanceOverviewResponse,
    AttendanceQualityRuleResult,
    LeaveApplicationItem,
    LeaveApplicationsListResponse,
    LeaveBalanceItem,
    LeaveBalancesListResponse,
    LeaveOverviewResponse,
    PunchMetrics,
    ShiftDistributionItem,
)
from app.modules.attendance.service import AttendanceService
from app.modules.definitions.attendance import AttendanceModuleDefinition
from app.modules.employee.schemas import IssueSeverity


def test_attendance_module_definition():
    assert AttendanceModuleDefinition.code == "ATTENDANCE"
    assert AttendanceModuleDefinition.name == "Attendance & Leave Analysis"
    assert len(AttendanceModuleDefinition.tables) >= 5
    assert len(AttendanceModuleDefinition.relationships) >= 3


def test_attendance_schemas():
    overview = AttendanceOverviewResponse(
        attendance_metrics=AttendanceMetrics(
            total_attendance_records=1000,
            employees_with_attendance=150,
            present_days=800,
            present_pct=80.0,
            absent_days=100,
            absent_pct=10.0,
            half_days=20,
            half_days_pct=2.0,
            leave_days=50,
            leave_days_pct=5.0,
            weekly_offs=20,
            paid_holidays=10,
        ),
        punch_metrics=PunchMetrics(
            total_punches_logged=2000,
            valid_punch_pairs=950,
            missing_punch_out_count=30,
            missing_punch_in_count=20,
            late_arrivals_count=45,
            early_departures_count=15,
            overtime_records_count=80,
            total_overtime_hours=120.5,
        ),
        shift_distribution=[
            ShiftDistributionItem(
                shift_id=1,
                shift_code="SH-1",
                shift_description="General Day Shift",
                from_time="09:00:00",
                to_time="18:00:00",
                assigned_attendance_count=900,
                percentage=90.0,
            )
        ],
    )
    assert overview.attendance_metrics.present_pct == 80.0
    assert overview.punch_metrics.total_overtime_hours == 120.5

    dir_resp = AttendanceDirectoryResponse(
        total=1,
        limit=20,
        offset=0,
        items=[
            AttendanceLogItem(
                att_id=101,
                emp_id=5,
                emp_code="EMP005",
                emp_name="John Doe",
                att_date="2026-08-15",
                att_sal_type="P",
                status_label="Present",
                in_time="09:02:15",
                out_time="18:05:00",
                shift_code="GS",
                shift_desc="General Shift",
                late_mins=2,
                early_mins=0,
                ot_mins=0,
                emp_status="ACTIVE",
            )
        ],
    )
    assert dir_resp.total == 1
    assert dir_resp.items[0].emp_name == "John Doe"

    leave_resp = LeaveOverviewResponse(
        total_leave_requests=50,
        approved_requests=40,
        approved_pct=80.0,
        pending_requests=5,
        pending_pct=10.0,
        rejected_requests=3,
        rejected_pct=6.0,
        cancelled_requests=2,
        cancelled_pct=4.0,
        active_employees_on_leave=12,
        total_employees_with_leave_balance=150,
        leave_type_distribution=[{"leave_type": "Privilege Leave", "request_count": 30}],
    )
    assert leave_resp.approved_requests == 40

    leave_app_resp = LeaveApplicationsListResponse(
        total=1,
        limit=20,
        offset=0,
        items=[
            LeaveApplicationItem(
                leave_request_id=501,
                emp_id=5,
                emp_code="EMP005",
                emp_name="John Doe",
                request_date="2026-08-10",
                from_date="2026-08-15",
                to_date="2026-08-17",
                leave_type_code="PL",
                leave_type_desc="Privilege Leave",
                leave_days=3.0,
                approve_days=3.0,
                status_id=13,
                status_desc="Approved",
                is_cancelled=False,
                reason="Family Event",
            )
        ],
    )
    assert leave_app_resp.items[0].status_desc == "Approved"

    leave_bal_resp = LeaveBalancesListResponse(
        total=1,
        limit=20,
        offset=0,
        items=[
            LeaveBalanceItem(
                bal_id=901,
                emp_id=5,
                emp_code="EMP005",
                emp_name="John Doe",
                year_month="202607",
                total_present=22.0,
                total_absent=0.0,
                op_pl=10.0,
                earned_pl=1.5,
                availed_pl=2.0,
                encashed_pl=0.0,
                net_pl_bal=9.5,
                op_cl=5.0,
                earned_cl=1.0,
                availed_cl=0.0,
                net_cl_bal=6.0,
                op_sl=5.0,
                earned_sl=1.0,
                availed_sl=0.0,
                net_sl_bal=6.0,
            )
        ],
    )
    assert leave_bal_resp.items[0].net_pl_bal == 9.5

    quality_resp = AttendanceDataQualityResponse(
        overall_health_score=94.0,
        critical_issues_count=0,
        warning_issues_count=2,
        info_issues_count=1,
        rules=[
            AttendanceQualityRuleResult(
                rule_code="PUNCH_OUT_BEFORE_IN",
                rule_name="Punch Out Timestamp Earlier Than Punch In",
                severity=IssueSeverity.WARNING,
                description="Invalid timestamp sequence",
                issue_count=2,
                impact="Negative work duration",
                recommendation="Fix timestamps",
            )
        ],
        summary_by_severity={"CRITICAL": 0, "WARNING": 2, "INFO": 1},
    )
    assert quality_resp.overall_health_score == 94.0


@patch("app.modules.attendance.service.execute_readonly_query")
def test_attendance_service_overview(mock_query):
    mock_query.side_effect = [
        [
            {
                "total_records": 100,
                "total_emps": 10,
                "present_days": 80,
                "absent_days": 10,
                "half_days": 2,
                "leave_days": 5,
                "weekly_offs": 2,
                "paid_holidays": 1,
            }
        ],
        [
            {
                "total_punches": 200,
                "valid_pairs": 90,
                "missing_out": 5,
                "missing_in": 2,
                "late_arrivals": 10,
                "early_departures": 3,
                "ot_records": 8,
                "total_ot_hours": 16.0,
            }
        ],
        [
            {
                "ShiftID": 1,
                "ShiftCode": "GS",
                "ShiftDescription": "General Shift",
                "FromTime": "09:00:00",
                "ToTime": "18:00:00",
                "assigned_cnt": 90,
            }
        ],
    ]

    service = AttendanceService()
    res = service.get_attendance_overview()
    assert res.attendance_metrics.total_attendance_records == 100
    assert res.attendance_metrics.present_pct == 80.0
    assert res.punch_metrics.total_overtime_hours == 16.0
    assert len(res.shift_distribution) == 1


@patch("app.modules.attendance.service.execute_readonly_query")
def test_attendance_service_directory(mock_query):
    item_row = {
        "AttID": 1001,
        "AttEmpID": 5,
        "EmpCode": "E5",
        "emp_name": "Jane Smith",
        "att_date": "2026-08-15",
        "AttSalType": "P",
        "in_time": "09:00:00",
        "out_time": "18:00:00",
        "off_in_time": "09:00:00",
        "off_out_time": "18:00:00",
        "ShiftCode": "GS",
        "ShiftDescription": "General Shift",
        "late_mins": 0,
        "early_mins": 0,
        "ot_mins": 0,
        "emp_status": "ACTIVE",
    }
    mock_query.side_effect = [
        [{"total": 1}],
        [item_row],
        [{"total": 1}],
        [item_row],
    ]

    service = AttendanceService()
    res = service.get_attendance_directory(status_filter="PRESENT", limit=10, offset=0)
    assert res.total == 1
    assert res.items[0].emp_name == "Jane Smith"

    csv_data = service.export_attendance_directory(status_filter="PRESENT")
    assert "Jane Smith" in csv_data


@patch("app.modules.attendance.service.execute_readonly_query")
def test_attendance_service_leave_applications(mock_query):
    app_row = {
        "LeaveRequestID": 5001,
        "LeaveRequestByEmpID": 5,
        "EmpCode": "E5",
        "emp_name": "Jane Smith",
        "req_date": "2026-08-10",
        "from_date": "2026-08-15",
        "to_date": "2026-08-17",
        "LeaveTypeShortName": "PL",
        "LeaveTypeDesc": "Privilege Leave",
        "leave_days": 3.0,
        "LeaveApproveDays": 3.0,
        "LeaveStatusID": 13,
        "is_cancelled": 0,
        "LeaveReason": "Vacation",
    }
    mock_query.side_effect = [
        [{"total": 1}],
        [app_row],
        [{"total": 1}],
        [app_row],
    ]

    service = AttendanceService()
    res = service.get_leave_applications(status_filter="APPROVED", search="Jane")
    assert res.total == 1
    assert res.items[0].status_desc == "Approved"

    csv_data = service.export_leave_applications(status_filter="APPROVED")
    assert "Jane Smith" in csv_data


@patch("app.modules.attendance.service.execute_readonly_query")
def test_attendance_service_leave_balances(mock_query):
    bal_row = {
        "BalID": 9001,
        "EmpID": 5,
        "EmpCode": "E5",
        "emp_name": "Jane Smith",
        "YearMonth": "202607",
        "total_present": 22.0,
        "total_absent": 0.0,
        "op_pl": 10.0,
        "earned_pl": 1.5,
        "availed_pl": 2.0,
        "encashed_pl": 0.0,
        "op_cl": 5.0,
        "earned_cl": 1.0,
        "availed_cl": 0.0,
        "op_sl": 5.0,
        "earned_sl": 1.0,
        "availed_sl": 0.0,
    }
    mock_query.side_effect = [
        [{"total": 1}],
        [bal_row],
    ]

    service = AttendanceService()
    res = service.get_leave_balances(year_month="202607")
    assert res.total == 1
    assert res.items[0].net_pl_bal == 9.5


@patch("app.modules.attendance.service.execute_readonly_query")
def test_attendance_service_leave_overview(mock_query):
    mock_query.side_effect = [
        [
            {
                "total_requests": 20,
                "approved_cnt": 15,
                "pending_cnt": 3,
                "rejected_cnt": 1,
                "cancelled_cnt": 1,
            }
        ],
        [{"active_on_leave": 2}],
        [{"total_bal_emps": 50}],
        [{"LeaveTypeDesc": "Privilege Leave", "LeaveTypeShortName": "PL", "req_cnt": 15}],
    ]

    service = AttendanceService()
    res = service.get_leave_overview()
    assert res.total_leave_requests == 20
    assert res.approved_requests == 15
    assert res.active_employees_on_leave == 2


@patch("app.modules.attendance.service.execute_readonly_query")
def test_attendance_service_quality(mock_query):
    mock_query.return_value = [
        {
            "orphan_att_emp": 0,
            "orphan_leave_emp": 0,
            "invalid_leave_dates": 0,
            "negative_calculated_leave_balances": 0,
            "recent_att_inactive_emp": 0,
            "dup_att_emp_date": 0,
            "punch_out_before_in": 1,
            "missing_punch_out": 0,
            "missing_punch_in": 0,
            "orphan_att_shift": 0,
            "orphan_leave_type": 0,
            "overlapping_leave_requests": 0,
            "historical_att_inactive": 5,
            "leave_without_reason": 0,
        }
    ]

    service = AttendanceService()
    res = service.get_attendance_quality()
    assert res.overall_health_score == 98.0
    assert res.summary_by_severity["WARNING"] == 1


@patch("app.modules.attendance.service.execute_readonly_query")
def test_attendance_service_quality_issues(mock_query):
    mock_query.side_effect = [
        [{"t": 1}],
        [{"AttID": 101, "AttEmpID": 999, "d": "2026-08-15"}],
        [{"t": 1}],
        [{"AttID": 101, "AttEmpID": 999, "d": "2026-08-15"}],
        [{"t": 1}],
        [{"LeaveRequestID": 501, "LeaveRequestByEmpID": 999, "d": "2026-08-15"}],
        [{"t": 1}],
        [{"LeaveRequestID": 502, "emp_name": "Jane", "f": "2026-08-15", "t": "2026-08-10"}],
        [{"t": 1}],
        [{"BalID": 701, "YearMonth": "202607", "emp_name": "Jane", "net_pl": -2.0, "net_cl": 0.0}],
        [{"t": 1}],
        [{"AttID": 102, "emp_name": "Jane", "d": "2026-08-15"}],
        [{"t": 1}],
        [
            {
                "AttID": 103,
                "emp_name": "Jane",
                "d": "2026-08-15",
                "in_t": "09:00:00",
                "out_t": "08:00:00",
            }
        ],
        [{"t": 1}],
        [{"AttID": 104, "emp_name": "Jane", "d": "2026-08-15", "in_t": "09:00:00"}],
    ]

    service = AttendanceService()
    issues = service.get_attendance_quality_issues("ORPHAN_ATTENDANCE_EMP", search="101")
    assert issues.total == 1
    assert issues.items[0].record_id == "101"

    csv_data = service.export_attendance_quality_issues("ORPHAN_ATTENDANCE_EMP", search="101")
    assert "ORPHAN_EMP" in csv_data

    # Test other branch issues
    assert service.get_attendance_quality_issues("ORPHAN_LEAVE_EMP").total == 1
    assert service.get_attendance_quality_issues("IMPOSSIBLE_LEAVE_DATES").total == 1
    assert service.get_attendance_quality_issues("CORRUPTED_LEAVE_BALANCE").total == 1
    assert service.get_attendance_quality_issues("ACTIVE_ATTENDANCE_DELETED_EMP").total == 1
    assert service.get_attendance_quality_issues("PUNCH_OUT_BEFORE_IN").total == 1
    assert service.get_attendance_quality_issues("MISSING_PUNCH_OUT").total == 1
    assert service.get_attendance_quality_issues("UNKNOWN_RULE").total == 0


def test_attendance_analyzer():
    mock_service = MagicMock()
    mock_service.get_attendance_overview.return_value = AttendanceOverviewResponse(
        attendance_metrics=AttendanceMetrics(
            total_attendance_records=1,
            employees_with_attendance=1,
            present_days=1,
            present_pct=100.0,
            absent_days=0,
            absent_pct=0.0,
            half_days=0,
            half_days_pct=0.0,
            leave_days=0,
            leave_days_pct=0.0,
            weekly_offs=0,
            paid_holidays=0,
        ),
        punch_metrics=PunchMetrics(
            total_punches_logged=1,
            valid_punch_pairs=1,
            missing_punch_out_count=0,
            missing_punch_in_count=0,
            late_arrivals_count=0,
            early_departures_count=0,
            overtime_records_count=0,
            total_overtime_hours=0.0,
        ),
        shift_distribution=[],
    )
    mock_service.get_leave_overview.return_value = LeaveOverviewResponse(
        total_leave_requests=0,
        approved_requests=0,
        approved_pct=0.0,
        pending_requests=0,
        pending_pct=0.0,
        rejected_requests=0,
        rejected_pct=0.0,
        cancelled_requests=0,
        cancelled_pct=0.0,
        active_employees_on_leave=0,
        total_employees_with_leave_balance=0,
        leave_type_distribution=[],
    )
    mock_service.get_attendance_quality.return_value = AttendanceDataQualityResponse(
        overall_health_score=100.0,
        critical_issues_count=0,
        warning_issues_count=0,
        info_issues_count=0,
        rules=[],
        summary_by_severity={"CRITICAL": 0, "WARNING": 0, "INFO": 0},
    )

    analyzer = AttendanceAnalyzer(service=mock_service)
    analysis = analyzer.run_analysis()
    assert analysis["status"] == "COMPLETED"
    assert analysis["quality"]["overall_health_score"] == 100.0


@patch("app.modules.attendance.service.execute_readonly_query")
def test_attendance_org_hierarchy_service(mock_exec):
    mock_exec.side_effect = [
        # Comp
        [
            {
                "id": 1,
                "name": "Aether Industries Limited",
                "code": "AIL",
                "headcount": 100,
                "total_attendance": 5000,
                "present_count": 4500,
                "late_count": 500,
                "total_ot_hours": 1000.0,
            }
        ],
        # Loc
        [
            {
                "comp_id": 1,
                "id": 2,
                "name": "Genesis",
                "code": "Site 2",
                "headcount": 60,
                "total_attendance": 3000,
                "present_count": 2700,
                "late_count": 300,
                "total_ot_hours": 600.0,
            }
        ],
        # Dept Summary
        [
            {
                "id": 3,
                "name": "Production Team",
                "code": "3",
                "headcount": 40,
                "total_attendance": 2000,
                "present_count": 1800,
                "late_count": 200,
                "total_ot_hours": 400.0,
            }
        ],
        # Loc Dept Children
        [
            {
                "loc_id": 2,
                "id": 3,
                "name": "Production Team",
                "code": "3",
                "headcount": 40,
                "total_attendance": 2000,
                "present_count": 1800,
                "late_count": 200,
                "total_ot_hours": 400.0,
            }
        ],
    ]

    service = AttendanceService()
    resp = service.get_attendance_org_hierarchy()
    assert len(resp.companies) == 1
    assert len(resp.locations) == 1
    assert len(resp.departments) == 1
    assert resp.companies[0].name == "Aether Industries Limited"
    assert resp.companies[0].children[0].name == "Genesis"
    assert resp.companies[0].children[0].children[0].name == "Production Team"


@patch("app.modules.attendance.service.execute_readonly_query")
def test_get_department_attendance_detail(mock_exec):
    mock_exec.side_effect = [
        # q_dept
        [
            {
                "id": 3,
                "name": "Production Team",
                "code": "PROD",
                "headcount": 50,
                "total_attendance": 2000,
                "present_count": 1800,
                "absent_count": 100,
                "late_count": 150,
                "total_ot_hours": 300.0,
            }
        ],
        # q_leaves_count
        [
            {
                "active_leaves": 12,
                "pending_leaves": 3,
            }
        ],
    ]

    service = AttendanceService()
    resp = service.get_department_attendance_detail(3)
    assert resp.dept_id == 3
    assert resp.dept_name == "Production Team"
    assert resp.headcount == 50
    assert resp.present_pct == 90.0
    assert resp.absent_pct == 5.0
    assert resp.active_leaves_count == 12
    assert resp.pending_leaves_count == 3


@patch("app.modules.attendance.service.execute_readonly_query")
def test_get_employee_lifetime_attendance_analytics(mock_exec):
    mock_exec.side_effect = [
        # q_emp
        [
            {
                "EmpID": 1273,
                "EmpCode": "2170",
                "emp_name": "Arbind Sahu",
                "join_date": "2021-03-22",
                "dept_name": "Research & Development Team",
                "loc_name": "Catalyst",
                "EmpIsActive": True,
                "EmpIsDeleted": False,
            }
        ],
        # q_att
        [
            {
                "total_attendance_records": 100,
                "present_days": 90,
                "absent_days": 5,
                "half_days": 1,
                "leave_days": 4,
                "weekly_offs": 10,
                "paid_holidays": 0,
                "late_arrivals_count": 25,
                "total_late_mins": 500,
                "early_exits_count": 2,
                "total_early_mins": 10,
                "overtime_records_count": 5,
                "total_ot_hours": 40.0,
                "missing_punch_outs": 6,
                "missing_punch_ins": 0,
                "unpunched_salary_days": 10,
            }
        ],
        # q_unauth
        [
            {
                "unauthorized_absence_days": 5,
                "leave_covered_absence_days": 2,
            }
        ],
        # q_bal
        [
            {
                "PL": 4.0,
                "CL": 0.0,
                "SL": 0.0,
                "CO": 0.0,
            }
        ],
        # q_req
        [
            {
                "leave_code": "PL",
                "request_count": 2,
                "total_days_taken": 4.0,
                "last_availed_date": "2026-04-11",
            }
        ],
    ]

    service = AttendanceService()
    resp = service.get_employee_lifetime_attendance_analytics(1273)
    assert resp.emp_id == 1273
    assert resp.emp_name == "Arbind Sahu"
    assert resp.present_days == 90
    assert resp.present_pct == 100.0  # 90 present / 90 working days (100 - 10 weekly offs)
    assert resp.late_arrivals_count == 25
    assert resp.unauthorized_absence_days == 5
    assert resp.leave_covered_absence_days == 2
    assert resp.absconding_risk_level == "MEDIUM"  # 5/90 = 5.6% -> MEDIUM (3-8%)
    assert resp.leave_days == 2  # leave_covered_cnt from unauthorized query
    assert resp.weekly_offs == 10
    assert len(resp.leaves_breakdown) == 4
    assert resp.leaves_breakdown[0].leave_type == "Privilege/Paid Leave"
    assert len(resp.risk_signals) > 0


@patch("app.modules.attendance.service.execute_readonly_query")
def test_get_attendance_directory_noise_filtering_and_status_derivation(mock_exec):
    mock_exec.side_effect = [
        [{"total": 2}],
        [
            {
                "AttID": 1001,
                "AttEmpID": 1847,
                "EmpCode": "EMP1847",
                "emp_name": "Test User",
                "att_date": "2026-07-17",
                "AttSalType": "SAL",
                "in_time": "09:00:00",
                "out_time": "18:00:00",
                "off_in_time": None,
                "off_out_time": None,
                "ShiftCode": "G1",
                "ShiftDescription": "General Shift",
                "late_mins": 0,
                "early_mins": 0,
                "ot_mins": 0,
                "emp_status": "ACTIVE",
            },
            {
                "AttID": 1002,
                "AttEmpID": 1847,
                "EmpCode": "EMP1847",
                "emp_name": "Test User",
                "att_date": "2026-07-16",
                "AttSalType": "SAL",
                "in_time": "09:20:00",
                "out_time": "17:40:00",
                "off_in_time": None,
                "off_out_time": None,
                "ShiftCode": "G1",
                "ShiftDescription": "General Shift",
                "late_mins": 20,
                "early_mins": 20,
                "ot_mins": 0,
                "emp_status": "ACTIVE",
            },
        ],
    ]

    service = AttendanceService()
    res = service.get_attendance_directory(emp_id=1847)
    assert res.total == 2
    assert len(res.items) == 2
    assert res.items[0].status_label == "Present"
    assert res.items[1].status_label == "Late & Early Exit"
    # Ensure noise reduction clause was included in SQL query
    sql_args = mock_exec.call_args_list[0][0][0]
    assert "NOT (s.ShiftCode IN ('WO', 'PH')" in sql_args
