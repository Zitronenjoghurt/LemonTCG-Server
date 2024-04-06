from pydantic import BaseModel
from typing import Optional

class RoomCreationSuccess(BaseModel):
    code: str

class RoomInformation(BaseModel):
    code: str
    owner_name: str
    opponent_name: Optional[str]
    owner_ready: bool
    opponent_ready: bool
    created_stamp: int
    is_ready: bool