import os
# Add 'backend' to Python's module search path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import logging
import requests
import pandas as pd
import yfinance as yf
import kagglehub
import google.generativeai as genai
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.services.pool_service import allocate_tranches

#from app.services.pool_service import allocate_tranches
from app.ml.risk_model import get_updated_dataset, get_risk_score

# Load environment variables
load_dotenv()

# Constants
MODEL_PKL = "loan_risk_model.pkl" 
api_key = os.getenv("api_key")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def download_loan_data():
    """Download loan dataset from Kaggle."""
    logging.info("Downloading Loan Dataset from Kaggle...")
    path = kagglehub.dataset_download("lorenzozoppelletto/financial-risk-for-loan-approval")
    logging.info(f"Dataset downloaded at: {path}")
    return pd.read_csv(os.path.join(path, "Loan.csv"))


# Function to Process Loan Data with Macroeconomic Features
def process_loan_data(df,start_year=2018, end_year=2024):
    logging.info("Fetching macroeconomic data...")

    # Step 1: Fetch macroeconomic data from Yahoo Finance
    tickers = {
        "interest_rate": "^IRX",  # 13-week Treasury Bill Rate
        "bond_yield": "^TNX",  # 10-Year Treasury Yield
        "market_volatility": "^VIX"  # VIX Index
    }

    macro_data = {}
    for key, ticker in tickers.items():
        asset = yf.Ticker(ticker)
        hist = asset.history(period="max")
        hist.index = hist.index.year
        macro_data[key] = hist["Close"].groupby(hist.index).mean()

    df_macro = pd.DataFrame(macro_data)
    df_macro = df_macro.loc[start_year:end_year].reset_index().rename(columns={"Date": "Year"})

    logging.info("Fetching inflation data from FRED API...")

    # Step 2: Fetch inflation data from FRED API
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json"
    response = requests.get(url).json()

    inflation_data = pd.DataFrame(response["observations"])
    inflation_data["date"] = pd.to_datetime(inflation_data["date"])
    inflation_data["Year"] = inflation_data["date"].dt.year
    inflation_data["Inflation"] = inflation_data["value"].astype(float)
    inflation_data["InflationRate"] = inflation_data["Inflation"].pct_change(12) * 100
    inflation_data = inflation_data[["Year", "InflationRate"]].dropna().groupby("Year").mean().reset_index()

    # Merge macroeconomic and inflation data
    merged_data = pd.merge(df_macro, inflation_data, on='Year', how='left')

    logging.info("Merging loan dataset with macroeconomic indicators...")

    # Step 3: Merge with Loan Data
    df['ApplicationYear'] = pd.to_datetime(df['ApplicationDate']).dt.year
    loan_data = df[(df['ApplicationYear'] >= start_year) & (df['ApplicationYear'] <= end_year)]
    loan_data = pd.merge(loan_data, merged_data, left_on='ApplicationYear', right_on='Year', how='left')

    # Step 4: Compute Financial Risk Metrics
    logging.info("Computing financial risk metrics...")

    loan_data["InterestRateSensitivity"] = loan_data["LoanAmount"] * (
                loan_data["interest_rate"] / loan_data["BaseInterestRate"])
    loan_data["DebtSensitivityRatio"] = loan_data["TotalDebtToIncomeRatio"] * (
                1 + loan_data["InflationRate"].iloc[0] / 100)
    loan_data["MarketVolatilityImpact"] = loan_data["RiskScore"] * (loan_data["market_volatility"].iloc[0] / 20)

    loan_data["InterestImpact"] = loan_data["LoanAmount"] * (loan_data["InterestRate"] / loan_data["interest_rate"])
    loan_data["InflationImpact"] = loan_data["TotalDebtToIncomeRatio"] * (loan_data["InflationRate"] / 100)

    logging.info("Loan data processing completed.")
    logging.info(f"the data is {loan_data.head()}")

    return loan_data





def summarize_tranche_allocation(selected_loans_per_tranche, criterion, suboption):
    """Generate a summary of the tranche allocation."""
    if selected_loans_per_tranche is None:
        return None
    summary = f"Investor selected loans based on '{criterion}' with suboption '{suboption}'.\nTranche Allocation Summary:\n"
    for tranche, loans in selected_loans_per_tranche.items():
        total_loans = len(loans)
        total_amount = loans["LoanAmount"].sum() if not loans.empty else 0
        avg_risk_score = loans["RiskScore"].mean() if not loans.empty else 0
        summary += f" - {tranche}: {total_loans} loans, Total Amount: {total_amount}, Avg Risk Score: {avg_risk_score:.2f}\n"
    return summary


def analyze_macro_impact(selected_loans_per_tranche, loan_data):
    """Analyze macroeconomic impact on selected tranches."""
    if selected_loans_per_tranche is None  or loan_data is None:
        return None
    summary = "Macroeconomic Impact on Tranches:\n"
    for tranche, loans in selected_loans_per_tranche.items():

        if loans.empty:
            summary += f" - {tranche}: No loans in this tranche.\n"
            continue
        loans["InterestImpact"] = loans["LoanAmount"] * (loans["InterestRate"] / loan_data["interest_rate"])
        logging.info(f"LoanAmount: {loans['LoanAmount']}")
        logging.info(f"InterestRate: {loans['InterestRate']}")
        logging.info(f"interest_rate: {loan_data['interest_rate']}")
        loans["InflationImpact"] = loans["TotalDebtToIncomeRatio"] * (loans["InflationRate"] / 100)
        summary += f" - {tranche}: Avg Interest Impact: {loans['InterestImpact'].mean()}, Avg Inflation Impact: {loans['InflationImpact'].mean()}\n"
    return summary


def generate_ai_report(tranche_summary, macro_impact_summary):
    """Generate AI-powered report using Google Gemini AI."""

    if not GENAI_API_KEY:
        logging.error("Google Gemini API Key is missing. Cannot generate AI report.")
        return "AI Report generation failed due to missing API key."
    if tranche_summary is None or macro_impact_summary is None:
        return "No loans available under this category"

    genai.configure(api_key=GENAI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Imagine yourself as a bank manager and generate a structured loan securitization report:
    {tranche_summary}
    {macro_impact_summary}
    Just have the following sections:
    Securitization Type,Underlying Assets,Investor Selection Criteria,
    I. Tranche Allocation Summary
    II. Macroeconomic Impact Analysis
    III.  Discussion of Findings
    IV. Conclusion
    V. Disclaimer
    Also explain the financial terms used in the report in a structured manner.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error generating AI report: {e}")
        return "AI Report generation failed."


# Main Execution Flow
df = download_loan_data()
predictions = get_risk_score(MODEL_PKL, df)
df = get_updated_dataset(df, predictions)
loan_data = process_loan_data(df)
selected_loans_per_tranche = allocate_tranches(loan_data, criterion='Liquidity', suboption='High Liquidity',
                                               investor_budget=20000)
tranche_summary = summarize_tranche_allocation(selected_loans_per_tranche, "Liquidity", "High Liquidity")
macro_impact_summary = analyze_macro_impact(selected_loans_per_tranche, loan_data)
ai_report = generate_ai_report(tranche_summary, macro_impact_summary)
logging.info(ai_report)

