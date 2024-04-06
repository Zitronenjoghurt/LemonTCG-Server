from fastapi import APIRouter, Security, status, Query, HTTPException
from src.auth.api_key_authentication import user_validator, User
from src.models.base_models import ErrorMessage
from src.models.friend_models import FriendList, FriendRequests

router = APIRouter(prefix="/friend")

# region get_friend
@router.get(
    "/",
    tags=["Friend"],
    status_code=status.HTTP_200_OK,
    response_model=FriendList,
    responses={
        status.HTTP_200_OK: {"description": "Friend list"},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"}
    },
    summary="List",
    description="Retrieve your list of friends."
)
async def get_friend(user: User = Security(user_validator("get-friend"))) -> FriendList:
    return await user.get_friend_list()
# endregion


# region delete_friend
@router.delete(
    "/",
    tags=["Friend"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Friend successfully removed"},
        status.HTTP_400_BAD_REQUEST: {"description": "Failed to remove friend", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": ErrorMessage}
    },
    summary="Remove",
    description="Remove a friend."
)
async def delete_friend(
    user: User = Security(user_validator("delete-friend")),
    name: str = Query(
        description="The username of the user to remove from your friends, not case-sensitive."
    )
) -> None:
    target = await User.find_one(name=name.lower())
    if not isinstance(target, User):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    success, message = await user.remove_friend(user=target)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
# endregion


# region get_request
@router.get(
    "/request",
    tags=["Friend"],
    status_code=status.HTTP_200_OK,
    response_model=FriendRequests,
    responses={
        status.HTTP_200_OK: {"description": "Friend requests"},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"}
    },
    summary="Requests",
    description="Retrieve your friend requests."
)
async def get_request(user: User = Security(user_validator("get-friend-request"))) -> FriendRequests:
    return await user.get_friend_requests()
# endregion


# region post_request
@router.post(
    "/request",
    tags=["Friend"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Friend request sent"},
        status.HTTP_400_BAD_REQUEST: {"description": "Failed to send request", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": ErrorMessage}
    },
    summary="Send Request",
    description="Send a friend request to the given user."
)
async def post_request(
    user: User = Security(user_validator("post-friend-request")),
    name: str = Query(
        description="The username of the user to add as a friend, not case-sensitive."
    )
) -> None:
    target = await User.find_one(name=name.lower())
    if not isinstance(target, User):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    success, message = target.receive_friend_request(user_key=user.key)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    await target.save()
# endregion


# region delete_request
@router.delete(
    "/request",
    tags=["Friend"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Friend request deleted"},
        status.HTTP_400_BAD_REQUEST: {"description": "Failed to delete request", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": ErrorMessage}
    },
    summary="Retract Request",
    description="Retract a friend request from the given user."
)
async def delete_request(
    user: User = Security(user_validator("delete-friend-request")),
    name: str = Query(
        description="The username of the user you want to retract the friend request from, not case-sensitive."
    )
) -> None:
    target = await User.find_one(name=name.lower())
    if not isinstance(target, User):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    success, message = await user.retract_friend_request(user=target)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
# endregion


# region post_request_accept
@router.post(
    "/request/accept",
    tags=["Friend"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Accepted friend request"},
        status.HTTP_400_BAD_REQUEST: {"description": "Failed to accept friend request", "model": ErrorMessage},
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": ErrorMessage}
    },
    summary="Accept Request",
    description="Accept a friend request of the given user."
)
async def post_request_accept(
    user: User = Security(user_validator("post-friend-request-accept")),
    name: str = Query(
        description="The username of the user to aceept the friend request of, not case-sensitive."
    )
) -> None:
    target = await User.find_one(name=name.lower())
    if not isinstance(target, User):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    success, message = await user.accept_friend_request(user=target)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
# endregion


# region post_request_deny
@router.post(
    "/request/deny",
    tags=["Friend"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Denied friend request"},
        status.HTTP_400_BAD_REQUEST: {"description": "Failed to deny friend request", "model": ErrorMessage},
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": ErrorMessage}
    },
    summary="Deny Request",
    description="Deny a friend request of the given user."
)
async def post_request_deny(
    user: User = Security(user_validator("post-friend-request-deny")),
    name: str = Query(
        description="The username of the user to deny the friend request of, not case-sensitive."
    )
) -> None:
    target = await User.find_one(name=name.lower())
    if not isinstance(target, User):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    success, message = await user.deny_friend_request(user_key=target.key)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
# endregion