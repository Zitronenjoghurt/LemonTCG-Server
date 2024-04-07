import pytest
from httpx import AsyncClient
from src.models.user_models import UserPublicInformation

@pytest.mark.asyncio
async def test_send_friend_request(client: AsyncClient, header1: dict, header2: dict):
    response = await client.post("/friend/request")
    assert response.status_code == 403

    response = await client.post("/friend/request", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 204

    response = await client.post("/friend/request", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "Already sent a request."}

    response = await client.post("/friend/request", params={"name": "test-1"}, headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "Can't add yourself as a friend."}

    response = await client.post("/friend/request", params={"name": "test-1"}, headers=header2)
    assert response.status_code == 204

    response = await client.post("/friend/request", params={"name": "test-0"}, headers=header2)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}

    # Check status
    response = await client.get("/friend/request", headers=header1)
    assert response.status_code == 200
    data = response.json()
    user_data = data.get("requests", [])[0].get("user")
    test2 = UserPublicInformation.model_validate(user_data)
    assert test2.name == "test-2"

    response = await client.get("/friend/request", headers=header2)
    assert response.status_code == 200
    data = response.json()
    user_data = data.get("requests", [])[0].get("user")
    test1 = UserPublicInformation.model_validate(user_data)
    assert test1.name == "test-1"

@pytest.mark.asyncio
async def test_retract_friend_request(client: AsyncClient, header1: dict, header2: dict):
    response = await client.delete("/friend/request")
    assert response.status_code == 403

    response = await client.delete("/friend/request", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 204

    response = await client.delete("/friend/request", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "No pending friend request with user."}

    response = await client.delete("/friend/request", params={"name": "test-1"}, headers=header2)
    assert response.status_code == 204

    response = await client.delete("/friend/request", params={"name": "test-0"}, headers=header2)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}

    # Check status
    response = await client.get("/friend/request", headers=header1)
    assert response.status_code == 200
    data = response.json()
    assert data.get("requests") == []

    response = await client.get("/friend/request", headers=header2)
    assert response.status_code == 200
    data = response.json()
    assert data.get("requests") == []

    # Resend requests
    await test_send_friend_request(client=client, header1=header1, header2=header2)

@pytest.mark.asyncio
async def test_deny_friend_request(client: AsyncClient, header1: dict, header2: dict):
    response = await client.post("/friend/request/deny")
    assert response.status_code == 403

    response = await client.post("/friend/request/deny", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 204

    response = await client.post("/friend/request/deny", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "No pending friend request with user."}

    response = await client.post("/friend/request/deny", params={"name": "test-1"}, headers=header2)
    assert response.status_code == 204

    response = await client.post("/friend/request/deny", params={"name": "test-0"}, headers=header2)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}

    # Check status
    response = await client.get("/friend/request", headers=header1)
    assert response.status_code == 200
    data = response.json()
    assert data.get("requests") == []

    response = await client.get("/friend/request", headers=header2)
    assert response.status_code == 200
    data = response.json()
    assert data.get("requests") == []

    # Resend requests
    await test_send_friend_request(client=client, header1=header1, header2=header2)

@pytest.mark.asyncio
async def test_accept_friend_request(client: AsyncClient, header1: dict, header2: dict):
    response = await client.post("/friend/request/accept")
    assert response.status_code == 403

    response = await client.post("/friend/request/accept", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 204

    response = await client.post("/friend/request/accept", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "Already on friendlist."}

    response = await client.post("/friend/request/accept", params={"name": "test-1"}, headers=header2)
    assert response.status_code == 400
    assert response.json() == {"detail": "Already on friendlist."}

    response = await client.post("/friend/request/accept", params={"name": "test-0"}, headers=header2)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}

    # Request friend
    response = await client.post("/friend/request", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "Already on friendlist."}

    # Check status
    response = await client.get("/friend/", headers=header1)
    assert response.status_code == 200
    data = response.json()
    user_data = data.get("friends", [])[0].get("user")
    test2 = UserPublicInformation.model_validate(user_data)
    assert test2.name == "test-2"

    response = await client.get("/friend/", headers=header2)
    assert response.status_code == 200
    data = response.json()
    user_data = data.get("friends", [])[0].get("user")
    test1 = UserPublicInformation.model_validate(user_data)
    assert test1.name == "test-1"

@pytest.mark.asyncio
async def test_remove_friend(client: AsyncClient, header1: dict, header2: dict):
    response = await client.delete("/friend/")
    assert response.status_code == 403

    response = await client.delete("/friend/", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 204

    response = await client.delete("/friend/", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "Not friends with user."}

    response = await client.delete("/friend/", params={"name": "test-2"}, headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "Not friends with user."}

    response = await client.delete("/friend/", params={"name": "test-0"}, headers=header2)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}

    # Check status
    response = await client.get("/friend/", headers=header1)
    assert response.status_code == 200
    data = response.json()
    assert data.get("friends") == []

    response = await client.get("/friend/", headers=header2)
    assert response.status_code == 200
    data = response.json()
    assert data.get("friends") == []

    # Accept non-existing request
    response = await client.post("/friend/request/accept", params={"name": "test-1"}, headers=header2)
    assert response.status_code == 400
    assert response.json() == {"detail": "No pending friend request with user."}