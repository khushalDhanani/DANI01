from unittest.mock import patch

import pytest

from app.modules.employee.analyzer import EmployeeModuleAnalyzer
from app.modules.employee.schemas import IssueSeverity
from app.modules.employee.service import EmployeeService
from app.modules.registry import module_registry


def test_employee_module_definition_registered():
    mod = module_registry.get("EMPLOYEE")
    assert mod is not None
    assert mod.code == "EMPLOYEE"
    assert mod.root_table == "EmployeeMst"
    assert mod.root_key == "EmpID"
    assert len(mod.tables) >= 10
    assert len(mod.relationships) >= 8


@pytest.mark.asyncio
async def test_employee_service_overview():
    service = EmployeeService()

    mock_status_res = [
        {"total": 3091, "active": 1316, "inactive": 116, "resigned": 1555, "deleted": 104}
    ]
    mock_gender_res = [{"label": "M", "count": 1000}, {"label": "F", "count": 316}]
    mock_type_res = [{"label": "Permanent", "count": 1300}, {"label": "Contract", "count": 16}]
    mock_dept_res = [{"label": "R&D", "count": 400}, {"label": "Production", "count": 300}]
    mock_comp_res = [{"label": "Aether Industries Limited", "count": 1316}]
    mock_loc_res = [{"label": "Site 1", "count": 800}]
    mock_user_res = [{"users_linked": 1200, "total_active_users": 4214}]
    mock_rep_res = [{"emps_with_active_mgr": 1222}]

    def mock_query(sql, params=None):
        if "SUM(CASE WHEN EmpIsActive" in sql:
            return mock_status_res
        elif "EmpGender" in sql:
            return mock_gender_res
        elif "EmpTypeDesc" in sql:
            return mock_type_res
        elif "d.DeptName" in sql:
            return mock_dept_res
        elif "c.CompName" in sql:
            return mock_comp_res
        elif "l.LocName" in sql:
            return mock_loc_res
        elif "users_linked" in sql:
            return mock_user_res
        elif "emps_with_active_mgr" in sql:
            return mock_rep_res
        return []

    with patch("app.modules.employee.service.execute_readonly_query", side_effect=mock_query):
        overview = await service.get_employee_overview()
        assert overview.status_counts.total == 3091
        assert overview.status_counts.active == 1316
        assert overview.status_counts.resigned == 1555
        assert len(overview.gender_distribution) == 2
        assert overview.gender_distribution[0].label == "Male"
        assert len(overview.employment_type_distribution) == 2
        assert len(overview.department_distribution) == 2
        assert overview.user_account_coverage["active_employees_with_login"] == 1200


@pytest.mark.asyncio
async def test_employee_service_structure():
    service = EmployeeService()
    mock_rc_rows = [
        {"table_name": "EmployeeMst", "row_count": 3091},
        {"table_name": "EmployeeOfficialDet", "row_count": 4658},
        {"table_name": "EmployeeReportingDet", "row_count": 10456},
        {"table_name": "SecurityUserMst", "row_count": 5420},
    ]

    with patch("app.modules.employee.service.execute_readonly_query", return_value=mock_rc_rows):
        structure = await service.get_employee_structure()
        assert structure.master_table == "dbo.EmployeeMst"
        assert structure.canonical_key == "EmpID"
        assert structure.business_key == "EmpCode"
        assert len(structure.tables) >= 10
        assert len(structure.relationships) >= 10
        assert structure.confidence_summary["CONFIRMED"] >= 10


@pytest.mark.asyncio
async def test_employee_service_quality():
    service = EmployeeService()
    mock_dq_rows = [
        {"code": "DUP_EMP_CODE", "cnt": 20},
        {"code": "ACTIVE_PAST_RESIGN", "cnt": 3},
        {"code": "MISSING_OFFICIAL_RECORD", "cnt": 6},
        {"code": "MISSING_EMAIL", "cnt": 12},
        {"code": "MISSING_DEPT", "cnt": 8},
        {"code": "MISSING_DESIG", "cnt": 8},
        {"code": "MISSING_MANAGER", "cnt": 94},
        {"code": "DUP_PAN", "cnt": 102},
        {"code": "DUP_AADHAAR", "cnt": 145},
        {"code": "DUP_PHONE", "cnt": 117},
        {"code": "INACTIVE_NO_RESIGN_DATE", "cnt": 116},
        {"code": "ORPHAN_REFERENCES", "cnt": 5},
    ]

    with patch("app.modules.employee.service.execute_readonly_query", return_value=mock_dq_rows):
        quality = await service.get_employee_quality()
        assert quality.critical_issues_count == 29
        assert quality.warning_issues_count == 486
        assert quality.info_issues_count == 121
        assert len(quality.rules) == 12
        dup_rule = next(r for r in quality.rules if r.rule_code == "DUP_EMP_CODE")
        assert dup_rule.severity == IssueSeverity.CRITICAL
        assert dup_rule.issue_count == 20


@pytest.mark.asyncio
async def test_employee_service_records_and_detail():
    service = EmployeeService()

    mock_count_res = [{"total": 1, "active_cnt": 1, "inactive_cnt": 0}]
    mock_items_res = [
        {
            "EmpID": 3,
            "EmpCode": "1002",
            "EmpFirstName": "Kevin",
            "EmpMiddleName": "Kiritbhai",
            "EmpLastName": "Shah",
            "full_name": "Kevin Kiritbhai Shah",
            "EmpGender": "M",
            "EmpBirthDate": "1991-11-24",
            "EmpEmailIDCompany": "kevin@aether.co.in",
            "EmpEmailIDPersonal": "kevin@yahoo.com",
            "EmpPhone1": "+917600817822",
            "EmpPANNo": "ENGPS6706C",
            "AadharCardNo": "476474429318",
            "EmpJoinDate": "2013-05-04",
            "EmpResignDate": None,
            "EmpIsActive": True,
            "EmpIsDeleted": False,
            "employment_type": "Permanent",
            "company_name": "Aether Industries Limited",
            "department_name": "Procurement Team",
            "designation_name": "Lead Procurement",
            "location_name": "Site 1",
            "grade_desc": "Grade II",
            "FunctionalMgrEmpID": 5,
            "functional_mgr_name": "Rohan Desai",
            "AdminMgrEmpID": 92,
            "admin_mgr_name": "Denish Dodhiyawala",
            "UserID": 2,
            "UserName": "Kevin Shah",
            "UserIsActive": True,
            "role_desc": "Manager",
        }
    ]

    def mock_query(sql, params=None):
        if (
            "SELECT COUNT(*) AS total" in sql
            or "SELECT \n            COUNT(*) AS total" in sql
            or "COUNT(*) AS total," in sql
        ):
            return mock_count_res
        elif "OFFSET :offset" in sql:
            return mock_items_res
        elif "WHERE e.EmpID = :emp_id" in sql:
            return [
                mock_items_res[0]
                | {
                    "EmpTitle": "Mr.",
                    "EmpBloodGroupID": 5,
                    "marital_status": "Married",
                    "religion": "Hindu",
                    "caste_category": "General",
                    "nationality": "India",
                    "EmpPhone2": None,
                    "EmpDirectNumber": None,
                    "EmpExtentionNumber": "3010",
                    "EmpCUGNumber": None,
                    "EmpCorrAdd1": "Add1",
                    "EmpCorrAdd2": None,
                    "EmpCorrAdd3": None,
                    "EmpCorrPincode": "394230",
                    "EmpPermAdd1": "Add1",
                    "EmpPermAdd2": None,
                    "EmpPermAdd3": None,
                    "EmpPermPincode": "394230",
                    "EmpUANNo": "1001",
                    "EmpPFNo": "PF1",
                    "EmpESICNo": None,
                    "VoterID": None,
                    "EmpDrivingLicenseNo": None,
                    "PRANNo": None,
                    "SapGLCode": None,
                    "MicrosoftObjectID": None,
                }
            ]
        elif "FROM dbo.EmployeeOfficialDet o" in sql:
            return [
                {
                    "EmpOfficeDetID": 1,
                    "DeptName": "Procurement",
                    "DesigName": "Lead",
                    "LocName": "Site 1",
                    "EmpGradeDesc": "Grade II",
                    "ApplicableFrDate": "2013-05-04",
                    "JoiningDate": "2013-05-04",
                    "ResignDate": None,
                    "EmpOfficeDetIsActive": True,
                }
            ]
        elif "FROM dbo.EmployeeReportingDet r" in sql:
            return [
                {
                    "ReportingEmpID": 5,
                    "mgr_code": "1149",
                    "mgr_name": "Rohan Desai",
                    "ReportingType": "F",
                }
            ]
        elif "FROM dbo.SecurityUserMst u" in sql:
            return [
                {
                    "UserID": 2,
                    "UserName": "kevin",
                    "UserEmail": "kevin@aether.co.in",
                    "UserADID": "kevin",
                    "UserIsActive": True,
                    "RoleDesc": "Manager",
                }
            ]
        elif "FROM dbo.EmployeeFamilyDet" in sql:
            return [
                {
                    "EmpFamilyDetID": 10,
                    "EmpFamilyMemberName": "Family 1",
                    "RelationID": 1,
                    "EmpFamilyMemberDOB": None,
                    "EmpFamilyMemberPhone": None,
                    "EmpFamilyIsEmergencyContact": True,
                }
            ]
        elif "FROM dbo.EmployeeQualificationDet" in sql:
            return [
                {
                    "EmpQualDetID": 20,
                    "DegreeID": 1,
                    "PassingYear": 2012,
                    "GradePercentage": "80%",
                    "InstituteName": "Uni",
                }
            ]
        elif "FROM dbo.EmployeeExperienceDet" in sql:
            return [
                {
                    "EmpExpDetID": 30,
                    "CompanyName": "Past Corp",
                    "Designation": "Exec",
                    "FromDate": None,
                    "ToDate": None,
                    "LastDrawnCTC": "500000",
                }
            ]
        return []

    with patch("app.modules.employee.service.execute_readonly_query", side_effect=mock_query):
        records = await service.get_employee_records()
        assert records.total == 1
        assert len(records.items) == 1
        assert records.items[0].emp_code == "1002"
        assert records.items[0].department_name == "Procurement Team"

        detail = await service.get_employee_detail(3)
        assert detail is not None
        assert detail.emp_id == 3
        assert detail.full_name == "Kevin Kiritbhai Shah"
        assert len(detail.official_history) == 1
        assert len(detail.family_members) == 1


@pytest.mark.asyncio
async def test_employee_analyzer_delegation():
    analyzer = EmployeeModuleAnalyzer()
    with (
        patch.object(analyzer.service, "get_employee_overview", return_value={"mock": "overview"}),
        patch.object(
            analyzer.service, "get_employee_structure", return_value={"mock": "structure"}
        ),
        patch.object(analyzer.service, "get_employee_quality", return_value={"mock": "quality"}),
    ):
        res_ov = await analyzer.analyze_overview()
        res_st = await analyzer.analyze_structure()
        res_qu = await analyzer.analyze_quality()
        assert res_ov == {"mock": "overview"}
        assert res_st == {"mock": "structure"}
        assert res_qu == {"mock": "quality"}
