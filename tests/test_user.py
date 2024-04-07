import pytest
from httpx import AsyncClient
from src.models.user_models import UserPrivateInformation, UserPublicInformation

@pytest.mark.asyncio
async def test_get_private_information(client: AsyncClient, header1: dict, header2: dict):
    response = await client.get("/user/")
    assert response.status_code == 403

    response = await client.get("/user/", headers=header1)
    assert response.status_code == 200
    test1 = UserPrivateInformation.model_validate(response.json())
    assert test1.name == "test-1"
    assert test1.display_name == "test-1"

    response = await client.get("/user/", headers=header2)
    assert response.status_code == 200
    test2 = UserPrivateInformation.model_validate(response.json())
    assert test2.name == "test-2"
    assert test2.display_name == "test-2"

@pytest.mark.asyncio
async def test_get_public_information(client: AsyncClient, header1: dict):
    response = await client.get("/user/search")
    assert response.status_code == 403

    response = await client.get("/user/search", params={"name": "test-1"}, headers=header1)
    assert response.status_code == 200
    test1 = UserPublicInformation.model_validate(response.json())
    assert test1.name == "test-1"
    assert test1.display_name == "test-1"

    response = await client.get("/user/search", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 200
    test2 = UserPublicInformation.model_validate(response.json())
    assert test2.name == "test-2"
    assert test2.display_name == "test-2"

    response = await client.get("/user/search", params={"name": "test-0"}, headers=header1)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}