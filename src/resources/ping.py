from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from src.auth.api_key_authentication import user_validator, User

router = APIRouter()

@router.get("/ping")
async def ping(user: User = Security(user_validator("ping"))) -> JSONResponse:
    return JSONResponse(content={"message": "Pong"}, status_code=200)