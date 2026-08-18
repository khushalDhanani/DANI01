from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_attendance_service
from app.main import app
from app.modules.attendance.schemas import (
    AttendanceDataQualityResponse,
    AttendanceDirectoryResponse,
    AttendanceLogItem,
    AttendanceMetrics,
    AttendanceOverviewResponse,
    AttendanceQualityIssuesListResponse,
    LeaveApplicationsListResponse,
    LeaveBalancesListResponse,
    LeaveOverviewResponse,
    PunchMetrics,
)


@pytest.fixture
def mock_attendance_service():
    service = MagicMock()
    service.get_attendance_overview.return_value = AttendanceOverviewResponse(
        attendance_metrics=AttendanceMetrics(
            total_attendance_records=100,
            employees_with_attendance=10,
            present_days=80,
            present_pct=80.0,
            absent_days=10,
            absent_pct=10.0,
            half_days=2,
            half_days_pct=2.0,
            leave_days=5,
            leave_days_pct=5.0,
            weekly_offs=2,
            paid_holidays=1,
        ),
        punch_metrics=PunchMetrics(
            total_punches_logged=200,
            valid_punch_pairs=90,
            missing_punch_out_count=5,
            missing_punch_in_count=2,
            late_arrivals_count=10,
            early_departures_count=3,
            overtime_records_count=8,
            total_overtime_hours=16.0,
        ),
        shift_distribution=[],
    )

    service.get_attendance_directory.return_value = AttendanceDirectoryResponse(
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
    service.export_attendance_directory.return_value = "att_id,emp_name\n101,John Doe"

    service.get_leave_overview.return_value = LeaveOverviewResponse(
        total_leave_requests=10,
        approved_requests=8,
        approved_pct=80.0,
        pending_requests=1,
        pending_pct=10.0,
        rejected_requests=1,
        rejected_pct=10.0,
        cancelled_requests=0,
        cancelled_pct=0.0,
        active_employees_on_leave=2,
        total_employees_with_leave_balance=15,
        leave_type_distribution=[],
    )

    service.get_leave_applications.return_value = LeaveApplicationsListResponse(
        total=0,
        limit=20,
        offset=0,
        items=[],
    )
    service.export_leave_applications.return_value = "req_id,emp_name\n1,John Doe"

    service.get_leave_balances.return_value = LeaveBalancesListResponse(
        total=0,
        limit=20,
        offset=0,
        items=[],
    )

    service.get_attendance_quality.return_value = AttendanceDataQualityResponse(
        overall_health_score=95.0,
        critical_issues_count=0,
        warning_issues_count=1,
        info_issues_count=0,
        rules=[],
        summary_by_severity={"CRITICAL": 0, "WARNING": 1, "INFO": 0},
    )

    service.get_attendance_quality_issues.return_value = AttendanceQualityIssuesListResponse(
        issue_code="PUNCH_OUT_BEFORE_IN",
        total=0,
        limit=20,
        offset=0,
        items=[],
    )
    service.export_attendance_quality_issues.return_value = "record_id,detail\n1,Reversed punch"

    return service


def test_attendance_api_routes(mock_attendance_service):
    app.dependency_overrides[get_attendance_service] = lambda: mock_attendance_service
    client = TestClient(app)

    try:
        # 1. Overview
        res = client.get("/api/v1/modules/ATTENDANCE/overview")
        assert res.status_code == 200
        assert res.json()["attendance_metrics"]["total_attendance_records"] == 100

        # 2. Directory
        res = client.get("/api/v1/modules/ATTENDANCE/directory")
        assert res.status_code == 200
        assert res.json()["total"] == 1

        # 3. Export directory
        res = client.get("/api/v1/modules/ATTENDANCE/directory/export")
        assert res.status_code == 200
        assert "John Doe" in res.text

        # 4. Leave overview
        res = client.get("/api/v1/modules/ATTENDANCE/leave/overview")
        assert res.status_code == 200
        assert res.json()["approved_requests"] == 8

        # 5. Leave applications
        res = client.get("/api/v1/modules/ATTENDANCE/leave/applications")
        assert res.status_code == 200

        # 6. Export leave applications
        res = client.get("/api/v1/modules/ATTENDANCE/leave/applications/export")
        assert res.status_code == 200

        # 7. Leave balances
        res = client.get("/api/v1/modules/ATTENDANCE/leave/balances")
        assert res.status_code == 200

        # 8. Quality audit
        res = client.get("/api/v1/modules/ATTENDANCE/quality")
        assert res.status_code == 200
        assert res.json()["overall_health_score"] == 95.0

        # 9. Quality issues
        res = client.get("/api/v1/modules/ATTENDANCE/quality/issues?issue=PUNCH_OUT_BEFORE_IN")
        assert res.status_code == 200

        # 10. Export quality issues
        res = client.get(
            "/api/v1/modules/ATTENDANCE/quality/issues/export?issue=PUNCH_OUT_BEFORE_IN"
        )
        assert res.status_code == 200
    finally:
        app.dependency_overrides.clear()
