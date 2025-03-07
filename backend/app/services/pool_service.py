import pandas as pd
import numpy as np  # Used for handling division by zero (np.nan)

def classify_tranche(loan: dict) -> str:
    """
    Assigns a tranche to a loan based on its RiskScore.
    """
    if loan.get("RiskScore", 0) > 85:
        return "Senior Tranche"
    elif loan.get("RiskScore", 0) > 70:
        return "Mezzanine Tranche"
    elif loan.get("RiskScore", 0) > 50:
        return "Subordinated Tranche"
    else:
        return "Equity Tranche"

# Helper functions for creditworthiness checks

def has_no_defaults_or_bankruptcy(row):
    return (row["PreviousLoanDefaults"] == 0) and (row["BankruptcyHistory"] == 0)

def is_excellent_credit(row):
    return ((row["CreditScore"] >= 800) or 
            (row["LengthOfCreditHistory"] > 10) or 
            ((3 <= row["NumberOfOpenCreditLines"] <= 7) and (row["NumberOfCreditInquiries"] <= 2)))

def is_good_credit(row):
    return ((700 <= row["CreditScore"] < 800) or
            (row["LengthOfCreditHistory"] >= 7) or
            ((3 <= row["NumberOfOpenCreditLines"] <= 12) and (row["NumberOfCreditInquiries"] <= 4)))

def is_fair_credit(row):
    return ((600 <= row["CreditScore"] < 700) or
            (3 <= row["LengthOfCreditHistory"] <= 6) or
            (row["NumberOfOpenCreditLines"] > 12) or
            (row["NumberOfCreditInquiries"] > 4))

# Helper function for Liquidity criteria
def filter_liquidity(df, suboption):
    df = df.copy()
    df['LoanAmount'] = df['LoanAmount'].replace(0, np.nan)
    df['LoanDuration'] = df['LoanDuration'].replace(0, np.nan)
    df['Liquidity_Ratio'] = (df['SavingsAccountBalance'] + df['CheckingAccountBalance']) / df['LoanAmount']
    df['Relative_Ratio'] = df['MonthlyIncome'] / (df['LoanAmount'] / df['LoanDuration'])
    if suboption == "High Liquidity":
        return df[(df["Liquidity_Ratio"] > 1) | (df["Relative_Ratio"] >= 3)]
    elif suboption == "Medium Liquidity":
        return df[((df["Liquidity_Ratio"] > 0.5) | (df["Relative_Ratio"] >= 2)) & (df["Relative_Ratio"] < 3)]
    elif suboption == "Low Liquidity":
        return df[(df["Liquidity_Ratio"] <= 0.5) | (df["Relative_Ratio"] <= 1)]

# Helper function for Financial Status criteria
def filter_financial_status(df, suboption):
    df = df.copy()
    df["IncomePerDependent"] = df["AnnualIncome"] / (df["NumberOfDependents"] + 1)
    if suboption == "High Income":
        return df[(df["IncomePerDependent"] > 50000) & (df["EmploymentStatus"] == "Employed")]
    elif suboption == "Medium Income":
        return df[(df["IncomePerDependent"] > 25000) & (df["IncomePerDependent"] <= 50000) &
                  (df["EmploymentStatus"].isin(["Employed", "Self Employed"]))]
    elif suboption == "Low Income":
        return df[(df["IncomePerDependent"] <= 25000) | (df["EmploymentStatus"] == "Unemployed")]

# Dictionary mapping of criteria to filtering functions
CRITERIA = {
    "Duration": {
        "Short-Term": lambda df: df[df["LoanDuration"] <= 12],
        "Medium-Term": lambda df: df[(df["LoanDuration"] > 12) & (df["LoanDuration"] <= 60)],
        "Long-Term": lambda df: df[df["LoanDuration"] > 60],
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
    "ML-Based Risk": {
        "Low-Risk": lambda df: df[df["RiskScore"] > 80],
        "Medium-Risk": lambda df: df[(df["RiskScore"] > 50) & (df["RiskScore"] <= 80)],
        "High-Risk": lambda df: df[df["RiskScore"] <= 50],
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
        "Highly Trustable": lambda df: df[(df["TotalDebtToIncomeRatio"] <= 30) & ((df["PreviousLoanDefaults"] == 0) & (df["BankruptcyHistory"] == 0))],
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
        # Sort loans (priority: RiskScore descending, LoanAmount ascending).
        loans = loans.sort_values(by=["RiskScore", "LoanAmount"], ascending=[False, True])
        # Use the filter_by_budget function to select loans within the budget.
        filtered_loans = filter_by_budget(loans, investor_budget)
        selected_loans_per_tranche[tranche] = filtered_loans
        total_amount = filtered_loans["LoanAmount"].sum() if not filtered_loans.empty else 0
        print(f"{tranche}: {len(filtered_loans)} loans selected, Total Amount: {total_amount} (Budget: {investor_budget})")

    return selected_loans_per_tranche
    