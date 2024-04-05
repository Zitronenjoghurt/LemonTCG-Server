from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from src.entities.api_key import ApiKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# A factory method for validating the given api key with a given endpoint name
def api_key_validator(endpoint_name: str):
    async def validate_api_key(x_api_key: str = Security(api_key_header)):
        api_key = await ApiKey.find_one(key=x_api_key)
        if not isinstance(api_key, ApiKey):
            raise HTTPException(status_code=403, detail="Invalid API Key.")
        api_key.use(endpoint=endpoint_name)
        await api_key.save()
        return api_key
    return validate_api_key