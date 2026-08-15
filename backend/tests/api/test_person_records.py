from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.person.records_schemas import (
    PersonFullRootDetail,
    PersonListItem,
    PersonListResponse,
    PersonRecordDetailResponse,
)

MOCK_PERSON_ITEM = PersonListItem(
    PersonID=725850,
    PersonFirstName="John",
    PersonLastName="Doe",
    PersonTitle="Director",
    PersonDepartment="Ops",
)

MOCK_PERSON_FULL = PersonFullRootDetail(
    PersonID=725850,
    PersonFirstName="John",
    PersonLastName="Doe",
    PersonTitle="Director",
    PersonDepartment="Ops",
)

MOCK_PAGE_RESPONSE = PersonListResponse(
    total=1,
    limit=10,
    offset=0,
    items=[MOCK_PERSON_ITEM],
)

MOCK_DETAIL_RESPONSE = PersonRecordDetailResponse(
    person=MOCK_PERSON_FULL,
    addresses=[],
    contacts=[],
    companies=[],
    relations=[],
    documents=[],
    extra_fields=[],
    ims=[],
    ownership_history=[],
)


@pytest.mark.asyncio
async def test_get_person_records_list():
    with patch(
        "app.modules.person.records_service.PersonRecordsService.get_persons_list",
        new_callable=AsyncMock,
        return_value=MOCK_PAGE_RESPONSE,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/modules/PERSON/records?limit=10")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert data["limit"] == 10
            assert len(data["items"]) == 1
            assert data["items"][0]["PersonID"] == 725850
            assert data["items"][0]["PersonFirstName"] == "John"


@pytest.mark.asyncio
async def test_get_person_records_with_status_filter():
    with patch(
        "app.modules.person.records_service.PersonRecordsService.get_persons_list",
        new_callable=AsyncMock,
        return_value=MOCK_PAGE_RESPONSE,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/modules/PERSON/records?status=ACTIVE&limit=5")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_person_records_with_attribute_filter():
    with patch(
        "app.modules.person.records_service.PersonRecordsService.get_persons_list",
        new_callable=AsyncMock,
        return_value=MOCK_PAGE_RESPONSE,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/modules/PERSON/records?has_email=true&has_phone=true&limit=5"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_person_records_detail_not_found():
    with patch(
        "app.modules.person.records_service.PersonRecordsService.get_person_detail",
        new_callable=AsyncMock,
        return_value=None,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/modules/PERSON/records/999999999")
            assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_person_records_detail_full():
    with patch(
        "app.modules.person.records_service.PersonRecordsService.get_person_detail",
        new_callable=AsyncMock,
        return_value=MOCK_DETAIL_RESPONSE,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            detail_res = await ac.get("/api/v1/modules/PERSON/records/725850")
            assert detail_res.status_code == 200
            data = detail_res.json()
            assert "person" in data
            assert data["person"]["PersonID"] == 725850
