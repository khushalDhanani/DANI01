from unittest.mock import patch

from app.modules.payroll.payroll_service import PayrollService


def test_payroll_service_metadata():
    svc = PayrollService()
    meta = svc.get_payroll_metadata()
    assert meta.module_code == "PAYROLL"
    assert len(meta.tables) >= 4
    assert any(t.table_name == "dbo.PayEarnedSalary" for t in meta.tables)
    assert len(meta.relationships) >= 4


@patch("app.modules.payroll.payroll_service.execute_readonly_query")
def test_get_payroll_overview(mock_exec):
    mock_exec.side_effect = [
        # 1. total
        [
            {
                "total_payroll_records": 81899,
                "emps_with_payroll": 2500,
                "lifetime_net_pay": 50000000.0,
                "lifetime_earned": 55000000.0,
                "lifetime_deduction": 5000000.0,
            }
        ],
        # 2. no pay
        [{"emps_without_payroll": 50}],
        # 3. monthly trends
        [
            {
                "sal_month": "202607",
                "record_count": 15,
                "total_earned": 3500000.0,
                "total_deduction": 500000.0,
                "total_net_pay": 3000000.0,
            }
        ],
    ]

    svc = PayrollService()
    res = svc.get_payroll_overview()

    assert res.total_payroll_records == 81899
    assert res.total_employees_with_payroll == 2500
    assert res.total_employees_without_payroll == 50
    assert res.latest_payroll_month == "202607"
    assert res.latest_month_net_pay == 3000000.0


@patch("app.modules.payroll.payroll_service.execute_readonly_query")
def test_get_payroll_directory(mock_exec):
    mock_exec.side_effect = [
        # count
        [{"total": 1}],
        # items
        [
            {
                "EarnedSalID": 101,
                "emp_id": 18,
                "emp_code": "EMP-18",
                "emp_name": "Aman Desai",
                "dept_name": "Engineering",
                "sal_month": "202606",
                "paid_days": 25.0,
                "present_days": 24.0,
                "total_earned": 50000.0,
                "total_deduction": 5000.0,
                "net_pay": 45000.0,
                "ctc_gross": 600000.0,
                "pay_date": "2026-07-05",
                "is_active": 1,
            }
        ],
    ]

    svc = PayrollService()
    res = svc.get_payroll_directory(limit=10, offset=0)

    assert res.total == 1
    assert len(res.items) == 1
    assert res.items[0].emp_name == "Aman Desai"
    assert res.items[0].net_pay == 45000.0


@patch("app.modules.payroll.payroll_service.execute_readonly_query")
def test_get_payroll_quality(mock_exec):
    mock_exec.return_value = [
        {"code": "ORPHAN_PAYROLL_HEADER", "cnt": 0},
        {"code": "CORRUPTED_NET_PAY", "cnt": 21},
        {"code": "ORPHAN_PAYROLL_DETAIL", "cnt": 0},
        {"code": "DUP_PAYROLL_PERIOD", "cnt": 0},
        {"code": "NEGATIVE_SALARY", "cnt": 0},
        {"code": "MISSING_PAYROLL_RECORD", "cnt": 12},
    ]

    svc = PayrollService()
    res = svc.get_payroll_quality()

    assert res.critical_issues_count == 21
    assert res.info_issues_count == 12
    assert len(res.rules) == 6


@patch("app.modules.payroll.payroll_service.execute_readonly_query")
def test_get_employee_payroll_history(mock_exec):
    mock_exec.side_effect = [
        # emp info
        [
            {
                "EmpID": 18,
                "EmpCode": "EMP-18",
                "emp_name": "Aman Desai",
                "dept_name": "Engineering",
                "EmpIsActive": 1,
            }
        ],
        # slips
        [
            {
                "EarnedSalID": 101,
                "sal_month": "202606",
                "paid_days": 25.0,
                "present_days": 24.0,
                "absent_days": 0.0,
                "total_earned": 50000.0,
                "total_deduction": 5000.0,
                "net_pay": 45000.0,
                "bank_name": "HDFC Bank",
                "bank_acc_no": "123456789",
                "pay_date": "2026-07-05",
            }
        ],
    ]

    svc = PayrollService()
    res = svc.get_employee_payroll_history(18)

    assert res.emp_id == 18
    assert res.total_payslips_count == 1
    assert res.lifetime_net_pay == 45000.0
    assert res.history_items[0].sal_month == "202606"
