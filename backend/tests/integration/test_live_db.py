import pytest
from fastapi.testclient import TestClient

from app.db.mssql import test_connection as mssql_test_connection
from app.main import app


@pytest.mark.integration
def test_live_mssql_connection():
    """Live integration test against configured MSSQL instance.

    Skips gracefully if database is unreachable in local/CI environment.
    """
    is_connected = mssql_test_connection()
    if not is_connected:
        pytest.skip("Live MSSQL instance is not reachable in this environment.")
    assert is_connected is True


@pytest.mark.integration
def test_campaigns_against_real_mssql():
    """Live integration test calling campaign APIs against real MSSQL."""
    is_connected = mssql_test_connection()
    if not is_connected:
        pytest.skip("Live MSSQL instance is not reachable in this environment.")

    client = TestClient(app)
    response = client.get("/api/v1/campaigns")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
