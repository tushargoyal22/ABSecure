"""User Authentication Data Models.

This module contains Pydantic models for user data representation,
including validation and serialization of user-related information.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from bson import ObjectId
from pydantic_core.core_schema import CoreSchema, ValidationInfo

class PyObjectId(str):
    """Custom type for handling MongoDB ObjectId in Pydantic models.
    
    Provides proper validation and serialization between ObjectId and string representations.
    """
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler) -> CoreSchema:
        """Generate core schema for Pydantic to properly handle OpenAPI schema generation.
        
        Args:
            source_type: The source type being processed
            handler: The schema handler
            
        Returns:
            CoreSchema: The generated core schema
        """
        return handler.generate_schema(str)

    @classmethod
    def validate(cls, v, info: ValidationInfo) -> str:
        """Validate and convert ObjectId to string representation.
        
        Args:
            v: Input value to validate
            info: Validation context information
            
        Returns:
            str: String representation of valid ObjectId
            
        Raises:
            ValueError: If input is not a valid ObjectId
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class User(BaseModel):
    """User model representing application user accounts.
    
    Attributes:
        id: Unique identifier (as PyObjectId)
        full_name: User's full name
        email: Validated email address
        password: Hashed password string
        is_verified: Email verification status
        verification_token: Token for email verification
        tranches: List of tranche IDs the user has access to
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    full_name: str
    email: EmailStr
    password: str
    is_verified: bool = False
    verification_token: Optional[str] = None
    tranches: List[str] = []

    class Config:
        """Pydantic model configuration with example schema."""
        json_schema_extra = {
            "example": {
                "full_name": "user",
                "email": "user@example.com",
                "password": "securepassword",
                "is_verified": False,
                "verification_token": None
            }
        }