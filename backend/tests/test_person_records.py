import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_get_person_records_list():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/modules/PERSON/records?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert "limit" in data
        assert data["limit"] == 10
        assert isinstance(data["items"], list)
        if len(data["items"]) > 0:
            first = data["items"][0]
            assert "PersonID" in first
            assert "PersonFirstName" in first


@pytest.mark.asyncio
async def test_get_person_records_with_status_filter():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/modules/PERSON/records?status=ACTIVE&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data


@pytest.mark.asyncio
async def test_get_person_records_with_attribute_filter():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/api/v1/modules/PERSON/records?has_email=true&has_phone=true&limit=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data


@pytest.mark.asyncio
async def test_get_person_records_detail_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/modules/PERSON/records/999999999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_person_records_detail_full():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # First get a valid PersonID
        list_res = await ac.get("/api/v1/modules/PERSON/records?limit=1")
        assert list_res.status_code == 200
        items = list_res.json().get("items", [])
        if items:
            person_id = items[0]["PersonID"]
            detail_res = await ac.get(f"/api/v1/modules/PERSON/records/{person_id}")
            assert detail_res.status_code == 200
            data = detail_res.json()
            assert "person" in data
            assert "addresses" in data
            assert "contacts" in data
            assert "companies" in data
            assert "relations" in data
            assert "documents" in data
            assert "extra_fields" in data
            assert "ims" in data
            assert data["person"]["PersonID"] == person_id
