import uuid
from datetime import date, datetime
from src.database.collection import Collection
from src.entities.database_entity import DatabaseEntity
from src.models.friend_models import FriendInformation, FriendList, FriendRequest, FriendRequests
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
    friends: dict[str, datetime] = {}
    friend_requests: dict[str, datetime] = {}

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
    
    # region friends
    def receive_friend_request(self, user_key: str) -> tuple[bool, str]:
        if user_key == self.key:
            return False, "Can't add yourself as a friend."
        if user_key in self.friend_requests:
            return False, "Already sent a request."
        if user_key in self.friend_requests:
            return False, "Already on friendlist."
        self.friend_requests[user_key] = datetime.now()
        return True, ""
    
    async def retract_friend_request(self, user: 'User') -> tuple[bool, str]:
        if self.key not in user.friend_requests:
            return False, "No pending friend request with user."
        del user.friend_requests[self.key]
        await user.save()
        return True, ""
    
    async def accept_friend_request(self, user: 'User') -> tuple[bool, str]:
        if user.key not in self.friend_requests:
            return False, "No pending friend request with user."
        del self.friend_requests[user.key]

        if self.key in user.friend_requests:
            del user.friend_requests[self.key]

        now_date = datetime.now()
        self.friends[user.key] = now_date
        user.friends[self.key] = now_date

        await self.save()
        await user.save()
        return True, ""
    
    async def deny_friend_request(self, user_key: str) -> tuple[bool, str]:
        if user_key not in self.friend_requests:
            return False, "No pending friend request with user."
        del self.friend_requests[user_key]

        await self.save()
        return True, ""
    
    async def remove_friend(self, user: 'User') -> tuple[bool, str]:
        if user.key not in self.friends:
            return False, "Not friends with user."
        del self.friends[user.key]
        del user.friends[self.key]
        await self.save()
        await user.save()
        return True, ""
    
    async def get_friend_list(self) -> FriendList:
        friend_information = []
        for user_key, date in self.friends.items():
            user = await User.find_one(key=user_key)

            if isinstance(user, User):
                information = user.get_public_information()
            else:
                information = None

            friend_information.append(FriendInformation(user=information, friends_since_stamp=int(date.timestamp())))

        return FriendList(
            friends=friend_information
        )
    
    async def get_friend_requests(self) -> FriendRequests:
        requests = []
        for user_key, date in self.friend_requests.items():
            user = await User.find_one(key=user_key)

            if isinstance(user, User):
                information = user.get_public_information()
            else:
                information = None

            requests.append(FriendRequest(user=information, received_stamp=int(date.timestamp())))

        return FriendRequests(
            requests=requests
        )
    # endregion

    