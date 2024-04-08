from typing import Optional
from pydantic import BaseModel

class WsRcvMessage(BaseModel):
    receiver_username: str
    encrypted_content: str
    sent_stamp: int

# 1: Invalid Message body
# 2: Invalid User
# 3: Success
# 4: Incoming Message
class WsResponse(BaseModel):
    code: int
    message: str
    sender_name: Optional[str] = None
    sender_public_key: Optional[str] = None

WS_INVALID_MESSAGE_BODY = WsResponse(code=1, message="Invalid message body.").model_dump_json()
WS_USER_NOT_FOUND = WsResponse(code=2, message="User not found.").model_dump_json()
WS_MESSAGE_DELIVERED = WsResponse(code=3, message="Message delivered.").model_dump_json()