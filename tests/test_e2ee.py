import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_post_e2ee(client: AsyncClient, header1: dict):
    header1.update({"X-Public-Key": "public", "X-Encrypted-Private-Key": "private"})
    response = await client.post("/e2ee/")
    assert response.status_code == 403

    response = await client.post("/e2ee/", headers=header1)
    assert response.status_code == 200
    assert response.json() == {"key": "public"}

    response = await client.post("/e2ee/", headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "E2EE already enabled."}

@pytest.mark.asyncio
async def test_get_e2ee(client: AsyncClient, header2: dict):
    response = await client.get("/e2ee/")
    assert response.status_code == 403

    response = await client.get("/e2ee/", params={"name": "test-1"}, headers=header2)
    assert response.status_code == 200
    assert response.json() == {"key": "public"}

    response = await client.get("/e2ee/", params={"name": "test-2"}, headers=header2)
    assert response.status_code == 400
    assert response.json() == {"detail": "User has not set up E2EE."}

    response = await client.get("/e2ee/", params={"name": "test-0"}, headers=header2)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}

@pytest.mark.asyncio
async def test_get_e2ee_private(client: AsyncClient, header1: dict, header2):
    response = await client.get("/e2ee/private")
    assert response.status_code == 403

    response = await client.get("/e2ee/private", headers=header1)
    assert response.status_code == 200
    assert response.json() == {"key": "private"}

    response = await client.get("/e2ee/private", headers=header2)
    assert response.status_code == 400
    assert response.json() == {"detail": "E2EE not set up."}

@pytest.mark.asyncio
async def test_get_e2ee_public(client: AsyncClient, header1: dict, header2):
    response = await client.get("/e2ee/public")
    assert response.status_code == 403

    response = await client.get("/e2ee/public", headers=header1)
    assert response.status_code == 200
    assert response.json() == {"key": "public"}

    response = await client.get("/e2ee/public", headers=header2)
    assert response.status_code == 400
    assert response.json() == {"detail": "E2EE not set up."}