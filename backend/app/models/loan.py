from pydantic import BaseModel, GetJsonSchemaHandler, Field
from pydantic.json_schema import JsonSchemaValue
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

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: JsonSchemaValue, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}  # Ensure OpenAPI schema treats ObjectId as a string

class Loan(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    ApplicationDate: str
    Age: int
    AnnualIncome: int
    CreditScore: int
    EmploymentStatus: str
    EducationLevel: str
    Experience: int
    LoanAmount: int
    LoanDuration: int
    MaritalStatus: str
    NumberOfDependents: int
    HomeOwnershipStatus: str
    MonthlyDebtPayments: int
    CreditCardUtilizationRate: float
    NumberOfOpenCreditLines: int
    NumberOfCreditInquiries: int
    DebtToIncomeRatio: float
    BankruptcyHistory: int
    LoanPurpose: str
    PreviousLoanDefaults: int
    PaymentHistory: int
    LengthOfCreditHistory: int
    SavingsAccountBalance: int
    CheckingAccountBalance: int
    TotalAssets: int
    TotalLiabilities: int
    MonthlyIncome: float
    UtilityBillsPaymentHistory: float
    JobTenure: int
    NetWorth: int  # Added missing fields
    BaseInterestRate: float
    InterestRate: float
    MonthlyLoanPayment: float
    TotalDebtToIncomeRatio: float
    LoanApproved: int
    RiskScore: int

    class Config:
        json_schema_extra = {
            "example": {
                "ApplicationDate": "2025-02-17",
                "Age": 30,
                "AnnualIncome": 50000,
                "CreditScore": 700,
                "EmploymentStatus": "Employed",
                "EducationLevel": "Bachelor",
                "Experience": 5,
                "LoanAmount": 10000,
                "LoanDuration": 24,
                "MaritalStatus": "Single",
                "NumberOfDependents": 0,
                "HomeOwnershipStatus": "Rent",
                "MonthlyDebtPayments": 500,
                "CreditCardUtilizationRate": 0.3,
                "NumberOfOpenCreditLines": 2,
                "NumberOfCreditInquiries": 1,
                "DebtToIncomeRatio": 0.4,
                "BankruptcyHistory": 0,
                "LoanPurpose": "Personal",
                "PreviousLoanDefaults": 0,
                "PaymentHistory": 12,
                "LengthOfCreditHistory": 6,
                "SavingsAccountBalance": 5000,
                "CheckingAccountBalance": 1000,
                "TotalAssets": 50000,
                "TotalLiabilities": 10000,
                "MonthlyIncome": 4000,
                "UtilityBillsPaymentHistory": 0.9,
                "JobTenure": 3,
                "NetWorth": 40000,
                "BaseInterestRate": 3.5,
                "InterestRate": 5.0,
                "MonthlyLoanPayment": 450,
                "TotalDebtToIncomeRatio": 0.35,
                "LoanApproved": 1,
                "RiskScore": 750
            }
        }
