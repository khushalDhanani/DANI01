from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

MOCK_CAMPAIGNS_RAW = [
    {
        "CampID": 1,
        "CampName": "Diwali - 2025",
        "CampStartDate": None,
        "CampReviewCutOfDate": None,
        "CampDelReminderDate": None,
        "TransCutOffDate": None,
        "CampCloseDate": None,
        "CampStatusID": 547,
        "CampStatus": "Close",
        "CampIsActive": True,
        "CreatedBy": "Admin",
        "CreatedAt": None,
        "TotalTransactions": 896,
        "ApprovedCount": 864,
        "PendingReviewCount": 0,
        "RejectedCount": 32,
        "DeliveredCount": 850,
    }
]

MOCK_ITEMS_RAW = [
    {
        "CampDetID": 1,
        "CampID": 1,
        "PRClassID": 1,
        "PRClassName": "Grade I",
        "ItemRefID": 22231,
        "ItemName": "Gift Box Big",
        "AdHocLimit": 50,
    }
]

MOCK_EVENTS_RAW = [
    {
        "ID": 1,
        "CampID": 1,
        "LocID": 8,
        "DLEventID": 157531,
        "EventSubject": "Diwali Event",
        "EventFromDate": None,
        "EventToDate": None,
    }
]

MOCK_TRANSACTIONS_RAW = [
    {
        "PRID": 1,
        "CampID": 1,
        "CampName": "Diwali - 2025",
        "PersonID": 725850,
        "RecipientName": "John Doe",
        "PersonTitle": "Director",
        "PersonDepartment": "Ops",
        "PersonPRClassID": 1,
        "PRClassName": "Grade I",
        "PRTypeID": 543,
        "PRTypeName": "Campaign",
        "CampReviewStatusID": 550,
        "ReviewStatusName": "Approved",
        "DeliveryTypeID": 553,
        "DeliveryTypeName": "Courier",
        "DeliveryStatusID": 555,
        "DeliveryStatusName": "Delivered",
        "PROwnerEmpID": 844,
        "OwnerName": "Alice Smith",
        "OwnerDepartment": "HR",
        "GiftOrderedDt": None,
        "IsReattempt": False,
        "IsActive": True,
    }
]

MOCK_AUDIT_LOGS_RAW = [
    {
        "TransactionID": 1,
        "CampID": 1,
        "CampName": "Diwali - 2025",
        "PRID": 1,
        "TransactionStatusID": 550,
        "StatusName": "Approved",
        "TransactionDesc": "Approved",
        "ModuleName": "PRReviewStatus",
        "TransactionMessage": "Approved order",
        "EntUser": "Alice Smith",
        "EntDt": None,
        "CorrelationIdStr": "45C83C57-AF8D-42B7-B0AB-41DC174265A2",
        "Severity": 1,
    }
]


@patch("app.modules.campaign.campaign_service.execute_readonly_query")
def test_get_campaigns_list(mock_query):
    mock_query.return_value = MOCK_CAMPAIGNS_RAW

    response = client.get("/api/v1/campaigns")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["CampID"] == 1
    assert data[0]["CampName"] == "Diwali - 2025"
    assert data[0]["TotalTransactions"] == 896


@patch("app.modules.campaign.campaign_service.execute_readonly_query")
def test_get_campaign_detail(mock_query):
    # First call in get_campaign_detail is get_campaign_summaries, second is items, third is events
    mock_query.side_effect = [MOCK_CAMPAIGNS_RAW, MOCK_ITEMS_RAW, MOCK_EVENTS_RAW]

    response = client.get("/api/v1/campaigns/1")
    assert response.status_code == 200
    data = response.json()
    assert data["CampID"] == 1
    assert len(data["Items"]) == 1
    assert data["Items"][0]["ItemName"] == "Gift Box Big"
    assert len(data["Events"]) == 1


@patch("app.modules.campaign.campaign_service.execute_readonly_query")
def test_get_campaign_detail_not_found(mock_query):
    mock_query.return_value = MOCK_CAMPAIGNS_RAW

    response = client.get("/api/v1/campaigns/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@patch("app.modules.campaign.campaign_service.execute_readonly_query")
def test_get_pr_transactions(mock_query):
    # First query for count, second query for items
    mock_query.side_effect = [[{"total": 1}], MOCK_TRANSACTIONS_RAW]

    response = client.get("/api/v1/campaigns/transactions?camp_id=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["PRID"] == 1
    assert data["items"][0]["RecipientName"] == "John Doe"
    assert data["items"][0]["OwnerName"] == "Alice Smith"


@patch("app.modules.campaign.campaign_service.execute_readonly_query")
def test_get_pr_audit_logs(mock_query):
    # First query for count, second query for items
    mock_query.side_effect = [[{"total": 1}], MOCK_AUDIT_LOGS_RAW]

    response = client.get("/api/v1/campaigns/audit-log?camp_id=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["TransactionID"] == 1
    assert data["items"][0]["EntUser"] == "Alice Smith"
