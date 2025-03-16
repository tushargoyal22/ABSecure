# backend/models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
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