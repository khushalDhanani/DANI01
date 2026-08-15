from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_campaigns_list():
    response = client.get("/api/v1/campaigns")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    first = data[0]
    assert "CampID" in first
    assert "CampName" in first
    assert "TotalTransactions" in first


def test_get_campaign_detail():
    response = client.get("/api/v1/campaigns/1")
    assert response.status_code == 200
    data = response.json()
    assert data["CampID"] == 1
    assert "Items" in data
    assert "Events" in data
    assert isinstance(data["Items"], list)


def test_get_pr_transactions():
    response = client.get("/api/v1/campaigns/transactions?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 10
    if len(data["items"]) > 0:
        first = data["items"][0]
        assert "PRID" in first
        assert "RecipientName" in first


def test_get_pr_audit_logs():
    response = client.get("/api/v1/campaigns/audit-log?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 5
