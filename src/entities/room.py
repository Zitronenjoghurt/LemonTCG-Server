import secrets
from datetime import datetime
from typing import Optional
from src.database.collection import Collection
from src.entities.database_entity import DatabaseEntity
from src.entities.user import User
from src.resources.models.room_models import RoomInformation

CODE_CHARACTERS = "ABCDEFGHKMNPQRSTUVWXYZ23456789"
MAX_ROOM_COUNT = 5

class Room(DatabaseEntity):
    COLLECTION = Collection.ROOMS
    code: str
    owner_key: str
    owner_ready: bool = False
    opponent_key: Optional[str] = None
    opponent_ready: bool = False
    visible: bool = False
    created_stamp: datetime = datetime.now()

    @staticmethod
    async def create(owner_key: str, visibe: bool = False) -> Optional['Room']:
        rooms = await Room.find_all(owner_key=owner_key)
        if len(rooms) >= MAX_ROOM_COUNT:
            return
        code = await generate_code()
        return Room(owner_key=owner_key, code=code, visible=visibe)
    
    async def get_information(self) -> RoomInformation:
        owner = await User.find_one(key=self.owner_key)
        opponent = await User.find_one(key=self.opponent_key) if self.opponent_key else None
        return RoomInformation(
            code=self.code,
            owner_name=owner.name if isinstance(owner, User) else "No Name",
            opponent_name=opponent.name if isinstance(opponent, User) else None,
            owner_ready=self.owner_ready,
            opponent_ready=self.opponent_ready,
            created_stamp=int(self.created_stamp.timestamp()),
            is_ready=self.is_ready()
        )
    
    def join(self, key: str) -> tuple[bool, str]:
        if isinstance(self.opponent_key, str):
            return False, "Room is full."
        self.opponent_key = key
        return True, ""
    
    async def leave(self, key: str) -> tuple[bool, str]:
        match key:
            case self.owner_key:
                await self.delete()
                return True, "Room closed."
            case self.opponent_key:
                self.opponent_key = None
                self.opponent_ready = False
                await self.save()
                return True, "Left room."
            case _:
                return False, "Not a participant of the room."
            
    def ready(self, key: str, state: bool) -> tuple[bool, str]:
        match key:
            case self.owner_key:
                self.owner_ready = state
                return True, ""
            case self.opponent_key:
                self.opponent_ready = state
                return True, ""
            case _:
                return False, "Not a participant of the room."
            
    def visible_to(self, key: str) -> bool:
        if self.visible:
            return True
        return key == self.owner_key or key == self.opponent_key
    
    def is_ready(self) -> bool:
        return isinstance(self.opponent_key, str) and self.owner_ready and self.opponent_ready

async def generate_code() -> str:
    while True:
        code = ''.join(secrets.choice(CODE_CHARACTERS) for _ in range(6))
        room = await Room.find_one(code=code)
        if not isinstance(room, Room):
            return code