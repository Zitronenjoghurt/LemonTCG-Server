from pydantic import BaseModel

class RoomCreationSuccess(BaseModel):
    code: str

class RoomInformation(BaseModel):
    code: str
    owner_name: str
    opponent_name: str
    owner_ready: bool
    opponent_ready: bool
    created_stamp: int