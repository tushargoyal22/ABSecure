from pydantic import BaseModel, Field
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
        return str(v)  # Convert ObjectId to string for JSON response

class Loan(BaseModel):
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
    
    RiskScore: Optional[int] = None  # ML model will assign this value if not provided during pooling/tranching
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
                "EmploymentStatus": "Employed"  # Required field now included in the example
            }
        }
