import uuid
from datetime import datetime
from src.database.collection import Collection
from src.entities.database_entity import DatabaseEntity

class ApiKey(DatabaseEntity):
    COLLECTION = Collection.API_KEYS
    UNIQUE_FIELDS = ["key"]
    key: str
    user: str
    used_endpoints: dict[str, int] = {}
    last_used_stamp: datetime = datetime.now()
    created_stamp: datetime = datetime.now()

    @staticmethod
    def new(username: str) -> 'ApiKey':
        key = str(uuid.uuid4()).replace('-', '')
        return ApiKey(key=key, user=username)
    
    def use(self, endpoint: str) -> None:
        if endpoint not in self.used_endpoints:
            self.used_endpoints[endpoint] = 1
        else:
            self.used_endpoints[endpoint] += 1
        self.last_used_stamp = datetime.now()