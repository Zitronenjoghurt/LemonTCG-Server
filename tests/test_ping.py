import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_ping(client: AsyncClient, header1: dict, header2: dict):
    response = await client.get("/ping")
    assert response.status_code == 403

    response = await client.get("/ping", headers=header1)
    assert response.status_code == 200
    assert response.json() == {"message": "Pong"}

    response = await client.get("/ping", headers=header2)
    assert response.status_code == 200
    assert response.json() == {"message": "Pong"}