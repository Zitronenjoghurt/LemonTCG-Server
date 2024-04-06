from fastapi import APIRouter, Security, status
from src.auth.api_key_authentication import user_validator, User
from src.models.base_models import SuccessMessage

router = APIRouter()

# region get_ping
@router.get(
    "/ping",
    tags=["Miscellaneous"],
    status_code=status.HTTP_200_OK,
    response_model=SuccessMessage,
    responses={
        status.HTTP_200_OK: {"description": "Pong!"},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"}
    },
    summary="Ping",
    description="Check if the server is online and your api key valid."
)
async def get_ping(user: User = Security(user_validator("get-ping"))) -> SuccessMessage:
    return SuccessMessage(message="Pong")
# endregion