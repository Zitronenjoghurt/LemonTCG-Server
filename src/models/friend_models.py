from pydantic import BaseModel
from typing import Optional
from src.models.user_models import UserPublicInformation

class FriendInformation(BaseModel):
    user: Optional[UserPublicInformation] = None
    friends_since_stamp: int

class FriendList(BaseModel):
    friends: list[FriendInformation]

class FriendRequest(BaseModel):
    user: Optional[UserPublicInformation] = None
    received_stamp: int

class FriendRequests(BaseModel):
    requests: list[FriendRequest]