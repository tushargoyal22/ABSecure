from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)  # Convert ObjectId to string for JSON response

class LoanPool(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str  # Pool name (e.g., "Low Risk", "High Risk")
    total_amount: float
    avg_risk_score: float
    loans: List[PyObjectId]  # List of Loan IDs

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Low Risk",
                "total_amount": 500000,
                "avg_risk_score": 750,
                "loans": ["65a83f2e9b5a3d1b8c3f41e1", "65a83f2e9b5a3d1b8c3f41e2"]
            }
        }
