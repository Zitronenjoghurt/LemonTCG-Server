from typing import Optional
from src.database.collection import Collection
from src.entities.database_entity import DatabaseEntity

class Message(DatabaseEntity):
    COLLECTION = Collection.MESSAGES
    content: str
    sender_key: str
    receiver_key: str
    sent_stamp: int
    read: bool = False
    read_stamp: Optional[int] = None