from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.employee.schemas import (
    EmployeeDataQualityResponse,
    EmployeeDetailResponse,
    EmployeeListItem,
    EmployeeListResponse,
    EmployeeOverviewResponse,
    EmployeeStatusCount,
    EmployeeStructureResponse,
    IssueSeverity,
    QualityRuleResult,
    RelationshipEdge,
    TableNodeMetadata,
)


@pytest.fixture
def mock_overview_response() -> EmployeeOverviewResponse:
    return EmployeeOverviewResponse(
        status_counts=EmployeeStatusCount(
            total=3091, active=1316, inactive=116, resigned=1555, deleted=104
        ),
        gender_distribution=[],
        employment_type_distribution=[],
        department_distribution=[],
        company_distribution=[],
        top_locations=[],
        user_account_coverage={"active_employees_with_login": 1200, "login_coverage_pct": 91.2},
        reporting_coverage={"active_employees_with_manager": 1222, "manager_coverage_pct": 92.8},
    )


@pytest.fixture
def mock_structure_response() -> EmployeeStructureResponse:
    return EmployeeStructureResponse(
        master_table="dbo.EmployeeMst",
        canonical_key="EmpID",
        business_key="EmpCode",
        tables=[
            TableNodeMetadata(
                schema="dbo",
                table="EmployeeMst",
                role="ROOT_MASTER",
                row_count=3091,
                key_column="EmpID",
                confidence="CONFIRMED",
                description="Core master entity",
            )
        ],
        relationships=[
            RelationshipEdge(
                source_table="dbo.EmployeeMst",
                target_table="dbo.EmployeeOfficialDet",
                source_key="EmpID",
                target_key="EmpID",
                relationship_type="ONE_TO_MANY",
                confidence="CONFIRMED",
                description="Position history",
            )
        ],
        confidence_summary={"CONFIRMED": 1, "LIKELY": 0},
    )


@pytest.fixture
def mock_quality_response() -> EmployeeDataQualityResponse:
    return EmployeeDataQualityResponse(
        overall_health_score=88.5,
        critical_issues_count=29,
        warning_issues_count=486,
        info_issues_count=121,
        rules=[
            QualityRuleResult(
                rule_code="DUP_EMP_CODE",
                rule_name="Duplicate Employee Code",
                severity=IssueSeverity.CRITICAL,
                description="Duplicates",
                issue_count=20,
                impact="High",
                recommendation="Fix",
            )
        ],
        summary_by_severity={"CRITICAL": 29, "WARNING": 486, "INFO": 121},
    )


@pytest.fixture
def mock_list_response() -> EmployeeListResponse:
    return EmployeeListResponse(
        total=1,
        active_count=1,
        inactive_count=0,
        limit=25,
        offset=0,
        items=[
            EmployeeListItem(
                emp_id=3,
                emp_code="1002",
                full_name="Kevin Shah",
                first_name="Kevin",
                is_active=True,
                is_deleted=False,
                department_name="Procurement Team",
            )
        ],
    )


@pytest.fixture
def mock_detail_response() -> EmployeeDetailResponse:
    return EmployeeDetailResponse(
        emp_id=3,
        emp_code="1002",
        first_name="Kevin",
        full_name="Kevin Shah",
        is_active=True,
        is_deleted=False,
        current_dept="Procurement Team",
    )


@pytest.mark.asyncio
async def test_get_employee_overview_endpoint(mock_overview_response: EmployeeOverviewResponse):
    with patch(
        "app.modules.employee.service.EmployeeService.get_employee_overview",
        new_callable=AsyncMock,
        return_value=mock_overview_response,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/modules/EMPLOYEE/overview")
            assert res.status_code == 200
            data = res.json()
            assert data["status_counts"]["total"] == 3091
            assert data["status_counts"]["active"] == 1316


@pytest.mark.asyncio
async def test_get_employee_structure_endpoint(mock_structure_response: EmployeeStructureResponse):
    with patch(
        "app.modules.employee.service.EmployeeService.get_employee_structure",
        new_callable=AsyncMock,
        return_value=mock_structure_response,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/modules/EMPLOYEE/structure")
            assert res.status_code == 200
            data = res.json()
            assert data["master_table"] == "dbo.EmployeeMst"
            assert data["canonical_key"] == "EmpID"


@pytest.mark.asyncio
async def test_get_employee_quality_endpoint(mock_quality_response: EmployeeDataQualityResponse):
    with patch(
        "app.modules.employee.service.EmployeeService.get_employee_quality",
        new_callable=AsyncMock,
        return_value=mock_quality_response,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/modules/EMPLOYEE/quality")
            assert res.status_code == 200
            data = res.json()
            assert data["critical_issues_count"] == 29
            assert len(data["rules"]) == 1


@pytest.mark.asyncio
async def test_get_employee_records_and_detail_endpoint(
    mock_list_response: EmployeeListResponse,
    mock_detail_response: EmployeeDetailResponse,
):
    with (
        patch(
            "app.modules.employee.service.EmployeeService.get_employee_records",
            new_callable=AsyncMock,
            return_value=mock_list_response,
        ),
        patch(
            "app.modules.employee.service.EmployeeService.get_employee_detail",
            new_callable=AsyncMock,
            side_effect=lambda emp_id: mock_detail_response if emp_id == 3 else None,
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Records List
            res_list = await client.get("/api/v1/modules/EMPLOYEE/records?status=ACTIVE")
            assert res_list.status_code == 200
            list_data = res_list.json()
            assert list_data["total"] == 1
            assert list_data["items"][0]["emp_code"] == "1002"

            # 2. Record Detail (200)
            res_detail = await client.get("/api/v1/modules/EMPLOYEE/records/3")
            assert res_detail.status_code == 200
            detail_data = res_detail.json()
            assert detail_data["emp_id"] == 3
            assert detail_data["full_name"] == "Kevin Shah"

            # 3. Record Detail (404)
            res_404 = await client.get("/api/v1/modules/EMPLOYEE/records/99999")
            assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_employee_exports():
    mock_csv_bytes = b"Employee ID,Employee Code\n3,1002\n"

    with (
        patch(
            "app.modules.employee.service.EmployeeService.export_employee_records",
            new_callable=AsyncMock,
            return_value=(mock_csv_bytes, "text/csv", "employees_active_csv.csv"),
        ),
        patch(
            "app.modules.employee.service.EmployeeService.export_quality_issues",
            new_callable=AsyncMock,
            return_value=(mock_csv_bytes, "text/csv", "quality_issue_dup_emp_code.csv"),
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Export records
            res1 = await client.get("/api/v1/modules/EMPLOYEE/records/export?status=ACTIVE")
            assert res1.status_code == 200
            assert "text/csv" in res1.headers["content-type"]
            assert b"Employee ID" in res1.content

            # Export quality
            res2 = await client.get("/api/v1/modules/EMPLOYEE/quality/export?issue=DUP_EMP_CODE")
            assert res2.status_code == 200
            assert "text/csv" in res2.headers["content-type"]
