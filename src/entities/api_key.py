import uuid
from src.database.collection import Collection
from src.entities.database_entity import DatabaseEntity

class ApiKey(DatabaseEntity):
    COLLECTION = Collection.API_KEYS
    UNIQUE_FIELDS = ["key"]
    key: str
    user: str

    @staticmethod
    def new(username: str) -> 'ApiKey':
        key = str(uuid.uuid4()).replace('-', '')
        return ApiKey(key=key, user=username)