from pydantic import BaseModel

class UserPrivateInformation(BaseModel):
    name: str
    display_name: str

class UserPublicInformation(BaseModel):
    name: str
    display_name: str