import pytest
from httpx import AsyncClient
from src.entities.room import MAX_ROOM_COUNT
from src.models.room_models import RoomCreationSuccess, RoomInformation

@pytest.fixture
async def room(client: AsyncClient, header1: dict):
    response = await client.post("/room/create")
    assert response.status_code == 403

    response = await client.post("/room/create", headers=header1)
    assert response.status_code == 201
    data = RoomCreationSuccess.model_validate(response.json())
    return data.code

@pytest.mark.asyncio
async def test_room_status(client: AsyncClient, header1: dict, room):
    code = await room

    response = await client.get("/room/status")
    assert response.status_code == 403

    response = await client.get("/room/status", params={"code": "donkey"}, headers=header1)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not found."}

    response = await client.get("/room/status", params={"code": code}, headers=header1)
    assert response.status_code == 200
    data = RoomInformation.model_validate(response.json())
    assert data.code == code
    assert data.owner_name == "test-1"
    assert data.opponent_name is None
    assert data.owner_ready is False
    assert data.opponent_ready is False
    assert data.is_ready is False

    # Leave room
    response = await client.post("/room/leave", params={"code": code}, headers=header1)
    assert response.status_code == 200
    assert response.json() == {"message": "Room closed."}

@pytest.mark.asyncio
async def test_room_leave(client: AsyncClient, header1: dict, header2: dict, room):
    code = await room

    response = await client.post("/room/leave")
    assert response.status_code == 403

    response = await client.post("/room/leave", params={"code": "donkey"}, headers=header1)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not found."}

    response = await client.post("/room/leave", params={"code": code}, headers=header2)
    assert response.status_code == 400
    assert response.json() == {"detail": "Not a participant of the room."}

    response = await client.post("/room/join", params={"code": code}, headers=header2)
    assert response.status_code == 204

    response = await client.post("/room/leave", params={"code": code}, headers=header2)
    assert response.status_code == 200
    assert response.json() == {"message": "Left room."}

    response = await client.post("/room/leave", params={"code": code}, headers=header1)
    assert response.status_code == 200
    assert response.json() == {"message": "Room closed."}

    # Check status
    response = await client.get("/room/status", params={"code": code}, headers=header1)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not found."}

@pytest.mark.asyncio
async def test_room_join(client: AsyncClient, header1: dict, header2: dict, header3: dict, room):
    code = await room

    response = await client.post("/room/join")
    assert response.status_code == 403

    response = await client.post("/room/join", params={"code": "donkey"}, headers=header1)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not found."}

    response = await client.post("/room/join", params={"code": code}, headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "Can't join your own room."}

    response = await client.post("/room/join", params={"code": code}, headers=header2)
    assert response.status_code == 204

    response = await client.post("/room/join", params={"code": code}, headers=header2)
    assert response.status_code == 400
    assert response.json() == {"detail": "Already joined the room."}

    response = await client.post("/room/join", params={"code": code}, headers=header3)
    assert response.status_code == 400
    assert response.json() == {"detail": "Room is full."}

    # check status
    response = await client.get("/room/status", params={"code": code}, headers=header1)
    assert response.status_code == 200
    data = RoomInformation.model_validate(response.json())
    assert data.code == code
    assert data.owner_name == "test-1"
    assert data.opponent_name == "test-2"
    assert data.owner_ready is False
    assert data.opponent_ready is False
    assert data.is_ready is False

    # Leave room
    response = await client.post("/room/leave", params={"code": code}, headers=header1)
    assert response.status_code == 200
    assert response.json() == {"message": "Room closed."}

@pytest.mark.asyncio
async def test_room_ready(client: AsyncClient, header1: dict, header2: dict, room):
    code = await room

    response = await client.post("/room/ready")
    assert response.status_code == 403

    response = await client.post("/room/ready", params={"code": "donkey", "state": True}, headers=header1)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not found."}

    response = await client.post("/room/ready", params={"code": code, "state": True}, headers=header2)
    assert response.status_code == 400
    assert response.json() == {"detail": "Not a participant of the room."}

    response = await client.post("/room/join", params={"code": code}, headers=header2)
    assert response.status_code == 204

    response = await client.post("/room/ready", params={"code": code, "state": True}, headers=header1)
    assert response.status_code == 204

    response = await client.post("/room/ready", params={"code": code, "state": True}, headers=header2)
    assert response.status_code == 204

    # Check Status
    response = await client.get("/room/status", params={"code": code}, headers=header1)
    assert response.status_code == 200
    data = RoomInformation.model_validate(response.json())
    assert data.code == code
    assert data.owner_name == "test-1"
    assert data.opponent_name == "test-2"
    assert data.owner_ready is True
    assert data.opponent_ready is True
    assert data.is_ready is True

    response = await client.post("/room/ready", params={"code": code, "state": False}, headers=header1)
    assert response.status_code == 204

    # Check Status
    response = await client.get("/room/status", params={"code": code}, headers=header1)
    assert response.status_code == 200
    data = RoomInformation.model_validate(response.json())
    assert data.code == code
    assert data.owner_name == "test-1"
    assert data.opponent_name == "test-2"
    assert data.owner_ready is False
    assert data.opponent_ready is True
    assert data.is_ready is False

    # Leave room
    response = await client.post("/room/leave", params={"code": code}, headers=header1)
    assert response.status_code == 200
    assert response.json() == {"message": "Room closed."}

@pytest.mark.asyncio
async def test_room_limit(client: AsyncClient, header1: dict):
    for _ in range(MAX_ROOM_COUNT):
        await client.post("/room/create", headers=header1)

    response = await client.post("/room/create", headers=header1)
    assert response.status_code == 400
    assert response.json() == {"detail": "Maximum room limit reached."}