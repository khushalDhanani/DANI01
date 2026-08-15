from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data


def test_database_health_connected():
    with patch("app.api.routes.health.test_connection", return_value=True):
        response = client.get("/api/v1/health/database")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "database": "connected"}


def test_database_health_disconnected():
    with patch("app.api.routes.health.test_connection", return_value=False):
        response = client.get("/api/v1/health/database")
        assert response.status_code == 200
        assert response.json() == {"status": "error", "database": "disconnected"}
