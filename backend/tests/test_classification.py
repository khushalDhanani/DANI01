from unittest.mock import MagicMock

from app.classification.classifier import TableClassifier
from app.classification.rules import classify_column_signals
from app.classification.taxonomy import SemanticType
from app.schemas.database import ColumnInfo


def test_classify_identifiers():
    pk_col = ColumnInfo(
        ordinal=1,
        name="PersonID",
        data_type="bigint",
        nullable=False,
        identity=True,
        computed=False,
        has_default=False,
        primary_key=True,
        foreign_key=False,
    )
    sem_type, conf, signals = classify_column_signals(pk_col)
    assert sem_type == SemanticType.IDENTIFIER
    assert conf == 1.0
    assert "primary_key" in signals
    assert "column_name_suffix_id" in signals

    fk_col = ColumnInfo(
        ordinal=2,
        name="CityID",
        data_type="bigint",
        nullable=True,
        identity=False,
        computed=False,
        has_default=False,
        primary_key=False,
        foreign_key=True,
    )
    sem_type, conf, signals = classify_column_signals(fk_col)
    assert sem_type == SemanticType.IDENTIFIER
    assert conf == 1.0
    assert "foreign_key" in signals


def test_classify_pii_and_sensitivity():
    email_col = ColumnInfo(
        ordinal=1,
        name="EmailAddress",
        data_type="nvarchar",
        nullable=True,
        identity=False,
        computed=False,
        has_default=False,
    )
    sem_type, conf, _signals = classify_column_signals(email_col)
    assert sem_type == SemanticType.EMAIL
    assert conf >= 0.95

    phone_col = ColumnInfo(
        ordinal=2,
        name="MobileNumber",
        data_type="varchar",
        nullable=True,
        identity=False,
        computed=False,
        has_default=False,
    )
    sem_type, _conf, _signals = classify_column_signals(phone_col)
    assert sem_type == SemanticType.PHONE


def test_classify_address_and_coordinates():
    lat_col = ColumnInfo(
        ordinal=1,
        name="Latitude",
        data_type="decimal",
        nullable=True,
        identity=False,
        computed=False,
        has_default=False,
    )
    assert classify_column_signals(lat_col)[0] == SemanticType.LATITUDE

    lng_col = ColumnInfo(
        ordinal=2,
        name="Longitude",
        data_type="decimal",
        nullable=True,
        identity=False,
        computed=False,
        has_default=False,
    )
    assert classify_column_signals(lng_col)[0] == SemanticType.LONGITUDE

    street_col = ColumnInfo(
        ordinal=3,
        name="Street",
        data_type="varchar",
        nullable=True,
        identity=False,
        computed=False,
        has_default=False,
    )
    assert classify_column_signals(street_col)[0] == SemanticType.STREET

    postal_col = ColumnInfo(
        ordinal=4,
        name="PostalCode",
        data_type="nvarchar",
        nullable=True,
        identity=False,
        computed=False,
        has_default=False,
    )
    assert classify_column_signals(postal_col)[0] == SemanticType.POSTAL_CODE


def test_classify_dates_and_status():
    ent_col = ColumnInfo(
        ordinal=1,
        name="PersonAddEntDt",
        data_type="datetime",
        nullable=False,
        identity=False,
        computed=False,
        has_default=False,
    )
    assert classify_column_signals(ent_col)[0] == SemanticType.CREATED_DATETIME

    upd_col = ColumnInfo(
        ordinal=2,
        name="PersonAddUpdDt",
        data_type="datetime",
        nullable=True,
        identity=False,
        computed=False,
        has_default=False,
    )
    assert classify_column_signals(upd_col)[0] == SemanticType.UPDATED_DATETIME

    active_col = ColumnInfo(
        ordinal=3,
        name="PersonAddIsActive",
        data_type="bit",
        nullable=False,
        identity=False,
        computed=False,
        has_default=False,
    )
    assert classify_column_signals(active_col)[0] == SemanticType.STATUS_FLAG


def test_table_classifier_service():
    mock_discovery = MagicMock()
    mock_discovery.get_columns.return_value = [
        ColumnInfo(
            ordinal=1,
            name="PersonID",
            data_type="bigint",
            nullable=False,
            identity=True,
            computed=False,
            has_default=False,
            primary_key=True,
        ),
        ColumnInfo(
            ordinal=2,
            name="Email",
            data_type="nvarchar",
            nullable=True,
            identity=False,
            computed=False,
            has_default=False,
        ),
    ]

    classifier = TableClassifier(discovery=mock_discovery)
    res = classifier.classify_table("dbo", "DLPerson")

    assert res.schema_name == "dbo"
    assert res.table == "DLPerson"
    assert len(res.columns) == 2

    c1 = res.columns[0]
    assert c1.name == "PersonID"
    assert c1.semantic_type == "IDENTIFIER"
    assert c1.sensitivity == "INTERNAL"
    assert c1.expose_values is True
    assert c1.confidence == 1.0

    c2 = res.columns[1]
    assert c2.name == "Email"
    assert c2.semantic_type == "EMAIL"
    assert c2.sensitivity == "PII"
    assert c2.expose_values is False
