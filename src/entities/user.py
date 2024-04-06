import uuid
from datetime import datetime
from src.database.collection import Collection
from src.entities.database_entity import DatabaseEntity
from src.models.user_models import UserPrivateInformation, UserPublicInformation

class User(DatabaseEntity):
    COLLECTION = Collection.USERS
    UNIQUE_FIELDS = ["key", "name"]
    key: str
    name: str
    display_name: str
    used_endpoints: dict[str, int] = {}
    last_access_stamp: datetime = datetime.now()
    created_stamp: datetime = datetime.now()

    @staticmethod
    def new(name: str) -> 'User':
        key = str(uuid.uuid4()).replace('-', '')
        return User(key=key, name=name.lower(), display_name=name)
    
    def use_endpoint(self, endpoint: str) -> None:
        if endpoint not in self.used_endpoints:
            self.used_endpoints[endpoint] = 1
        else:
            self.used_endpoints[endpoint] += 1
        self.last_access_stamp = datetime.now()

    def get_private_information(self) -> UserPrivateInformation:
        return UserPrivateInformation(
            name=self.name,
            display_name=self.display_name
        )
    
    def get_public_information(self) -> UserPublicInformation:
        return UserPublicInformation(
            name=self.name,
            display_name=self.display_name
        )