from unittest.mock import patch

import pytest

from app.modules.definitions.organization import OrganizationModuleDefinition
from app.modules.organization.analyzer import OrganizationModuleAnalyzer
from app.modules.organization.schemas import (
    OrgDataQualityResponse,
    OrgHierarchyResponse,
    OrgOverviewResponse,
    OrgReportingTreeResponse,
    OrgUnitListResponse,
    OrgUnitType,
)
from app.modules.organization.service import OrganizationService


def test_organization_module_definition():
    assert OrganizationModuleDefinition.code == "ORGANIZATION"
    assert OrganizationModuleDefinition.root_table == "OrgCompanyMst"
    assert OrganizationModuleDefinition.root_key == "CompID"
    assert len(OrganizationModuleDefinition.tables) >= 7
    assert len(OrganizationModuleDefinition.relationships) >= 5


@pytest.mark.asyncio
async def test_get_org_overview_mocked():
    service = OrganizationService()

    mock_scale = [
        {
            "total_companies": 2,
            "active_companies": 2,
            "total_locations": 22,
            "active_locations": 18,
            "total_main_depts": 26,
            "active_main_depts": 26,
            "total_departments": 52,
            "active_departments": 43,
            "total_designations": 389,
            "active_designations": 370,
            "total_grades": 9,
            "active_grades": 9,
        }
    ]
    mock_comps = [{"id": 1, "name": "Aether Industries Limited", "code": "AIL", "count": 1225}]
    mock_locs = [{"id": 1, "name": "Catalyst", "code": "Site 1", "count": 387}]
    mock_depts = [{"id": 24, "name": "Maintenance Team - 2", "code": "M2", "count": 140}]
    mock_grades = [{"id": 1, "name": "Grade I", "code": None, "count": 15}]
    mock_total = [{"total": 1316}]

    with patch(
        "app.modules.organization.service.execute_readonly_query",
        side_effect=[mock_scale, mock_comps, mock_locs, mock_depts, mock_grades, mock_total],
    ):
        res = await service.get_org_overview()
        assert isinstance(res, OrgOverviewResponse)
        assert res.scale_counts.total_companies == 2
        assert res.scale_counts.active_locations == 18
        assert res.active_employee_total == 1316
        assert len(res.headcount_by_company) == 1
        assert res.headcount_by_company[0].count == 1225


@pytest.mark.asyncio
async def test_get_org_hierarchy_map_mocked():
    service = OrganizationService()

    mock_rows = [
        {
            "CompID": 1,
            "CompName": "Aether Industries Limited",
            "CompCode": "AIL",
            "LocID": 1,
            "LocName": "Catalyst",
            "LocShortName": "Site 1",
            "SOSSiteHeadEmpID": 864,
            "site_head_code": "1799",
            "site_head_name": "Ramesh Maurya",
            "MainDeptID": 4,
            "MainDeptName": "Maintenance Team",
            "DeptID": 24,
            "DeptName": "Maintenance Team - 2",
            "DeptHeadEmpID": 102,
            "dept_head_code": "1082",
            "dept_head_name": "Parag Detroja",
            "DesigID": 10,
            "DesigName": "Maintenance Engineer",
            "headcount": 50,
        }
    ]

    with patch("app.modules.organization.service.execute_readonly_query", return_value=mock_rows):
        res = await service.get_org_hierarchy_map()
        assert isinstance(res, OrgHierarchyResponse)
        assert len(res.companies) == 1
        assert res.companies[0].name == "Aether Industries Limited"
        assert res.companies[0].headcount == 50
        assert len(res.companies[0].children) == 1
        assert res.companies[0].children[0].name == "Catalyst"


@pytest.mark.asyncio
async def test_get_org_units_mocked():
    service = OrganizationService()

    mock_count = [{"total": 1}]
    mock_items = [
        {
            "unit_id": 1,
            "unit_type": "COMPANY",
            "unit_code": "AIL",
            "unit_name": "Aether Industries Limited",
            "parent_id": None,
            "parent_name": None,
            "head_emp_id": None,
            "head_name": None,
            "head_code": None,
            "active_headcount": 1225,
            "is_active": True,
            "is_deleted": False,
        }
    ]

    with patch(
        "app.modules.organization.service.execute_readonly_query",
        side_effect=[mock_count, mock_items],
    ):
        res = await service.get_org_units(unit_type=OrgUnitType.COMPANY)
        assert isinstance(res, OrgUnitListResponse)
        assert res.total == 1
        assert len(res.items) == 1
        assert res.items[0].unit_name == "Aether Industries Limited"


@pytest.mark.asyncio
async def test_get_org_quality_mocked():
    service = OrganizationService()

    mock_dq = [
        {"code": "MISSING_OFFICIAL_RECORD", "cnt": 6},
        {"code": "MULTIPLE_ACTIVE_POSITIONS", "cnt": 1},
        {"code": "EMPTY_LOCATIONS", "cnt": 4},
        {"code": "EMPTY_DEPARTMENTS", "cnt": 1},
        {"code": "EMPTY_DESIGNATIONS", "cnt": 88},
        {"code": "LINKED_TO_INACTIVE_LOCATION", "cnt": 1},
        {"code": "INACTIVE_ORGANIZATION_UNITS", "cnt": 32},
    ]

    with patch("app.modules.organization.service.execute_readonly_query", return_value=mock_dq):
        res = await service.get_org_quality()
        assert isinstance(res, OrgDataQualityResponse)
        assert res.critical_issues_count >= 7
        assert res.overall_health_score <= 100.0


@pytest.mark.asyncio
async def test_get_reporting_hierarchy_mocked():
    service = OrganizationService()

    mock_rows = [
        {
            "EmpID": 170,
            "EmpCode": "1001",
            "full_name": "Rohan Amin",
            "DesigName": "Managing Director",
            "DeptName": "Founder",
            "LocName": "Catalyst",
            "EmpGradeDesc": "Grade I",
            "ReportingEmpID": None,
            "direct_reports_count": 5,
        }
    ]

    with patch("app.modules.organization.service.execute_readonly_query", return_value=mock_rows):
        res = await service.get_reporting_hierarchy()
        assert isinstance(res, OrgReportingTreeResponse)
        assert len(res.roots) == 1
        assert res.roots[0].role_type == "EXECUTIVE"


@pytest.mark.asyncio
async def test_organization_analyzer():
    analyzer = OrganizationModuleAnalyzer()
    with patch.object(analyzer.service, "get_org_overview", return_value="overview"):
        assert await analyzer.analyze_overview() == "overview"
    with patch.object(analyzer.service, "get_org_hierarchy_map", return_value="hierarchy"):
        assert await analyzer.analyze_hierarchy() == "hierarchy"
    with patch.object(analyzer.service, "get_org_quality", return_value="quality"):
        assert await analyzer.analyze_quality() == "quality"
