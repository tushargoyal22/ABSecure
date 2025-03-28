from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):  
        if isinstance(v, ObjectId):
            return str(v) 
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)  

class Tranche(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    tranche_name: str
    risk_category: str 
    return_category: str  
    payment_priority: str
    loans: List[PyObjectId] 
    budget_spent: float 
    average_risk: float
    investor_budget: float
    criteria: str
    suboption: str
    investor_id: Optional[PyObjectId] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "65ff3d7f36e9f8a7a2d3a1b1", 
                "tranche_name": "Tranche A",
                "risk_category": "Low",
                "return_category": "Stable",
                "payment_priority": "First to be paid",  
                "loans": ["65ff3d7f36e9f8a7a2d3a1b2", "65ff3d7f36e9f8a7a2d3a1b3"],
                "budget_spent": 100000.0,
                "average_risk": 40.3,
                "criteria": "Liquidity",
                "suboption": "High Liquidity",
                "investor_budget": 200000.0,
                "investor_id": "65ff3d7f36e9f8a7a2d3a1b1",
            }
        }