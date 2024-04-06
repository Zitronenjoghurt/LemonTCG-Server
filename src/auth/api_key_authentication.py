from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from src.entities.user import User

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# A factory method for validating the given api key with a given endpoint name
def user_validator(endpoint_name: str):
    async def validate_user(x_api_key: str = Security(api_key_header)) -> User:
        user = await User.find_one(key=x_api_key)
        if not isinstance(user, User):
            raise HTTPException(status_code=403, detail="Invalid API Key.")
        user.use_endpoint(endpoint=endpoint_name)
        await user.save()
        return user
    return validate_user