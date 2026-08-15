from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.exceptions import TableNotFoundError
from app.main import app
from app.modules.person.analyzer import PersonModuleAnalyzer
from app.modules.person.metrics import PersonMetricsService, safe_percent
from app.modules.person.queries import build_person_metrics_query
from app.schemas.database import ColumnInfo, TableInfo, TableStructureResponse


def make_col(ordinal: int, name: str, data_type: str = "varchar") -> ColumnInfo:
    return ColumnInfo(
        ordinal=ordinal,
        name=name,
        data_type=data_type,
        nullable=True,
        identity=False,
        computed=False,
        has_default=False,
    )


@pytest.fixture
def mock_person_discovery() -> MagicMock:
    discovery = MagicMock()

    def get_structure_side_effect(schema_name: str, table_name: str):
        if table_name == "DLPersonMst":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonMst", estimated_rows=1000, column_count=8),
                columns=[
                    make_col(1, "PersonID", "int"),
                    make_col(2, "PersonFirstName", "varchar"),
                    make_col(3, "PersonLastName", "varchar"),
                    make_col(4, "PersonIsActive", "bit"),
                    make_col(5, "PersonIsDeleted", "bit"),
                    make_col(6, "PersonIsTemp", "bit"),
                    make_col(7, "PersonIsBlackList", "bit"),
                    make_col(8, "PersonEntDt", "datetime"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonAddressDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonAddressDet", estimated_rows=500, column_count=11),
                columns=[
                    make_col(1, "PersonAddID", "int"),
                    make_col(2, "PersonID", "int"),
                    make_col(3, "Street", "varchar"),
                    make_col(4, "CityName", "varchar"),
                    make_col(5, "StateName", "varchar"),
                    make_col(6, "PostalCode", "varchar"),
                    make_col(7, "CountryID", "int"),
                    make_col(8, "PersonAddIsActive", "bit"),
                    make_col(9, "Latitude", "float"),
                    make_col(10, "Longitude", "float"),
                    make_col(11, "GoogleFormattedAddress", "varchar"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonPhoneEmailURLDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonPhoneEmailURLDet", estimated_rows=800, column_count=7),
                columns=[
                    make_col(1, "PersonPhoneID", "int"),
                    make_col(2, "PersionID", "int"),
                    make_col(3, "LabelTypeID", "int"),
                    make_col(4, "TypeValue", "varchar"),
                    make_col(5, "PersonPhoneIsActive", "bit"),
                    make_col(6, "IsVerified", "bit"),
                    make_col(7, "IsPrimary", "bit"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonCompanyLinkDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonCompanyLinkDet", estimated_rows=300, column_count=5),
                columns=[
                    make_col(1, "PersonLinkID", "int"),
                    make_col(2, "PersonID", "int"),
                    make_col(3, "DLCompID", "int"),
                    make_col(4, "CompPersonRoleID", "int"),
                    make_col(5, "IsPrimary", "bit"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonRelationDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonRelationDet", estimated_rows=50, column_count=4),
                columns=[
                    make_col(1, "PersonRelationID", "int"),
                    make_col(2, "PersonID", "int"),
                    make_col(3, "RelatedPersonID", "int"),
                    make_col(4, "RelationShipTypeID", "int"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonDocumentDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonDocumentDet", estimated_rows=0, column_count=5),
                columns=[
                    make_col(1, "PersonDocID", "int"),
                    make_col(2, "PersonID", "int"),
                    make_col(3, "PersonDocDesc", "varchar"),
                    make_col(4, "PersonDocExtention", "varchar"),
                    make_col(5, "PersonDocIsReadOnly", "bit"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonExtraFieldValueDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonExtraFieldValueDet", estimated_rows=100, column_count=5),
                columns=[
                    make_col(1, "PersonExtraFieldValueID", "int"),
                    make_col(2, "PersonID", "int"),
                    make_col(3, "ExtraFieldID", "int"),
                    make_col(4, "PersonExtraFieldValue", "varchar"),
                    make_col(5, "PersonExtraFieldIsActive", "bit"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonIMDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonIMDet", estimated_rows=10, column_count=4),
                columns=[
                    make_col(1, "PersonIMID", "int"),
                    make_col(2, "PersionID", "int"),
                    make_col(3, "LabelTypeIMID", "int"),
                    make_col(4, "TypeValue", "varchar"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        raise TableNotFoundError(schema_name, table_name)

    discovery.get_table_structure.side_effect = get_structure_side_effect
    return discovery


# ── 1. Helper Unit Tests ──────────────────────────────────────────


def test_safe_percent():
    assert safe_percent(50, 100) == 50.0
    assert safe_percent(1, 3) == 33.33
    assert safe_percent(0, 100) == 0.0
    assert safe_percent(10, 0) == 0.0
    assert safe_percent(None, 100) is None


def test_build_person_metrics_query_basic():
    query = build_person_metrics_query(
        root_table="dbo.DLPersonMst",
    )
    assert "COUNT_BIG(1) AS total_persons" in query
    assert "FROM dbo.DLPersonMst p" in query


# ── 2. Service Unit Tests ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_person_metrics_calculation_success(mock_person_discovery: MagicMock):
    service = PersonMetricsService(discovery=mock_person_discovery)

    mock_db_row = {
        "total_persons": 1000,
        "active_persons": 950,
        "inactive_persons": 50,
        "deleted_persons": 10,
        "temp_persons": 5,
        "active_contacts": 900,
    }
    mock_child_counts = {
        "total_relationships": 15,
    }

    with patch("app.modules.person.metrics.execute_readonly_query") as mock_exec:
        mock_exec.side_effect = [[mock_db_row], [mock_child_counts]]
        res = await service.calculate_metrics()

    assert res.status == "COMPLETED"
    assert res.module == "PERSON"
    assert res.root_entity == "dbo.DLPersonMst"
    assert res.metrics.total_persons == 1000
    assert res.metrics.active_persons == 950
    assert res.metrics.active_percent == 95.0
    assert res.metrics.inactive_persons == 50
    assert res.metrics.inactive_percent == 5.0


@pytest.mark.asyncio
async def test_person_metrics_zero_persons(mock_person_discovery: MagicMock):
    service = PersonMetricsService(discovery=mock_person_discovery)

    mock_db_row = {
        "total_persons": 0,
        "active_persons": 0,
        "inactive_persons": 0,
    }

    with patch("app.modules.person.metrics.execute_readonly_query") as mock_exec:
        mock_exec.side_effect = [[mock_db_row], [{"total_relationships": 0}]]
        res = await service.calculate_metrics()

    assert res.status == "COMPLETED"
    assert res.metrics.total_persons == 0
    assert res.metrics.active_percent == 0.0


@pytest.mark.asyncio
async def test_person_metrics_missing_root_table():
    discovery = MagicMock()
    discovery.get_table_structure.side_effect = TableNotFoundError("dbo", "DLPersonMst")
    service = PersonMetricsService(discovery=discovery)

    res = await service.calculate_metrics()
    assert res.status == "FAILED"
    assert res.metrics.total_persons == 0
    assert len(res.warnings) > 0


# ── 3. Analyzer Integration Tests ─────────────────────────────────


@pytest.mark.asyncio
async def test_person_analyzer_integration(mock_person_discovery: MagicMock):
    analyzer = PersonModuleAnalyzer(discovery=mock_person_discovery)

    mock_db_row = {
        "total_persons": 500,
        "active_persons": 450,
        "active_contacts": 0,
    }
    mock_child_counts = {
        "total_relationships": 5,
    }

    with patch("app.modules.person.metrics.execute_readonly_query") as mock_exec:
        mock_exec.side_effect = [[mock_db_row], [mock_child_counts]]
        res = await analyzer.analyze_metrics()

    assert res.module == "PERSON"
    assert res.status == "COMPLETED"
    assert res.metrics.total_persons == 500
    assert res.metrics.active_percent == 90.0


# ── 4. API Route Integration Tests ────────────────────────────────


@pytest.mark.asyncio
async def test_person_metrics_api_endpoint(mock_person_discovery: MagicMock):
    from app.api.dependencies import get_discovery_service

    app.dependency_overrides[get_discovery_service] = lambda: mock_person_discovery

    mock_db_row = {
        "total_persons": 1000,
        "active_persons": 900,
        "active_contacts": 900,
    }
    mock_child_counts = {
        "total_relationships": 20,
    }

    try:
        with patch("app.modules.person.metrics.execute_readonly_query") as mock_exec:
            mock_exec.side_effect = [[mock_db_row], [mock_child_counts]]
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/v1/modules/PERSON/metrics")
                assert res.status_code == 200
                data = res.json()
                assert data["module"] == "PERSON"
                assert data["status"] == "COMPLETED"
                assert data["metrics"]["total_persons"] == 1000
                assert data["metrics"]["active_percent"] == 90.0
    finally:
        app.dependency_overrides.clear()
