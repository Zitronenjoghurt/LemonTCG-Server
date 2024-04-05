from fastapi import FastAPI
from src.resources import ping

api = FastAPI(
    title="LemonTCG Multiplayer API",
    description="The API enabling multiplayer features for LemonTCG.",
    version="0.1.0"
)

api.include_router(ping.router)