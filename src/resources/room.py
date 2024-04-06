from fastapi import APIRouter, Security, HTTPException, Query, status
from src.auth.api_key_authentication import user_validator, User
from src.entities.room import Room
from src.models.base_models import ErrorMessage, SuccessMessage
from src.models.room_models import RoomCreationSuccess, RoomInformation

router = APIRouter(prefix="/room")

# region get_status
@router.get(
    "/status",
    tags=["Room"],
    status_code=status.HTTP_200_OK,
    response_model=RoomInformation,
    responses={
        status.HTTP_200_OK: {"description": "Room information"},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"},
        status.HTTP_404_NOT_FOUND: {"description": "Room not found", "model": ErrorMessage}
    },
    summary="Status",
    description="Retrieve status information about a room."
)
async def get_status(
    user: User = Security(user_validator("get-room-status")),
    code: str = Query(
        description="The code of the room."
    )
) -> RoomInformation:
    code = code.upper()
    room = await Room.find_one(code=code)
    if not isinstance(room, Room) or not room.visible_to(key=user.key):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
    return await room.get_information()
# endregion


# region post_create
@router.post(
    "/create",
    tags=["Room"],
    status_code=status.HTTP_201_CREATED,
    response_model=RoomCreationSuccess,
    responses={
        status.HTTP_201_CREATED: {"description": "Room successfully created"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to create room", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"}
    },
    summary="Create",
    description="Create multiplayer rooms for creating game sessions."
)
async def post_create(
    user: User = Security(user_validator("post-room-create")),
    visible: bool = Query(
        default=False,
        description="If the server is visible in public server view."
    )
) -> RoomCreationSuccess:
    room = await Room.create(owner_key=user.key, visibe=visible)
    if not isinstance(room, Room):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum room limit reached.")
    await room.save()
    return RoomCreationSuccess(code=room.code)
# endregion


# region post_join
@router.post(
    "/join",
    tags=["Room"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Successfully joined the room"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to join room", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"},
        status.HTTP_404_NOT_FOUND: {"description": "Room not found", "model": ErrorMessage}
    },
    summary="Join",
    description="Join a multiplayer room."
)
async def post_join(
    user: User = Security(user_validator("post-room-join")),
    code: str = Query(
        description="The code of the room to join."
    )
) -> None:
    code = code.upper()
    room = await Room.find_one(code=code)
    if not isinstance(room, Room):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
    
    success, message = room.join(key=user.key)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    await room.save()
# endregion


# region post_leave
@router.post(
    "/leave",
    tags=["Room"],
    status_code=status.HTTP_200_OK,
    response_model=SuccessMessage,
    responses={
        status.HTTP_200_OK: {"description": "Successfully left the room"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to leave room", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"},
        status.HTTP_404_NOT_FOUND: {"description": "Room not found", "model": ErrorMessage}
    },
    summary="Leave",
    description="Leave a multiplayer room."
)
async def post_leave(
    user: User = Security(user_validator("post-room-leave")),
    code: str = Query(
        description="The code of the room to leave."
    )
) -> SuccessMessage:
    code = code.upper()
    room = await Room.find_one(code=code)
    if not isinstance(room, Room):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
    
    success, message = await room.leave(key=user.key)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    return SuccessMessage(message=message)
# endregion


# region post_ready
@router.post(
    "/ready",
    tags=["Room"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Successfully changed ready state"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to change ready state", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"},
        status.HTTP_404_NOT_FOUND: {"description": "Room not found", "model": ErrorMessage}
    },
    summary="Ready",
    description="Change your ready state for a room."
)
async def post_ready(
    user: User = Security(user_validator("post-room-ready")),
    code: str = Query(
        description="The code of the room to leave."
    ),
    state: bool = Query(
        description="The new ready state"  
    )
) -> None:
    code = code.upper()
    room = await Room.find_one(code=code)
    if not isinstance(room, Room):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
    
    success, message = room.ready(key=user.key, state=state)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    await room.save()
# endregion

