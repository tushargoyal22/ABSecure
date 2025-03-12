import pandas as pd
import numpy as np  # Used for handling division by zero (np.nan)
import logging
from functools import lru_cache
from app.ml.risk_model import load_ml_risk_scores, get_updated_dataset
from app.config.database import get_database

logger = logging.getLogger(__name__)

# ---------------------------------------------------
# Cached Thresholds Retrieval
# ---------------------------------------------------
@lru_cache(maxsize=1)
def get_thresholds():
    """
    Retrieves and caches the thresholds document from MongoDB.
    Returns an empty dict if not found.
    """
    db = get_database()
    threshold_collection = db["thresholds"]
    doc = threshold_collection.find_one({"_id": "threshold_values"}, {"_id": 0})
    return doc if doc else {}

def preprocess_loan_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the DataFrame to ensure that all columns used in creditworthiness,
    liquidity, and risk assessment functions have appropriate types and default values.
    """
    df = df.copy()
    
    # Define default values for numeric columns.
    numeric_defaults = {
        "CreditScore": 0,
        "LengthOfCreditHistory": 0,
        "NumberOfOpenCreditLines": 0,
        "NumberOfCreditInquiries": 0,
        "PreviousLoanDefaults": 0,
        "BankruptcyHistory": 0,
        "Predicted_RiskScore": 0,
        "RiskScore": 0,
        "LoanAmount": 0,
        "LoanDuration": 1,  # Use 1 instead of 0 to avoid division by zero issues.
        "SavingsAccountBalance": 0,
        "CheckingAccountBalance": 0,
        "MonthlyIncome": 0,
        "MonthlyLoanPayment": 0,
        "DebtToIncomeRatio": 0,
        "TotalDebtToIncomeRatio": 0,
        "Age": 0,
        "AnnualIncome": 0,
        "NumberOfDependents": 0
    }
    
    # Convert numeric columns to numbers and fill NaNs with defaults.
    for col, default in numeric_defaults.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
    
    # Define defaults for categorical columns.
    categorical_defaults = {
        "EmploymentStatus": "Unknown"
    }
    
    # Fill missing categorical values.
    for col, default in categorical_defaults.items():
        if col in df.columns:
            df[col] = df[col].fillna(default)
    
    return df



# ---------------------------------------------------
# Tranche Classification
# ---------------------------------------------------
def classify_tranche(loan: dict) -> str:
    """
    Assigns a tranche to a loan based on its ML predicted RiskScore using dynamic thresholds.
    It checks for 'Predicted_RiskScore' first, and falls back to 'RiskScore' if not available.
    """
    thresholds = get_thresholds().get("tranche_thresholds", {"Senior": 40, "Mezzanine": 45, "Subordinated": 50})
    risk = loan.get("Predicted_RiskScore", loan.get("RiskScore", 0))
    if risk is None:
        risk = 0
    try:
        risk = float(risk)
    except (TypeError, ValueError):
        risk = 0

    if risk < thresholds["Senior"]:
        return "Senior Tranche"
    elif risk < thresholds["Mezzanine"]:
        return "Mezzanine Tranche"
    elif risk < thresholds["Subordinated"]:
        return "Subordinated Tranche"
    else:
        return "Equity Tranche"

# ---------------------------------------------------
# Creditworthiness Functions
# ---------------------------------------------------
def has_no_defaults_or_bankruptcy(row):
    return (row["PreviousLoanDefaults"] == 0) and (row["BankruptcyHistory"] == 0)

def is_excellent_credit(row):
    cw_thresholds = get_thresholds().get("creditworthiness_thresholds", {}).get("Excellent",
        {"min_credit_score": 800, "min_length": 10, "min_open_credit_lines": 3, "max_open_credit_lines": 7, "max_credit_inquiries": 2})
    return ((row["CreditScore"] >= cw_thresholds["min_credit_score"]) or 
            (row["LengthOfCreditHistory"] > cw_thresholds["min_length"]) or 
            ((cw_thresholds["min_open_credit_lines"] <= row["NumberOfOpenCreditLines"] <= cw_thresholds["max_open_credit_lines"]) and 
             (row["NumberOfCreditInquiries"] <= cw_thresholds["max_credit_inquiries"])))

def is_good_credit(row):
    cw_thresholds = get_thresholds().get("creditworthiness_thresholds", {}).get("Good",
        {"min_credit_score": 700, "max_credit_score": 800, "min_length": 7, "min_open_credit_lines": 3, "max_open_credit_lines": 12, "max_credit_inquiries": 4})
    return ((cw_thresholds["min_credit_score"] <= row["CreditScore"] < cw_thresholds["max_credit_score"]) or
            (row["LengthOfCreditHistory"] >= cw_thresholds["min_length"]) or
            ((cw_thresholds["min_open_credit_lines"] <= row["NumberOfOpenCreditLines"] <= cw_thresholds["max_open_credit_lines"]) and 
             (row["NumberOfCreditInquiries"] <= cw_thresholds["max_credit_inquiries"])))

def is_fair_credit(row):
    cw_thresholds = get_thresholds().get("creditworthiness_thresholds", {}).get("Fair",
        {"min_credit_score": 600, "max_credit_score": 700, "min_length": 3, "max_credit_inquiries": 5})
    return ((cw_thresholds["min_credit_score"] <= row["CreditScore"] < cw_thresholds["max_credit_score"]) or
            (row["LengthOfCreditHistory"] >= cw_thresholds["min_length"]) or
            (row["NumberOfOpenCreditLines"] > 12) or
            (row["NumberOfCreditInquiries"] > cw_thresholds["max_credit_inquiries"]))

# ---------------------------------------------------
# Liquidity and Financial Status Functions
# ---------------------------------------------------
def filter_liquidity(df, suboption):
    df = df.copy()
    # Replace zeros to avoid division by zero issues
    df['LoanAmount'] = df['LoanAmount'].replace(0, np.nan)
    df['LoanDuration'] = df['LoanDuration'].replace(0, np.nan)
    
    # Calculate ratios
    df['Liquidity_Ratio'] = (df['SavingsAccountBalance'] + df['CheckingAccountBalance']) / df['LoanAmount']
    df['Relative_Ratio'] = df['MonthlyIncome'] / (df['LoanAmount'] / df['LoanDuration'])
    
    # Handle NaN values in the ratio calculations.
    # For low liquidity filtering, fill NaNs with high values so they don't qualify.
    df['Liquidity_Ratio'] = df['Liquidity_Ratio'].fillna(np.inf)
    df['Relative_Ratio'] = df['Relative_Ratio'].fillna(np.inf)
    
    thresholds = get_thresholds().get("liquidity_thresholds", {})
    
    if suboption == "High Liquidity":
        th = thresholds.get("High Liquidity", {"min_liquidity_ratio": 1, "min_relative_ratio": 3})
        return df[(df["Liquidity_Ratio"] > th["min_liquidity_ratio"]) | (df["Relative_Ratio"] >= th["min_relative_ratio"])]
    
    elif suboption == "Medium Liquidity":
        th = thresholds.get("Medium Liquidity", {"min_liquidity_ratio": 0.5, "max_liquidity_ratio": 1, "min_relative_ratio": 2, "max_relative_ratio": 3})
        return df[((df["Liquidity_Ratio"] > th["min_liquidity_ratio"]) | (df["Relative_Ratio"] >= th["min_relative_ratio"])) & 
                  (df["Relative_Ratio"] < th["max_relative_ratio"])]
    
    elif suboption == "Low Liquidity":
        th = thresholds.get("Low Liquidity", {"max_liquidity_ratio": 0.5, "max_relative_ratio": 1})
        # Use AND to ensure both ratios are low for low liquidity loans.
        return df[(df["Liquidity_Ratio"] <= th["max_liquidity_ratio"]) & (df["Relative_Ratio"] <= th["max_relative_ratio"])]
    
    else:
        # Optionally handle invalid suboptions
        raise ValueError("Invalid liquidity suboption provided.")


def filter_financial_status(df, suboption):
    df = df.copy()
    # Ensure the relevant columns are numeric to avoid errors.
    df["AnnualIncome"] = pd.to_numeric(df["AnnualIncome"], errors="coerce").fillna(0)
    df["NumberOfDependents"] = pd.to_numeric(df["NumberOfDependents"], errors="coerce").fillna(0)
    
    # Compute IncomePerDependent safely.
    df["IncomePerDependent"] = df["AnnualIncome"] / (df["NumberOfDependents"] + 1)
    
    thresholds = get_thresholds().get("financial_status_thresholds", {})
    
    if suboption == "High Income":
        th = thresholds.get("High Income", {"min_income_per_dependent": 50000, "employment_status": "Employed"})
        return df[(df["IncomePerDependent"] > th["min_income_per_dependent"]) &
                  (df["EmploymentStatus"] == th["employment_status"])]
    
    elif suboption == "Medium Income":
        th = thresholds.get("Medium Income", {
            "min_income_per_dependent": 25000,
            "max_income_per_dependent": 50000,
            "employment_status": ["Employed", "Self Employed"]
        })
        return df[(df["IncomePerDependent"] > th["min_income_per_dependent"]) &
                  (df["IncomePerDependent"] <= th["max_income_per_dependent"]) &
                  (df["EmploymentStatus"].isin(th["employment_status"]))]
    
    elif suboption == "Low Income":
        th = thresholds.get("Low Income", {"max_income_per_dependent": 25000, "employment_status": "Unemployed"})
        # Using OR means a record qualifies if either its IncomePerDependent is low OR its EmploymentStatus is "Unemployed".
        # If you intend to require both conditions to be met, change the operator to &.
        return df[(df["IncomePerDependent"] <= th["max_income_per_dependent"]) |
                  (df["EmploymentStatus"] == th["employment_status"])]
    
    else:
        raise ValueError("Invalid financial status suboption provided.")


# ---------------------------------------------------
# CRITERIA Dictionary using Cached Thresholds
# ---------------------------------------------------
CRITERIA = {
    # Duration criteria using dynamic "duration_thresholds"
    "Duration": {
        "Short-Term": lambda df: df[df["LoanDuration"] <= get_thresholds().get("duration_thresholds", {}).get("Short-Term", {"max_duration": 12}).get("max_duration", 12)],
        "Medium-Term": lambda df: df[(df["LoanDuration"] >= get_thresholds().get("duration_thresholds", {}).get("Medium-Term", {"min_duration": 13}).get("min_duration", 13)) &
                                      (df["LoanDuration"] <= get_thresholds().get("duration_thresholds", {}).get("Medium-Term", {"max_duration": 60}).get("max_duration", 60))],
        "Long-Term": lambda df: df[df["LoanDuration"] >= get_thresholds().get("duration_thresholds", {}).get("Long-Term", {"min_duration": 61}).get("min_duration", 61)]
    },
    "Creditworthiness": {
        "Excellent": lambda df: df[df.apply(lambda row: is_excellent_credit(row) and has_no_defaults_or_bankruptcy(row), axis=1)],
        "Good": lambda df: df[df.apply(lambda row: is_good_credit(row) and has_no_defaults_or_bankruptcy(row), axis=1)],
        "Fair": lambda df: df[df.apply(lambda row: is_fair_credit(row) and has_no_defaults_or_bankruptcy(row), axis=1)],
        "Poor": lambda df: df[((df["CreditScore"] < 600) |
                               (df["LengthOfCreditHistory"] < 3) |
                               (df["NumberOfCreditInquiries"] > 5) |
                               (df["PreviousLoanDefaults"] == 1) |
                               (df["BankruptcyHistory"] == 1))]
    },
  
    "Risk-Based": {
    # Very Low Risk: Best credit profiles with high scores, low monthly payments, and solid employment.
    "Very Low Risk": lambda df: df[
        (df["CreditScore"] >= get_thresholds().get("custom_risk_thresholds", {}).get("Very Low Risk", {"min_credit_score": 750}).get("min_credit_score", 750)) &
        (df["MonthlyLoanPayment"] <= get_thresholds().get("custom_risk_thresholds", {}).get("Very Low Risk", {"max_monthly_payment": 1500}).get("max_monthly_payment", 1500)) &
        (df["EmploymentStatus"].isin(get_thresholds().get("custom_risk_thresholds", {}).get("Very Low Risk", {"employment_status": ["Employed", "Self-Employed"]}).get("employment_status", ["Employed", "Self-Employed"]))) &
        (df.apply(has_no_defaults_or_bankruptcy, axis=1))
    ],
    # Low Risk: Strong profiles, but with slightly lower credit scores or a bit higher monthly payments.
    "Low Risk": lambda df: df[
        (df["CreditScore"] >= get_thresholds().get("custom_risk_thresholds", {}).get("Low Risk", {"min_credit_score": 680}).get("min_credit_score", 680)) &
        (df["CreditScore"] < get_thresholds().get("custom_risk_thresholds", {}).get("Low Risk", {"max_credit_score": 750}).get("max_credit_score", 750)) &
        (df["MonthlyLoanPayment"] <= get_thresholds().get("custom_risk_thresholds", {}).get("Low Risk", {"max_monthly_payment": 3000}).get("max_monthly_payment", 3000)) &
        (df["EmploymentStatus"].isin(get_thresholds().get("custom_risk_thresholds", {}).get("Low Risk", {"employment_status": ["Employed", "Self-Employed"]}).get("employment_status", ["Employed", "Self-Employed"]))) &
        (df.apply(has_no_defaults_or_bankruptcy, axis=1))
    ],
    # Medium Risk: Moderate credit scores with acceptable monthly payments, may include a broader range of employment types.
    "Medium Risk": lambda df: df[
        (df["CreditScore"] >= get_thresholds().get("custom_risk_thresholds", {}).get("Medium Risk", {"min_credit_score": 600}).get("min_credit_score", 600)) &
        (df["CreditScore"] < get_thresholds().get("custom_risk_thresholds", {}).get("Medium Risk", {"max_credit_score": 680}).get("max_credit_score", 680)) &
        (df["MonthlyLoanPayment"] <= get_thresholds().get("custom_risk_thresholds", {}).get("Medium Risk", {"max_monthly_payment": 6000}).get("max_monthly_payment", 6000)) &
        (df["EmploymentStatus"].isin(get_thresholds().get("custom_risk_thresholds", {}).get("Medium Risk", {"employment_status": ["Employed", "Self-Employed", "Part-Time"]}).get("employment_status", ["Employed", "Self-Employed", "Part-Time"]))) &
        (df.apply(has_no_defaults_or_bankruptcy, axis=1))
    ],
    # High Risk: Any significant red flags such as low credit score, very high monthly payments,
    # non-preferred employment, or a history of defaults/bankruptcy.
    "High Risk": lambda df: df[
        (df["CreditScore"] < get_thresholds().get("custom_risk_thresholds", {}).get("High Risk", {"max_credit_score": 600}).get("max_credit_score", 600)) |
        (df["MonthlyLoanPayment"] > get_thresholds().get("custom_risk_thresholds", {}).get("High Risk", {"min_monthly_payment": 6000}).get("min_monthly_payment", 6000)) |
        (~df["EmploymentStatus"].isin(get_thresholds().get("custom_risk_thresholds", {}).get("High Risk", {"employment_status": ["Employed", "Self-Employed"]}).get("employment_status", ["Employed", "Self-Employed"]))) |
        (~df.apply(has_no_defaults_or_bankruptcy, axis=1))
    ]
},

    "Liquidity": {
        "High Liquidity": lambda df: filter_liquidity(df, "High Liquidity"),
        "Medium Liquidity": lambda df: filter_liquidity(df, "Medium Liquidity"),
        "Low Liquidity": lambda df: filter_liquidity(df, "Low Liquidity"),
    },
    "Debt Analysis": {
        "Low Debt": lambda df: df[df["DebtToIncomeRatio"] <= 30],
        "Moderate Debt": lambda df: df[(df["DebtToIncomeRatio"] > 30) & (df["DebtToIncomeRatio"] <= 50)],
        "High Debt": lambda df: df[(df["DebtToIncomeRatio"] > 50) | (df["BankruptcyHistory"] == 1)],
    },
    "Financial Liabilities": {
        "Not Trustable": lambda df: df[(df["TotalDebtToIncomeRatio"] >= 50) | (df["PreviousLoanDefaults"] == 1) | (df["BankruptcyHistory"] == 1)],
        "Moderate Trustable": lambda df: df[(df["TotalDebtToIncomeRatio"] > 30) & (df["TotalDebtToIncomeRatio"] <= 50) &
                                            (df["PreviousLoanDefaults"] == 0) & (df["BankruptcyHistory"] == 0)],
        "Highly Trustable": lambda df: df[(df["TotalDebtToIncomeRatio"] <= 30) & (df["PreviousLoanDefaults"] == 0) & (df["BankruptcyHistory"] == 0)],
    },
    "Age": {
        "Young Borrowers": lambda df: df[df["Age"] < 30],
        "Mid-Career Borrowers": lambda df: df[(df["Age"] >= 30) & (df["Age"] <= 50)],
        "Senior Borrowers": lambda df: df[df["Age"] > 50],
    },
    "Financial Status": {
        "High Income": lambda df: filter_financial_status(df, "High Income"),
        "Medium Income": lambda df: filter_financial_status(df, "Medium Income"),
        "Low Income": lambda df: filter_financial_status(df, "Low Income"),
    }
}

# ---------------------------------------------------
# Pooling and Allocation Functions
# ---------------------------------------------------

def pool_loans(df: pd.DataFrame, criterion: str, suboption: str) -> pd.DataFrame:
    """
    Pools loans based on the given criterion and suboption.
    """
    if criterion in CRITERIA and suboption in CRITERIA[criterion]:
        return CRITERIA[criterion][suboption](df)
    else:
        print("Invalid criterion selected.")
        return pd.DataFrame()  # Return an empty DataFrame

def filter_by_budget(tranche_df: pd.DataFrame, budget: float) -> pd.DataFrame:
    """
    Filters the given tranche DataFrame so that only loans are selected until the cumulative LoanAmount
    does not exceed the investor budget.
    """
    tranche_df = tranche_df.sort_values(by="LoanAmount", ascending=True)
    tranche_df = tranche_df[tranche_df["LoanAmount"].cumsum() <= budget]
    return tranche_df

def allocate_tranches(df: pd.DataFrame, criterion: str, suboption: str, investor_budget: float) -> dict:
    """
    Pools loans based on the chosen criterion, classifies them into tranches,
    and ensures that the total loan amount in each tranche does not exceed the investor's budget.
    """
    df = preprocess_loan_data(df)
    pooled_loans = pool_loans(df, criterion, suboption)
    if pooled_loans is None or pooled_loans.empty:
        print("No loans available for the selected criterion.")
        return None

    pooled_loans = pooled_loans.copy()
    pooled_loans["Tranche"] = pooled_loans.apply(classify_tranche, axis=1)

    # Group loans by Tranche.
    grouped_tranches = pooled_loans.groupby("Tranche")
    selected_loans_per_tranche = {}

    for tranche, loans in grouped_tranches:
        # Sort loans (priority: PredictedRiskScore ascending, LoanAmount ascending).
        loans = loans.sort_values(by=["Predicted_RiskScore", "LoanAmount"], ascending=[True, True])
        # Use the filter_by_budget function to select loans within the budget.
        filtered_loans = filter_by_budget(loans, investor_budget)
        selected_loans_per_tranche[tranche] = filtered_loans
        total_amount = filtered_loans["LoanAmount"].sum() if not filtered_loans.empty else 0
        print(f"{tranche}: {len(filtered_loans)} loans selected, Total Amount: {total_amount} (Budget: {investor_budget})")

    return selected_loans_per_tranche
