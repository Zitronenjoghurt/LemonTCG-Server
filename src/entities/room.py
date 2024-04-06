import secrets
from typing import Optional
from src.database.collection import Collection
from src.entities.database_entity import DatabaseEntity

CODE_CHARACTERS = "ABCDEFGHKMNPQRSTUVWXYZ23456789"
MAX_ROOM_COUNT = 5

class Room(DatabaseEntity):
    COLLECTION = Collection.ROOMS
    user_key: str
    code: str
    visible: bool = False

    @staticmethod
    async def create(user_key: str, visibe: bool = False) -> Optional['Room']:
        rooms = await Room.find_all(user_key=user_key)
        if len(rooms) >= MAX_ROOM_COUNT:
            return
        code = await generate_code()
        return Room(user_key=user_key, code=code, visible=visibe)

async def generate_code() -> str:
    while True:
        code = ''.join(secrets.choice(CODE_CHARACTERS) for _ in range(6))
        room = await Room.find_one(code=code)
        if not isinstance(room, Room):
            return code