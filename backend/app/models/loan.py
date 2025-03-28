"""Loan Data Models for Loan Management System.

This module contains Pydantic models for loan data validation and serialization,
including database storage format (Loan) and API input validation (LoanInput).
"""

from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class PyObjectId(str):
    """Custom type for MongoDB ObjectId handling.
    
    Provides validation and conversion between ObjectId and string representations.
    """
    @classmethod
    def __get_validators__(cls):
        """Yield validator methods for Pydantic model processing."""
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validate and convert ObjectId to string.
        
        Args:
            v: Input value to validate
            
        Returns:
            str: String representation of valid ObjectId
            
        Raises:
            ValueError: If input is not a valid ObjectId
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)  # Convert ObjectId to string for JSON response

class Loan(BaseModel):
    """Primary loan data model for database storage and full loan representation.
    
    Contains all loan attributes including required fields and optional analytics fields.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    ApplicationDate: str
    Age: int
    AnnualIncome: int
    CreditScore: int
    LoanAmount: int
    LoanDuration: int
    SavingsAccountBalance: int
    CheckingAccountBalance: int
    MonthlyIncome: int
    MonthlyLoanPayment: int
    DebtToIncomeRatio: int
    TotalDebtToIncomeRatio: int
    NumberOfOpenCreditLines: int
    NumberOfCreditInquiries: int
    LengthOfCreditHistory: int
    NumberOfDependents: int
    PreviousLoanDefaults: int
    BankruptcyHistory: int
    EmploymentStatus: str  

    # Optional fields for ML & analytics
    RiskScore: Optional[int] = None  # ML model will assign this if not provided
    EducationLevel: Optional[str] = None
    Experience: Optional[int] = None
    MaritalStatus: Optional[str] = None
    HomeOwnershipStatus: Optional[str] = None
    MonthlyDebtPayments: Optional[int] = None
    CreditCardUtilizationRate: Optional[float] = None
    LoanPurpose: Optional[str] = None
    PaymentHistory: Optional[int] = None
    TotalAssets: Optional[int] = None
    TotalLiabilities: Optional[int] = None
    UtilityBillsPaymentHistory: Optional[float] = None
    JobTenure: Optional[int] = None
    NetWorth: Optional[int] = None  
    BaseInterestRate: Optional[float] = None
    InterestRate: Optional[float] = None
    LoanApproved: Optional[int] = None

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "_id": "65ff3d7f36e9f8a7a2d3a1b1",  # Example ObjectId
                "ApplicationDate": "2025-02-17",
                "Age": 30,
                "AnnualIncome": 50000,
                "CreditScore": 700,
                "LoanAmount": 10000,
                "LoanDuration": 12,
                "SavingsAccountBalance": 2000,
                "CheckingAccountBalance": 1000,
                "MonthlyIncome": 4000,
                "MonthlyLoanPayment": 500,
                "DebtToIncomeRatio": 30,
                "TotalDebtToIncomeRatio": 35,
                "NumberOfOpenCreditLines": 3,
                "NumberOfCreditInquiries": 2,
                "LengthOfCreditHistory": 5,
                "NumberOfDependents": 1,
                "PreviousLoanDefaults": 0,
                "BankruptcyHistory": 0,
                "EmploymentStatus": "Employed",
                "RiskScore": 85,
                "LoanApproved": 1
            }
        }

class LoanInput(BaseModel):
    """Loan input model for API request validation.
    
    Contains only required fields for loan application submission.
    """
    ApplicationDate: str
    Age: int
    AnnualIncome: int
    CreditScore: int
    LoanAmount: int
    LoanDuration: int
    SavingsAccountBalance: int
    CheckingAccountBalance: int
    MonthlyIncome: int
    MonthlyLoanPayment: int
    DebtToIncomeRatio: int
    TotalDebtToIncomeRatio: int
    NumberOfOpenCreditLines: int
    NumberOfCreditInquiries: int
    LengthOfCreditHistory: int
    NumberOfDependents: int
    PreviousLoanDefaults: int
    BankruptcyHistory: int
    EmploymentStatus: str  

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "ApplicationDate": "2025-02-17",
                "Age": 30,
                "AnnualIncome": 50000,
                "CreditScore": 700,
                "LoanAmount": 10000,
                "LoanDuration": 12,
                "SavingsAccountBalance": 2000,
                "CheckingAccountBalance": 1000,
                "MonthlyIncome": 4000,
                "MonthlyLoanPayment": 500,
                "DebtToIncomeRatio": 30,
                "TotalDebtToIncomeRatio": 35,
                "NumberOfOpenCreditLines": 3,
                "NumberOfCreditInquiries": 2,
                "LengthOfCreditHistory": 5,
                "NumberOfDependents": 1,
                "PreviousLoanDefaults": 0,
                "BankruptcyHistory": 0,
                "EmploymentStatus": "Employed"
            }
        }