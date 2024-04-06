from fastapi import APIRouter, Security, HTTPException, Query, status
from src.auth.api_key_authentication import user_validator, User
from src.entities.room import Room
from src.resources.models.base_models import ErrorMessage, SuccessMessage
from src.resources.models.room_models import RoomCreationSuccess, RoomInformation

router = APIRouter(prefix="/room")

# region status
@router.get(
    "/status",
    tags=["Room"],
    status_code=status.HTTP_200_OK,
    response_model=RoomInformation,
    responses={
        status.HTTP_200_OK: {"description": "Room information"},
        status.HTTP_404_NOT_FOUND: {"description": "Room not found", "model": ErrorMessage}
    },
    summary="Status",
    description="Retrieve status information about a room."
)
async def get_status(
    code: str = Query(
        description="The code of the room."
    ),
    user: User = Security(user_validator("room-status"))
) -> RoomInformation:
    code = code.upper()
    room = await Room.find_one(code=code)
    if not isinstance(room, Room) or not room.visible_to(key=user.key):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
    return await room.get_information()
# endregion


# region create
@router.post(
    "/create",
    tags=["Room"],
    status_code=status.HTTP_201_CREATED,
    response_model=RoomCreationSuccess,
    responses={
        status.HTTP_201_CREATED: {"description": "Room successfully created"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to create room due to room size limit", "model": ErrorMessage}
    },
    summary="Create",
    description="Create multiplayer rooms for creating game sessions."
)
async def create(
    visible: bool = Query(
        default=False,
        description="If the server is visible in public server view."
    ), 
    user: User = Security(user_validator("room-create"))
) -> RoomCreationSuccess:
    room = await Room.create(owner_key=user.key, visibe=visible)
    if not isinstance(room, Room):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum room limit reached.")
    await room.save()
    return RoomCreationSuccess(code=room.code)
# endregion


# region join
@router.post(
    "/join",
    tags=["Room"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Successfully joined the room"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to join room", "model": ErrorMessage},
        status.HTTP_404_NOT_FOUND: {"description": "Room not found", "model": ErrorMessage}
    },
    summary="Join",
    description="Join a multiplayer room."
)
async def join(
    code: str = Query(
        description="The code of the room to join."
    ), 
    user: User = Security(user_validator("room-join"))
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


# region leave
@router.post(
    "/leave",
    tags=["Room"],
    status_code=status.HTTP_200_OK,
    response_model=SuccessMessage,
    responses={
        status.HTTP_200_OK: {"description": "Successfully left the room"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to leave room", "model": ErrorMessage},
        status.HTTP_404_NOT_FOUND: {"description": "Room not found", "model": ErrorMessage}
    },
    summary="Leave",
    description="Leave a multiplayer room."
)
async def leave(
    code: str = Query(
        description="The code of the room to leave."
    ), 
    user: User = Security(user_validator("room-leave"))
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


# region ready
@router.post(
    "/ready",
    tags=["Room"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Successfully changed ready state"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to change ready state", "model": ErrorMessage},
        status.HTTP_404_NOT_FOUND: {"description": "Room not found", "model": ErrorMessage}
    },
    summary="Ready",
    description="Change your ready state for a room."
)
async def ready(
    code: str = Query(
        description="The code of the room to leave."
    ),
    state: bool = Query(
        description="The new ready state"  
    ),
    user: User = Security(user_validator("room-ready"))
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

