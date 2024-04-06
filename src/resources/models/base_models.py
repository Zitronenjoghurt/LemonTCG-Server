from pydantic import BaseModel

class ErrorMessage(BaseModel):
    detail: str

class SuccessMessage(BaseModel):
    message: str