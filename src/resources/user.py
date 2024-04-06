from fastapi import APIRouter, Security, status, Query, HTTPException
from src.auth.api_key_authentication import user_validator, User
from src.models.base_models import ErrorMessage
from src.models.user_models import UserPrivateInformation, UserPublicInformation

router = APIRouter(prefix="/user")

# region get_user
@router.get(
    "/",
    tags=["User"],
    status_code=status.HTTP_200_OK,
    response_model=UserPrivateInformation,
    responses={
        status.HTTP_200_OK: {"description": "User information"},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"}
    },
    summary="User Information",
    description="Retrieve your own user information."
)
async def get_user(user: User = Security(user_validator("get-user"))) -> UserPrivateInformation:
    return user.get_private_information()
# endregion


# region get_search
@router.get(
    "/search",
    tags=["User"],
    status_code=status.HTTP_200_OK,
    response_model=UserPrivateInformation,
    responses={
        status.HTTP_200_OK: {"description": "User information"},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": ErrorMessage}
    },
    summary="User Search",
    description="Retrieve information about a user."
)
async def get_search(
    user: User = Security(user_validator("get-user")),
    name: str = Query(
        description="The username of the user to search, not case-sensitive."
    )
) -> UserPublicInformation:
    search_user = await User.find_one(name=name.lower())
    if not isinstance(search_user, User):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user.get_public_information()
# endregion