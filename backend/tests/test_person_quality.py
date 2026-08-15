from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.exceptions import TableNotFoundError
from app.main import app
from app.modules.person.quality.engine import PersonQualityEngine
from app.modules.person.quality.models import (
    QualityCategory,
    QualityFindingStatus,
    QualitySeverity,
)
from app.modules.person.quality.rules.completeness import (
    PersonMissingAddressRule,
    PersonMissingCompanyLinkRule,
    PersonMissingContactRule,
    PersonMissingEmailRule,
    PersonMissingPhoneRule,
)
from app.modules.person.quality.rules.consistency import (
    PersonCreatedAfterUpdatedRule,
    PersonSelfRelationshipRule,
)
from app.modules.person.quality.rules.integrity import (
    PersonOrphanAddressRule,
    PersonOrphanCompanyLinkRule,
    PersonOrphanContactRule,
    PersonOrphanRelationshipRule,
)
from app.modules.person.quality.rules.validity import (
    PersonInvalidEmailRule,
    PersonInvalidLatitudeRule,
    PersonInvalidLongitudeRule,
    PersonInvalidPhoneRule,
    PersonInvalidUrlRule,
)
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
def mock_quality_discovery() -> MagicMock:
    discovery = MagicMock()

    def get_structure_side_effect(schema_name: str, table_name: str):
        if table_name == "DLPersonMst":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonMst", estimated_rows=1000, column_count=7),
                columns=[
                    make_col(1, "PersonID", "int"),
                    make_col(2, "PersonFirstName", "varchar"),
                    make_col(3, "PersonLastName", "varchar"),
                    make_col(4, "PersonIsActive", "bit"),
                    make_col(5, "PersonIsDeleted", "bit"),
                    make_col(6, "PersonEntDt", "datetime"),
                    make_col(7, "PersonUpdDt", "datetime"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonAddressDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonAddressDet", estimated_rows=500, column_count=9),
                columns=[
                    make_col(1, "PersonAddID", "int"),
                    make_col(2, "PersonID", "int"),
                    make_col(3, "Street", "varchar"),
                    make_col(4, "CityName", "varchar"),
                    make_col(5, "StateName", "varchar"),
                    make_col(6, "PostalCode", "varchar"),
                    make_col(7, "CountryID", "int"),
                    make_col(8, "Latitude", "float"),
                    make_col(9, "Longitude", "float"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonPhoneEmailURLDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonPhoneEmailURLDet", estimated_rows=800, column_count=6),
                columns=[
                    make_col(1, "PersonPhoneID", "int"),
                    make_col(2, "PersionID", "int"),
                    make_col(3, "LabelTypeID", "int"),
                    make_col(4, "TypeValue", "varchar"),
                    make_col(5, "PersonPhoneIsActive", "bit"),
                    make_col(6, "IsPrimary", "bit"),
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
        raise TableNotFoundError(schema_name, table_name)

    discovery.get_table_structure.side_effect = get_structure_side_effect
    return discovery


# ── 1. Completeness Rules Unit Tests ─────────────────────────────────


def test_missing_address_rule():
    rule = PersonMissingAddressRule()
    assert rule.category == QualityCategory.COMPLETENESS
    assert rule.severity == QualitySeverity.HIGH

    with patch("app.modules.person.quality.rules.completeness.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_active": 1000, "missing_addr": 250}]
        finding = rule.evaluate()

    assert finding.affected_count == 250
    assert finding.total_evaluated == 1000
    assert finding.affected_percent == 25.0
    assert finding.status == QualityFindingStatus.APPLIED


def test_missing_contact_rule():
    rule = PersonMissingContactRule()
    with patch("app.modules.person.quality.rules.completeness.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_active": 1000, "missing_contact": 10}]
        finding = rule.evaluate()

    assert finding.affected_count == 10
    assert finding.affected_percent == 1.0


def test_missing_email_rule():
    rule = PersonMissingEmailRule()
    with patch("app.modules.person.quality.rules.completeness.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_active": 500, "missing_email": 50}]
        finding = rule.evaluate()

    assert finding.affected_count == 50
    assert finding.affected_percent == 10.0


def test_missing_phone_rule():
    rule = PersonMissingPhoneRule()
    with patch("app.modules.person.quality.rules.completeness.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_active": 500, "missing_phone": 5}]
        finding = rule.evaluate()

    assert finding.affected_count == 5
    assert finding.affected_percent == 1.0


def test_missing_company_link_rule():
    rule = PersonMissingCompanyLinkRule()
    with patch("app.modules.person.quality.rules.completeness.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_active": 1000, "missing_company": 300}]
        finding = rule.evaluate()

    assert finding.affected_count == 300
    assert finding.affected_percent == 30.0


# ── 2. Validity Rules Unit Tests ─────────────────────────────────────


def test_invalid_email_rule():
    rule = PersonInvalidEmailRule()
    with patch("app.modules.person.quality.rules.validity.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_emails": 1000, "invalid_emails": 20}]
        finding = rule.evaluate()

    assert finding.category == QualityCategory.VALIDITY
    assert finding.affected_count == 20
    assert finding.affected_percent == 2.0


def test_invalid_phone_rule():
    rule = PersonInvalidPhoneRule()
    with patch("app.modules.person.quality.rules.validity.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_phones": 2000, "invalid_phones": 40}]
        finding = rule.evaluate()

    assert finding.affected_count == 40
    assert finding.affected_percent == 2.0


def test_invalid_url_rule():
    rule = PersonInvalidUrlRule()
    with patch("app.modules.person.quality.rules.validity.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_urls": 100, "invalid_urls": 0}]
        finding = rule.evaluate()

    assert finding.affected_count == 0
    assert finding.affected_percent == 0.0


def test_invalid_lat_long_rules():
    lat_rule = PersonInvalidLatitudeRule()
    long_rule = PersonInvalidLongitudeRule()

    with patch("app.modules.person.quality.rules.validity.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_lats": 50, "invalid_lats": 2}]
        finding_lat = lat_rule.evaluate()

    assert finding_lat.affected_count == 2
    assert finding_lat.affected_percent == 4.0

    with patch("app.modules.person.quality.rules.validity.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_longs": 50, "invalid_longs": 1}]
        finding_long = long_rule.evaluate()

    assert finding_long.affected_count == 1
    assert finding_long.affected_percent == 2.0


# ── 3. Integrity & Consistency Rules Unit Tests ──────────────────────


def test_orphan_rules():
    addr_rule = PersonOrphanAddressRule()
    contact_rule = PersonOrphanContactRule()
    comp_rule = PersonOrphanCompanyLinkRule()
    rel_rule = PersonOrphanRelationshipRule()

    with patch("app.modules.person.quality.rules.integrity.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_addresses": 500, "orphan_addresses": 0}]
        finding = addr_rule.evaluate()
        assert finding.affected_count == 0
        assert finding.severity == QualitySeverity.CRITICAL

    with patch("app.modules.person.quality.rules.integrity.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_contacts": 800, "orphan_contacts": 5}]
        finding = contact_rule.evaluate()
        assert finding.affected_count == 5

    with patch("app.modules.person.quality.rules.integrity.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_company_links": 300, "orphan_company_links": 0}]
        finding = comp_rule.evaluate()
        assert finding.affected_count == 0

    with patch("app.modules.person.quality.rules.integrity.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_relationships": 50, "orphan_relationships": 0}]
        finding = rel_rule.evaluate()
        assert finding.affected_count == 0


def test_consistency_rules():
    self_rel_rule = PersonSelfRelationshipRule()
    ts_rule = PersonCreatedAfterUpdatedRule()

    with patch("app.modules.person.quality.rules.consistency.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_relationships": 50, "self_relationships": 1}]
        finding = self_rel_rule.evaluate()
        assert finding.affected_count == 1
        assert finding.severity == QualitySeverity.HIGH

    with patch("app.modules.person.quality.rules.consistency.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_timestamped": 1000, "invalid_timestamps": 0}]
        finding = ts_rule.evaluate()
        assert finding.affected_count == 0


# ── 4. Engine & Applicability Tests ──────────────────────────────────


@pytest.mark.asyncio
async def test_person_quality_engine_execution(mock_quality_discovery: MagicMock):
    engine = PersonQualityEngine(discovery=mock_quality_discovery)

    with patch("app.db.mssql.execute_readonly_query") as mock_exec:
        # Provide responses for all executed rules
        mock_exec.return_value = [{"total_active": 1000, "missing_addr": 200, "total_emails": 500, "invalid_emails": 10, "total_addresses": 500, "orphan_addresses": 0}]
        res = await engine.evaluate_quality()

    assert res.module == "PERSON"
    assert res.status == "COMPLETED"
    assert res.rules_evaluated == 16
    assert res.rules_skipped == 0
    assert len(res.findings) == 16


@pytest.mark.asyncio
async def test_person_quality_engine_skipped_rule():
    # Discovery returns structure without Latitude and Longitude columns
    discovery = MagicMock()

    def get_structure_side_effect(schema_name: str, table_name: str):
        if table_name == "DLPersonMst":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonMst", estimated_rows=1000, column_count=5),
                columns=[
                    make_col(1, "PersonID", "int"),
                    make_col(2, "PersonFirstName", "varchar"),
                    make_col(3, "PersonLastName", "varchar"),
                    make_col(4, "PersonIsActive", "bit"),
                    make_col(5, "PersonIsDeleted", "bit"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        elif table_name == "DLPersonAddressDet":
            return TableStructureResponse(
                table=TableInfo(schema="dbo", table="DLPersonAddressDet", estimated_rows=500, column_count=4),
                columns=[
                    make_col(1, "PersonAddID", "int"),
                    make_col(2, "PersonID", "int"),
                    make_col(3, "Street", "varchar"),
                    make_col(4, "CityName", "varchar"),
                ],
                primary_key=None,
                foreign_keys=[],
                indexes=[],
            )
        raise TableNotFoundError(schema_name, table_name)

    discovery.get_table_structure.side_effect = get_structure_side_effect

    engine = PersonQualityEngine(discovery=discovery)

    with patch("app.db.mssql.execute_readonly_query") as mock_exec:
        mock_exec.return_value = [{"total_active": 1000, "missing_addr": 100}]
        res = await engine.evaluate_quality()

    assert res.status == "DEGRADED"
    assert res.rules_skipped > 0
    skipped_findings = [f for f in res.findings if f.status == QualityFindingStatus.SKIPPED]
    assert len(skipped_findings) > 0
    assert any(f.rule_code == "PERSON_INVALID_LATITUDE" for f in skipped_findings)


@pytest.mark.asyncio
async def test_person_quality_engine_rule_isolation(mock_quality_discovery: MagicMock):
    engine = PersonQualityEngine(discovery=mock_quality_discovery)

    # Patch first rule evaluate to fail with an exception
    first_rule = engine.registry.get_all_rules()[0]
    with patch.object(first_rule, "evaluate", side_effect=Exception("Simulated DB connection error")):
        with patch("app.db.mssql.execute_readonly_query", return_value=[{"total_active": 100, "missing_addr": 0, "total_emails": 100, "invalid_emails": 0}]):
            res = await engine.evaluate_quality()

    # The engine should isolate the failure for the first rule and succeed for the rest
    assert res.module == "PERSON"
    assert res.findings[0].status == QualityFindingStatus.FAILED
    assert "Simulated DB connection error" in res.findings[0].message
    assert any(f.status == QualityFindingStatus.APPLIED for f in res.findings[1:])


# ── 5. API Integration Tests ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_person_quality_api_endpoint(mock_quality_discovery: MagicMock):
    from app.api.dependencies import get_discovery_service

    app.dependency_overrides[get_discovery_service] = lambda: mock_quality_discovery

    try:
        with patch("app.db.mssql.execute_readonly_query") as mock_exec:
            mock_exec.return_value = [{"total_active": 1000, "missing_addr": 100}]
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/v1/modules/PERSON/quality")
                assert res.status_code == 200
                data = res.json()
                assert data["module"] == "PERSON"
                assert "severity_summary" in data
                assert "findings" in data
                assert len(data["findings"]) == 16
    finally:
        app.dependency_overrides.clear()
