from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_database_summary():
    mock_row = {
        "schema_count": 12,
        "table_count": 934,
        "column_count": 14682,
        "estimated_rows": 284021923,
    }
    with patch(
        "app.discovery.metadata.execute_readonly_query", return_value=[mock_row]
    ):
        response = client.get("/api/v1/database/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["schema_count"] == 12
        assert data["table_count"] == 934
        assert data["column_count"] == 14682
        assert data["estimated_rows"] == 284021923


def test_api_database_schemas():
    mock_rows = [
        {"name": "dbo", "table_count": 842},
        {"name": "audit", "table_count": 41},
    ]
    with patch("app.discovery.metadata.execute_readonly_query", return_value=mock_rows):
        response = client.get("/api/v1/database/schemas")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["items"][0]["name"] == "dbo"
        assert data["items"][0]["table_count"] == 842


def test_api_database_tables():
    mock_count = [{"total": 1}]
    mock_data = [
        {
            "schema": "dbo",
            "table": "DLPerson",
            "estimated_rows": 8242921,
            "column_count": 42,
        }
    ]
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_count, mock_data],
    ):
        response = client.get(
            "/api/v1/database/tables?schema=dbo&search=Person&limit=50&offset=0"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["schema"] == "dbo"
        assert data["items"][0]["table"] == "DLPerson"
        assert data["items"][0]["estimated_rows"] == 8242921
        assert data["items"][0]["column_count"] == 42


def test_api_single_table():
    mock_row = [
        {
            "schema": "dbo",
            "table": "DLPerson",
            "estimated_rows": 8242921,
            "column_count": 42,
        }
    ]
    with patch("app.discovery.metadata.execute_readonly_query", return_value=mock_row):
        response = client.get("/api/v1/database/tables/dbo/DLPerson")
        assert response.status_code == 200
        data = response.json()
        assert data["schema"] == "dbo"
        assert data["table"] == "DLPerson"
        assert data["estimated_rows"] == 8242921
        assert data["column_count"] == 42


def test_api_single_table_not_found():
    with patch("app.discovery.metadata.execute_readonly_query", return_value=[]):
        response = client.get("/api/v1/database/tables/dbo/NonExistent")
        assert response.status_code == 404


def test_api_table_columns():
    mock_exists = [{"exists_flag": 1}]
    mock_columns = [
        {
            "ordinal": 1,
            "name": "PersonID",
            "data_type": "bigint",
            "max_length": 8,
            "precision": 19,
            "scale": 0,
            "nullable": 0,
            "identity": 1,
            "computed": 0,
            "has_default": 0,
            "default_definition": None,
            "primary_key": 1,
            "foreign_key": 0,
        }
    ]
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_exists, mock_columns],
    ):
        response = client.get("/api/v1/database/tables/dbo/DLPerson/columns")
        assert response.status_code == 200
        data = response.json()
        assert data["schema"] == "dbo"
        assert data["table"] == "DLPerson"
        assert len(data["columns"]) == 1
        assert data["columns"][0]["name"] == "PersonID"
        assert data["columns"][0]["data_type"] == "bigint"
        assert data["columns"][0]["primary_key"] is True


def test_api_table_keys():
    mock_exists_pk = [{"exists_flag": 1}]
    mock_pk_rows = [
        {"constraint_name": "PK_Person", "column_name": "PersonID", "ordinal": 1}
    ]
    mock_exists_fk = [{"exists_flag": 1}]
    mock_fk_rows = []
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_exists_pk, mock_pk_rows, mock_exists_fk, mock_fk_rows],
    ):
        response = client.get("/api/v1/database/tables/dbo/DLPerson/keys")
        assert response.status_code == 200
        data = response.json()
        assert data["schema"] == "dbo"
        assert data["table"] == "DLPerson"
        assert data["primary_key"]["name"] == "PK_Person"
        assert data["foreign_keys"] == []


def test_api_table_indexes():
    mock_exists = [{"exists_flag": 1}]
    mock_idx_rows = [
        {
            "index_name": "PK_DLPerson",
            "type_desc": "CLUSTERED",
            "is_unique": 1,
            "is_primary_key": 1,
            "is_unique_constraint": 0,
            "is_disabled": 0,
            "column_name": "PersonID",
            "key_ordinal": 1,
            "is_descending_key": 0,
            "is_included_column": 0,
        }
    ]
    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_exists, mock_idx_rows],
    ):
        response = client.get("/api/v1/database/tables/dbo/DLPerson/indexes")
        assert response.status_code == 200
        data = response.json()
        assert data["schema"] == "dbo"
        assert len(data["indexes"]) == 1
        assert data["indexes"][0]["name"] == "PK_DLPerson"
        assert data["indexes"][0]["type"] == "CLUSTERED"
        assert data["indexes"][0]["unique"] is True


def test_api_table_structure():
    mock_table = [
        {
            "schema": "dbo",
            "table": "DLPerson",
            "estimated_rows": 100,
            "column_count": 1,
        }
    ]
    mock_exists_cols = [{"exists_flag": 1}]
    mock_cols = [
        {
            "ordinal": 1,
            "name": "PersonID",
            "data_type": "bigint",
            "max_length": 8,
            "precision": 19,
            "scale": 0,
            "nullable": 0,
            "identity": 1,
            "computed": 0,
            "has_default": 0,
            "default_definition": None,
            "primary_key": 1,
            "foreign_key": 0,
        }
    ]
    mock_exists_pk = [{"exists_flag": 1}]
    mock_pk = [
        {"constraint_name": "PK_Person", "column_name": "PersonID", "ordinal": 1}
    ]
    mock_exists_fk = [{"exists_flag": 1}]
    mock_fk = []
    mock_exists_idx = [{"exists_flag": 1}]
    mock_idx = []

    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[
            mock_table,
            mock_exists_cols,
            mock_cols,
            mock_exists_pk,
            mock_pk,
            mock_exists_fk,
            mock_fk,
            mock_exists_idx,
            mock_idx,
        ],
    ):
        response = client.get("/api/v1/database/tables/dbo/DLPerson/structure")
        assert response.status_code == 200
        data = response.json()
        assert data["table"]["table"] == "DLPerson"
        assert len(data["columns"]) == 1
        assert data["primary_key"]["name"] == "PK_Person"
        assert data["foreign_keys"] == []
        assert data["indexes"] == []


def test_api_table_sample():
    mock_table = [
        {
            "schema": "dbo",
            "table": "DLPerson",
            "estimated_rows": 100,
            "column_count": 1,
        }
    ]
    mock_exists_cols = [{"exists_flag": 1}]
    mock_cols = [
        {
            "ordinal": 1,
            "name": "PersonID",
            "data_type": "bigint",
            "max_length": 8,
            "precision": 19,
            "scale": 0,
            "nullable": 0,
            "identity": 1,
            "computed": 0,
            "has_default": 0,
            "default_definition": None,
            "primary_key": 1,
            "foreign_key": 0,
        }
    ]
    mock_exists_pk = [{"exists_flag": 1}]
    mock_pk = [
        {"constraint_name": "PK_Person", "column_name": "PersonID", "ordinal": 1}
    ]
    mock_sample_rows = [{"PersonID": 101}, {"PersonID": 102}]

    with (
        patch(
            "app.discovery.metadata.execute_readonly_query",
            side_effect=[
                mock_table,
                mock_exists_cols,
                mock_cols,
                mock_exists_pk,
                mock_pk,
            ],
        ),
        patch(
            "app.sampling.sampler.execute_readonly_query",
            return_value=mock_sample_rows,
        ),
    ):
        response = client.get("/api/v1/database/tables/dbo/DLPerson/sample?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert data["schema"] == "dbo"
        assert data["table"] == "DLPerson"
        assert data["requested_rows"] == 50
        assert data["returned_rows"] == 2
        assert data["columns"] == ["PersonID"]
        assert len(data["rows"]) == 2
        assert data["rows"][0]["PersonID"] == 101


def test_api_table_profile():
    mock_table = [
        {
            "schema": "dbo",
            "table": "DLPerson",
            "estimated_rows": 100,
            "column_count": 1,
        }
    ]
    mock_exists_cols = [{"exists_flag": 1}]
    mock_cols = [
        {
            "ordinal": 1,
            "name": "PersonID",
            "data_type": "bigint",
            "max_length": 8,
            "precision": 19,
            "scale": 0,
            "nullable": 0,
            "identity": 1,
            "computed": 0,
            "has_default": 0,
            "default_definition": None,
            "primary_key": 1,
            "foreign_key": 0,
        }
    ]
    mock_exists_pk = [{"exists_flag": 1}]
    mock_pk = [
        {"constraint_name": "PK_Person", "column_name": "PersonID", "ordinal": 1}
    ]
    mock_sample_rows = [{"PersonID": 101}, {"PersonID": 102}]

    with (
        patch(
            "app.discovery.metadata.execute_readonly_query",
            side_effect=[
                mock_table,
                mock_exists_cols,
                mock_cols,
                mock_exists_pk,
                mock_pk,
                mock_exists_cols,
                mock_cols,
            ],
        ),
        patch(
            "app.sampling.sampler.execute_readonly_query",
            return_value=mock_sample_rows,
        ),
    ):
        response = client.get("/api/v1/database/tables/dbo/DLPerson/profile?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert data["schema"] == "dbo"
        assert data["table"] == "DLPerson"
        assert len(data["columns"]) == 1
        assert data["columns"][0]["name"] == "PersonID"
        assert data["columns"][0]["profile_type"] == "numeric"
        assert data["columns"][0]["min"] == 101.0
        assert data["columns"][0]["max"] == 102.0


def test_api_table_classification():
    mock_exists_cols = [{"exists_flag": 1}]
    mock_cols = [
        {
            "ordinal": 1,
            "name": "PersonID",
            "data_type": "bigint",
            "max_length": 8,
            "precision": 19,
            "scale": 0,
            "nullable": 0,
            "identity": 1,
            "computed": 0,
            "has_default": 0,
            "default_definition": None,
            "primary_key": 1,
            "foreign_key": 0,
        },
        {
            "ordinal": 2,
            "name": "Email",
            "data_type": "nvarchar",
            "max_length": 100,
            "precision": 0,
            "scale": 0,
            "nullable": 1,
            "identity": 0,
            "computed": 0,
            "has_default": 0,
            "default_definition": None,
            "primary_key": 0,
            "foreign_key": 0,
        },
    ]

    with patch(
        "app.discovery.metadata.execute_readonly_query",
        side_effect=[mock_exists_cols, mock_cols],
    ):
        response = client.get("/api/v1/database/tables/dbo/DLPerson/classification")
        assert response.status_code == 200
        data = response.json()
        assert data["schema"] == "dbo"
        assert data["table"] == "DLPerson"
        assert len(data["columns"]) == 2
        assert data["columns"][0]["semantic_type"] == "IDENTIFIER"
        assert data["columns"][0]["confidence"] == 1.0
        assert data["columns"][1]["semantic_type"] == "EMAIL"
        assert data["columns"][1]["sensitivity"] == "PII"
        assert data["columns"][1]["expose_values"] is False
