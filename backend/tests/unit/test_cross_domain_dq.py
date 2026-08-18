from unittest.mock import patch

from app.modules.employee.cross_domain_service import RULE_DEFINITIONS, CrossDomainQualityService


def test_rule_definitions_count():
    assert len(RULE_DEFINITIONS) == 15
    for rdef in RULE_DEFINITIONS:
        assert "code" in rdef
        assert "severity" in rdef
        assert rdef["severity"] in ["CRITICAL", "WARNING", "INFO"]


@patch("app.modules.employee.cross_domain_service.execute_readonly_query")
def test_get_cross_domain_overview(mock_exec):
    # Mock execute_readonly_query returning 0 or sample counts
    mock_exec.side_effect = [
        [{"cnt": 0, "emp_cnt": 0}],  # DUP_EMP_CODE
        [{"cnt": 0, "emp_cnt": 0}],  # ACTIVE_DELETED_CONFLICT
        [{"cnt": 3, "emp_cnt": 3}],
        [{"emp_id": 1}, {"emp_id": 2}, {"emp_id": 3}],  # ACTIVE_PAST_RESIGNED
        [{"cnt": 0, "emp_cnt": 0}],  # MISSING_OFFICIAL_RECORD
        [{"cnt": 0, "emp_cnt": 0}],  # MISSING_ORG_ASSIGNMENT
        [{"cnt": 0, "emp_cnt": 0}],  # MISSING_MANAGER
        [{"cnt": 0, "emp_cnt": 0}],  # INVALID_MANAGER_FK
        [{"cnt": 0, "emp_cnt": 0}],  # SELF_REPORTING_EMPLOYEE
        [{"cnt": 0, "emp_cnt": 0}],  # CIRCULAR_MANAGER_HIERARCHY
        [{"cnt": 0, "emp_cnt": 0}],  # ACTIVE_USER_INACTIVE_EMP
        [{"cnt": 0, "emp_cnt": 0}],  # ORPHAN_USER_LOGIN
        [{"cnt": 0, "emp_cnt": 0}],  # MULTIPLE_ACTIVE_USERS
        [{"cnt": 0, "emp_cnt": 0}],  # ATTENDANCE_ORPHAN_EMP
        [{"cnt": 0, "emp_cnt": 0}],  # LEAVE_ORPHAN_EMP
        [{"cnt": 21, "emp_cnt": 21}],
        [{"emp_id": 101}],  # PAYROLL_CORRUPTED_NET_PAY
    ]

    service = CrossDomainQualityService()
    res = service.get_cross_domain_overview()

    assert res.total_issues == 24
    assert res.critical_issues_count == 21
    assert res.warning_issues_count == 3
    assert res.total_affected_employees == 4
    assert len(res.rules) == 15
    assert res.overall_health_score < 100.0


@patch("app.modules.employee.cross_domain_service.execute_readonly_query")
def test_get_cross_domain_issues(mock_exec):
    mock_exec.side_effect = [
        [
            {
                "record_id": "EMP-101",
                "emp_id": 101,
                "emp_code": "EMP101",
                "emp_name": "Test User",
                "table_name": "dbo.EmployeeMst",
                "rule_failed": "ACTIVE_PAST_RESIGNED",
                "severity": "WARNING",
                "category": "MASTER",
                "issue_detail": "Active employee has resignation date",
            }
        ],
        [{"total": 1}],
    ]

    service = CrossDomainQualityService()
    res = service.get_cross_domain_issues(rule_code="ACTIVE_PAST_RESIGNED")

    assert res.total == 1
    assert len(res.items) == 1
    assert res.items[0].emp_code == "EMP101"
    assert res.items[0].rule_failed == "ACTIVE_PAST_RESIGNED"


@patch("app.modules.employee.cross_domain_service.execute_readonly_query")
def test_download_cross_domain_export(mock_exec):
    mock_exec.side_effect = [
        [
            {
                "record_id": "EMP-101",
                "emp_id": 101,
                "emp_code": "EMP101",
                "emp_name": "Test User",
                "table_name": "dbo.EmployeeMst",
                "rule_failed": "ACTIVE_PAST_RESIGNED",
                "severity": "WARNING",
                "category": "MASTER",
                "issue_detail": "Active employee has resignation date",
            }
        ],
        [{"total": 1}],
    ]

    service = CrossDomainQualityService()
    csv_bytes = service.download_cross_domain_export(rule_code="ACTIVE_PAST_RESIGNED")

    assert isinstance(csv_bytes, bytes)
    content = csv_bytes.decode("utf-8")
    assert "Record ID,Employee ID,Employee Code" in content
    assert "EMP-101,101,EMP101" in content
