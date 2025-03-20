from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId
from pydantic_core.core_schema import CoreSchema, ValidationInfo

class PyObjectId(str):
    """Custom type to handle MongoDB ObjectId fields properly."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler) -> CoreSchema:
        """Fixes OpenAPI schema resolution issues."""
        return handler.generate_schema(str)

    @classmethod
    def validate(cls, v, info: ValidationInfo) -> str:
        """Validates if the given value is a valid ObjectId."""
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class User(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    password: str
    is_verified: bool = False
    verification_token: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword",
                "is_verified": False,
                "verification_token": None
            }
        }
