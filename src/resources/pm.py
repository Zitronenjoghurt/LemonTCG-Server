from datetime import date, datetime
from fastapi import APIRouter, WebSocketDisconnect, WebSocket, HTTPException
from src.auth.api_key_authentication import user_validator
from src.entities.message import Message
from src.entities.user import User
from src.models.pm_models import WsRcvMessage, WsResponse, WS_INVALID_MESSAGE_BODY, WS_USER_NOT_FOUND, WS_MESSAGE_DELIVERED

router = APIRouter(prefix="/pm")

# region websocket
ACTIVE_CONNECTIONS: dict[str, WebSocket] = {}

@router.websocket("/ws")
async def pm_websocket(websocket: WebSocket):
    # Check for api key header
    api_key = websocket.headers.get("X-API-Key")
    if api_key is None:
        await websocket.close(code=1008)
        return
    
    # Validate api key
    try:
        validate = user_validator("pm-websocket")
        sender = await validate(api_key)
    except HTTPException:
        await websocket.close(code=1008)
        return
    
    # Accept connection
    await websocket.accept()
    ACTIVE_CONNECTIONS[sender.name] = websocket
    try:
        await pm_connection(sender=sender, websocket=websocket)
    except WebSocketDisconnect:
        ACTIVE_CONNECTIONS.pop(sender.name, None)

async def pm_connection(sender: User, websocket: WebSocket) -> None:
    while True:
        json_data = await websocket.receive_text()
        try:
            response = WsRcvMessage.model_validate_json(json_data=json_data)
        except Exception:
            await websocket.send_text(WS_INVALID_MESSAGE_BODY)
            continue
        username = response.receiver_username.lower()
        receiver = await User.find_one(name=username)
        if not isinstance(receiver, User):
            await websocket.send_text(WS_USER_NOT_FOUND)
            continue

        await websocket.send_text(WS_MESSAGE_DELIVERED)

        # Store message
        message = Message(content=response.encrypted_content, sender_key=sender.key, receiver_key=receiver.key, sent_stamp=response.sent_stamp)

        # Send message to user
        if receiver.name in ACTIVE_CONNECTIONS:
            receiver_message = WsResponse(code=4, message=response.encrypted_content, sender_name=sender.name, sender_public_key=sender.e2ee.public)
            await ACTIVE_CONNECTIONS[receiver.name].send_text(receiver_message.model_dump_json())
            now = datetime.now().timestamp()
            message.read = True
            message.read_stamp = int(now)

        await message.save()
# endregion