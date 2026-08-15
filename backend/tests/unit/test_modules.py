from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.exceptions import TableNotFoundError
from app.main import app
from app.modules.analyzer import ModuleAnalyzer
from app.modules.models import (
    ModuleDefinition,
    ModuleRelationshipDefinition,
    ModuleTableDefinition,
    ModuleTableRole,
    ModuleValidationStatus,
)
from app.modules.registry import DuplicateModuleError, ModuleRegistry
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
def sample_definition() -> ModuleDefinition:
    return ModuleDefinition(
        code="TEST_PERSON",
        name="Test Person Module",
        description="Test description for person domain.",
        root_schema="dbo",
        root_table="DLPerson",
        root_key="PersonID",
        tables=[
            ModuleTableDefinition(
                schema="dbo",
                table="DLPerson",
                role=ModuleTableRole.ROOT,
                required=True,
                key_columns=["PersonID"],
                important_columns=["FirstName", "LastName", "Email"],
            ),
            ModuleTableDefinition(
                schema="dbo",
                table="DLPersonAddressDet",
                role=ModuleTableRole.DETAIL,
                required=False,
                key_columns=["AddressID", "PersonID"],
                important_columns=["City", "PostalCode"],
            ),
        ],
        relationships=[
            ModuleRelationshipDefinition(
                parent_table="dbo.DLPerson",
                child_table="dbo.DLPersonAddressDet",
                parent_key="PersonID",
                child_key="PersonID",
                relationship_type="ONE_TO_MANY",
            )
        ],
        enabled=True,
        tags=["test"],
    )


@pytest.fixture
def mock_discovery() -> MagicMock:
    discovery = MagicMock()

    def get_structure_side_effect(schema_name: str, table_name: str):
        if table_name == "DLPerson":
            return TableStructureResponse(
                table=TableInfo(
                    schema="dbo", table="DLPerson", estimated_rows=1000, column_count=4
                ),
                columns=[
                    make_col(1, "PersonID", "int"),
                    make_col(2, "FirstName", "varchar"),
                    make_col(3, "LastName", "varchar"),
                    make_col(4, "Email", "varchar"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonAddressDet":
            return TableStructureResponse(
                table=TableInfo(
                    schema="dbo", table="DLPersonAddressDet", estimated_rows=500, column_count=4
                ),
                columns=[
                    make_col(1, "AddressID", "int"),
                    make_col(2, "PersonID", "int"),
                    make_col(3, "City", "varchar"),
                    make_col(4, "PostalCode", "varchar"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        raise TableNotFoundError(schema_name, table_name)

    discovery.get_table_structure.side_effect = get_structure_side_effect
    return discovery


# ── 1. Registry Unit Tests ──────────────────────────────────────────


def test_module_registration_and_lookup(sample_definition: ModuleDefinition):
    registry = ModuleRegistry()
    registry.register(sample_definition)

    found = registry.get("TEST_PERSON")
    assert found is not None
    assert found.name == "Test Person Module"
    assert found.root_table == "DLPerson"

    # Case-insensitive
    found_lower = registry.get("test_person")
    assert found_lower is not None
    assert found_lower.code == "TEST_PERSON"

    all_mods = registry.list_all()
    assert len(all_mods) == 1

    info_list = registry.list_info()
    assert len(info_list) == 1
    assert info_list[0].table_count == 2

    # Unregister
    assert registry.unregister("TEST_PERSON") is True
    assert registry.get("TEST_PERSON") is None


def test_duplicate_code_rejection(sample_definition: ModuleDefinition):
    registry = ModuleRegistry()
    registry.register(sample_definition)

    with pytest.raises(DuplicateModuleError):
        registry.register(sample_definition)


# ── 2. Validator Unit Tests ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_module_validation_success(
    sample_definition: ModuleDefinition, mock_discovery: MagicMock
):
    analyzer = ModuleAnalyzer(discovery=mock_discovery)
    result = await analyzer.validate(sample_definition)

    assert result.is_valid is True
    assert result.status == ModuleValidationStatus.READY
    assert result.root_table_exists is True
    assert result.root_key_exists is True
    assert result.tables_found == 2
    assert result.tables_missing == 0
    assert len(result.validation_errors) == 0


@pytest.mark.asyncio
async def test_module_validation_missing_root(sample_definition: ModuleDefinition):
    empty_discovery = MagicMock()
    empty_discovery.get_table_structure.side_effect = TableNotFoundError("dbo", "DLPerson")

    analyzer = ModuleAnalyzer(discovery=empty_discovery)
    result = await analyzer.validate(sample_definition)

    assert result.is_valid is False
    assert result.status == ModuleValidationStatus.INVALID
    assert result.root_table_exists is False
    assert any("Root table" in err for err in result.validation_errors)


@pytest.mark.asyncio
async def test_module_validation_missing_root_key(mock_discovery: MagicMock):
    # Definition with non-existent root key
    bad_key_def = ModuleDefinition(
        code="BAD_KEY",
        name="Bad Key Module",
        description="Testing bad root key",
        root_schema="dbo",
        root_table="DLPerson",
        root_key="NonExistentKeyID",
        tables=[],
    )

    analyzer = ModuleAnalyzer(discovery=mock_discovery)
    result = await analyzer.validate(bad_key_def)

    assert result.is_valid is False
    assert result.status == ModuleValidationStatus.INVALID
    assert result.root_table_exists is True
    assert result.root_key_exists is False
    assert any("Root key" in err for err in result.validation_errors)


@pytest.mark.asyncio
async def test_module_validation_missing_optional_table(sample_definition: ModuleDefinition):
    # Only root table exists, optional detail table DLPersonAddressDet is missing
    partial_discovery = MagicMock()

    def get_structure_side_effect(schema_name: str, table_name: str):
        if table_name == "DLPerson":
            return TableStructureResponse(
                table=TableInfo(
                    schema="dbo", table="DLPerson", estimated_rows=1000, column_count=4
                ),
                columns=[
                    make_col(1, "PersonID", "int"),
                    make_col(2, "FirstName", "varchar"),
                    make_col(3, "LastName", "varchar"),
                    make_col(4, "Email", "varchar"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        raise TableNotFoundError(schema_name, table_name)

    partial_discovery.get_table_structure.side_effect = get_structure_side_effect

    analyzer = ModuleAnalyzer(discovery=partial_discovery)
    result = await analyzer.validate(sample_definition)

    # Optional table missing -> Status should be DEGRADED (not INVALID), is_valid should be True
    assert result.is_valid is True
    assert result.status == ModuleValidationStatus.DEGRADED
    assert result.tables_found == 1
    assert result.tables_missing == 1
    assert len(result.validation_warnings) > 0


@pytest.mark.asyncio
async def test_module_validation_missing_column(mock_discovery: MagicMock):
    def_with_bad_col = ModuleDefinition(
        code="BAD_COL",
        name="Bad Col",
        description="Testing missing column",
        root_schema="dbo",
        root_table="DLPerson",
        root_key="PersonID",
        tables=[
            ModuleTableDefinition(
                schema="dbo",
                table="DLPerson",
                role=ModuleTableRole.ROOT,
                required=True,
                key_columns=["PersonID"],
                important_columns=["NonExistentColumn"],
            )
        ],
    )

    analyzer = ModuleAnalyzer(discovery=mock_discovery)
    result = await analyzer.validate(def_with_bad_col)

    assert result.is_valid is False
    assert result.status == ModuleValidationStatus.INVALID
    assert any("NonExistentColumn" in err for err in result.validation_errors)


# ── 3. API Integration Tests ────────────────────────────────────────


@pytest.mark.asyncio
async def test_module_api_list_and_get(sample_definition: ModuleDefinition):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # GET /api/v1/modules
        res = await client.get("/api/v1/modules")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # Person module is pre-registered

        # GET /api/v1/modules/PERSON
        res_get = await client.get("/api/v1/modules/PERSON")
        assert res_get.status_code == 200
        mod = res_get.json()
        assert mod["code"] == "PERSON"
        assert mod["root_table"] == "DLPersonMst"

        # GET /api/v1/modules/UNKNOWN_MOD (404)
        res_404 = await client.get("/api/v1/modules/UNKNOWN_MOD")
        assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_module_api_validate(mock_discovery: MagicMock):
    from app.api.dependencies import get_discovery_service

    app.dependency_overrides[get_discovery_service] = lambda: mock_discovery

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/modules/PERSON/validate")
            assert res.status_code == 200
            val = res.json()
            assert val["code"] == "PERSON"
            assert "status" in val
            assert "table_validations" in val
    finally:
        app.dependency_overrides.clear()
