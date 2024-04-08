import pytest
import websockets
from datetime import datetime
from src.models.pm_models import WsRcvMessage, WsResponse

@pytest.mark.asyncio
async def test_pm_websocket(header1: dict, header2: dict):
    uri = "ws://localhost:8000/pm/ws"

    try:
        async with websockets.connect(uri):
            pass
    except websockets.InvalidStatusCode as e:
        assert e.status_code == 403

    try:
        async with websockets.connect(uri, extra_headers={"X-API-Key": "Dongo"}):
            pass
    except websockets.InvalidStatusCode as e:
        assert e.status_code == 403
    
    async with websockets.connect(uri, extra_headers=header1) as websocket1:
        async with websockets.connect(uri, extra_headers=header2) as websocket2:
            # Invalid meshsage body
            await websocket1.send("{'lol': 'pog'}")
            response_json = await websocket1.recv()
            response = WsResponse.model_validate_json(response_json)
            assert response.code == 1
            assert response.message == "Invalid message body."

            # Invalid user
            message = WsRcvMessage(receiver_username="no-name", encrypted_content="You're an idiot >:)", sent_stamp=int(datetime.now().timestamp()))
            await websocket1.send(message.model_dump_json())
            response_json = await websocket1.recv()
            response = WsResponse.model_validate_json(response_json)
            assert response.code == 2
            assert response.message == "User not found."

            # Simple message
            message = WsRcvMessage(receiver_username="test-2", encrypted_content="You're an idiot >:)", sent_stamp=int(datetime.now().timestamp()))
            await websocket1.send(message.model_dump_json())
            response_json = await websocket1.recv()
            response = WsResponse.model_validate_json(response_json)
            assert response.code == 3
            assert response.message == "Message delivered."

            received = await websocket2.recv()
            received_message = WsResponse.model_validate_json(received)
            assert received_message.code == 4
            assert received_message.message == "You're an idiot >:)"
            assert received_message.sender_name == "test-1"
            assert received_message.sender_public_key == "public"