from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.resources import ping
from src.resources import room

api = FastAPI(
    title="LemonTCG Multiplayer API",
    description="The API enabling multiplayer features for LemonTCG.",
    version="0.1.0",
    docs_url="/swagger",
    redoc_url="/docs"
)

api.include_router(ping.router)
api.include_router(room.router)

@api.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")