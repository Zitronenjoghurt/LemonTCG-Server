from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from src.auth.api_key_authentication import api_key_validator, ApiKey

router = APIRouter()

@router.get("/ping")
async def ping(api_key: ApiKey = Security(api_key_validator("ping"))) -> JSONResponse:
    return JSONResponse(content={"message": "Pong"}, status_code=200)