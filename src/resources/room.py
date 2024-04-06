from fastapi import APIRouter, Security, HTTPException, Query
from src.auth.api_key_authentication import api_key_validator, ApiKey
from src.entities.room import Room
from src.resources.models.room_models import RoomCreationSuccess

router = APIRouter(prefix="/room")

@router.post(
    "/create",
    tags=["rooms"],
    status_code=201,
    response_model=RoomCreationSuccess,
    responses={
        201: {"description": "Room successfully created."},
        400: {"description": "Unable to create room due to room size limit."}
    },
    summary="Create",
    description="Create multiplayer rooms for creating game sessions."
)
async def create(
    visible: bool = Query(
        default=False,
        description="If the server is visible in public server view."
    ), 
    api_key: ApiKey = Security(api_key_validator("room-create"))
) -> RoomCreationSuccess:
    room = await Room.create(user_key=api_key.key, visibe=visible)
    if not isinstance(room, Room):
        raise HTTPException(status_code=400, detail="Maximum room limit reached.")
    await room.save()
    return RoomCreationSuccess(code=room.code)