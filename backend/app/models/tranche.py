"""Tranche Data Model for Loan Securitization.

This module contains the Pydantic model for tranche data representation,
including validation and serialization of tranche-related information.
"""

from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List

class PyObjectId(str):
    """Custom type for handling MongoDB ObjectId in Pydantic models.
    
    Provides validation and serialization between ObjectId and string representations.
    """
    @classmethod
    def __get_validators__(cls):
        """Generator yielding validator methods for Pydantic processing."""
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        """Validate and convert ObjectId to string representation.
        
        Args:
            v: Input value to validate (either ObjectId or string)
            field: Pydantic field being validated (unused)
            
        Returns:
            str: String representation of valid ObjectId
            
        Raises:
            ValueError: If input is not a valid ObjectId
        """
        if isinstance(v, ObjectId):
            return str(v) 
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)  

class Tranche(BaseModel):
    """Tranche model representing a risk segment in loan securitization.
    
    Attributes:
        id: Unique identifier (as PyObjectId)
        tranche_name: Name of the tranche
        risk_category: Risk classification (Low/Medium/High)
        return_category: Expected return profile
        payment_priority: Payment waterfall priority
        loans: List of loan IDs in this tranche
        budget_spent: Amount allocated to loans
        average_risk: Calculated risk score average
        investor_budget: Total available budget
        criteria: Allocation criteria used
        suboption: Specific sub-criteria applied
        investor_id: Optional investor reference
    """
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
        """Pydantic model configuration with example schema."""
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