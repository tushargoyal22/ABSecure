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

def pool_loans(df: pd.DataFrame, criterion: str, suboption: str) -> pd.DataFrame:
    """
    Pools loans based on the given criterion and suboption.
    """
    if criterion == "Duration":
        if suboption == "Short-Term":
            return df[df["LoanDuration"] <= 12]
        elif suboption == "Medium-Term":
            return df[(df["LoanDuration"] > 12) & (df["LoanDuration"] <= 60)]
        elif suboption == "Long-Term":
            return df[df["LoanDuration"] > 60]

    elif criterion == "Creditworthiness":
        if suboption == "Excellent":
            return df[df.apply(lambda row: is_excellent_credit(row) and has_no_defaults_or_bankruptcy(row), axis=1)]
        elif suboption == "Good":
            return df[df.apply(lambda row: is_good_credit(row) and has_no_defaults_or_bankruptcy(row), axis=1)]
        elif suboption == "Fair":
            return df[df.apply(lambda row: is_fair_credit(row) and has_no_defaults_or_bankruptcy(row), axis=1)]
        elif suboption == "Poor":
            return df[((df["CreditScore"] < 600) |
                       (df["LengthOfCreditHistory"] < 3) |
                       (df["NumberOfCreditInquiries"] > 5) |
                       (df["PreviousLoanDefaults"] == 1) |
                       (df["BankruptcyHistory"] == 1))]
    
    elif criterion == "ML-Based Risk":
        if suboption == "Low-Risk":
            return df[df["RiskScore"] > 80]
        elif suboption == "Medium-Risk":
            return df[(df["RiskScore"] > 50) & (df["RiskScore"] <= 80)]
        elif suboption == "High-Risk":
            return df[df["RiskScore"] <= 50]
    
    elif criterion == "Liquidity":
        df = df.copy()
        # Replace zero denominators with NaN to avoid division errors
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
    
    elif criterion == "Debt Analysis":
        if suboption == "Low Debt":
            return df[df["DebtToIncomeRatio"] <= 30]
        elif suboption == "Moderate Debt":
            return df[(df["DebtToIncomeRatio"] > 30) & (df["DebtToIncomeRatio"] <= 50)]
        elif suboption == "High Debt":
            # Corrected boolean condition using proper parentheses
            return df[(df["DebtToIncomeRatio"] > 50) | (df["PreviousLoanDefaults"] == 1)]
    
    elif criterion == "Financial Liabilities":
        if suboption == "Not Trustable":
            # Corrected boolean condition using proper parentheses
            return df[(df["TotalDebtToIncomeRatio"] <= 30) | (df["PreviousLoanDefaults"] == 1) | (df["BankruptcyHistory"] == 1)]
        elif suboption == "Moderate Trustable":
            return df[(df["TotalDebtToIncomeRatio"] > 30) & (df["TotalDebtToIncomeRatio"] <= 50) &
                      (df["PreviousLoanDefaults"] == 0) & (df["BankruptcyHistory"] == 0)]
        elif suboption == "Highly Trustable":
            return df[(df["TotalDebtToIncomeRatio"] > 50) | ((df["PreviousLoanDefaults"] == 0) & (df["BankruptcyHistory"] == 0))]
    
    elif criterion == "Age":
        if suboption == "Young Borrowers":
            return df[df["Age"] < 30]
        elif suboption == "Mid-Career Borrowers":
            return df[(df["Age"] >= 30) & (df["Age"] <= 50)]
        elif suboption == "Senior Borrowers":
            return df[df["Age"] > 50]
    
    elif criterion == "Financial Status":
        df = df.copy()
        df["IncomePerDependent"] = df["AnnualIncome"] / (df["NumberOfDependents"] + 1)
        if suboption == "High Income":
            return df[(df["IncomePerDependent"] > 50000) & (df["EmploymentStatus"] == "Employed")]
        elif suboption == "Medium Income":
            return df[(df["IncomePerDependent"] > 25000) & (df["IncomePerDependent"] <= 50000) &
                      (df["EmploymentStatus"].isin(["Employed", "Self Employed"]))]
        elif suboption == "Low Income":
            return df[(df["IncomePerDependent"] <= 25000) | (df["EmploymentStatus"] == "Unemployed")]
    
    else:
        print("Invalid criterion selected.")
        return pd.DataFrame()  # Return an empty DataFrame

def filter_by_budget(tranche_df: pd.DataFrame, budget: float) -> pd.DataFrame:
    """
    Filters the given tranche DataFrame so that only loans are selected until the cumulative LoanAmount
    does not exceed the investor_budget.
    """
    tranche_df = tranche_df.sort_values(by="LoanAmount", ascending=True)
    cumulative_sum = 0.0
    selected_rows = []
    for index, row in tranche_df.iterrows():
        cumulative_sum += row["LoanAmount"]
        if cumulative_sum <= budget:
            selected_rows.append(row)
        else:
            break
    return pd.DataFrame(selected_rows)

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

    # if selected_loans_per_tranche:
    #     final_allocation = pd.concat(selected_loans_per_tranche.values(), ignore_index=True)
    #     print(f"Total loans allocated: {len(final_allocation)}")
    #     print(f"Total amount allocated: {final_allocation['LoanAmount'].sum()} (Budget: {investor_budget})")
    # else:
    #     print("No loans allocated after applying budget constraint.")

    return selected_loans_per_tranche