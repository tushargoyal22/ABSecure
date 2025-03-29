"""FastAPI router for loan tranche allocation and reporting.

This module provides endpoints for allocating loans into different risk tranches
and generating AI-powered financial reports based on the allocations.
"""

from fastapi import APIRouter, HTTPException
import pandas as pd
from app.config.database import get_database
from app.services.pool_service import allocate_tranches
from app.ml.risk_model import load_ml_risk_scores, get_updated_dataset, get_risk_score
from app.ml.analysis import generate_ai_report, summarize_tranche_allocation, analyze_macro_impact, process_loan_data
import logging

router = APIRouter()

# Get the loan database and its loans collection.
loan_db = get_database()
loans_collection = loan_db["loans"]
MODEL_PKL = 'loan_risk_model.pkl'

@router.post("/allocate")
def allocate_tranches_endpoint(criterion: str, suboption: str, investor_budget: float):
    """Allocate loans into tranches based on criteria and budget.

    This endpoint takes allocation criteria and investor budget, processes loan data,
    calculates risk scores, and allocates loans into appropriate tranches (Senior,
    Mezzanine, Subordinated, Equity).

    Args:
        criterion (str): Primary criterion for loan selection (e.g., 'Risk', 'Return')
        suboption (str): Sub-criterion refining the selection (e.g., 'Low', 'Medium')
        investor_budget (float): Total available budget for investment

    Returns:
        dict: Dictionary containing:
            - message: Status message
            - tranche_details: List of dictionaries with tranche allocation details

    Raises:
        HTTPException: 404 if no loans found or data is empty
        HTTPException: 500 if risk score prediction fails
    """
    # Fetch all loans from the loans collection.
    loans = list(loans_collection.find({}))
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found in the loan database.")

    # Convert MongoDB records into a pandas DataFrame.
    df = pd.DataFrame(loans)
    if df.empty:
        raise HTTPException(status_code=404, detail="Loan data is empty after conversion.")

    df = df.drop(columns=["investor_id", "status", "tranche_type"], errors='ignore')
    predictions = load_ml_risk_scores(df)
    if predictions is None:
        raise HTTPException(status_code=500, detail="Risk score predictions failed.")
    df = get_updated_dataset(df, predictions)

    logging.info(f"DataFrame columns after update: {df.columns.tolist()}")
    tranches = allocate_tranches(df, criterion, suboption, investor_budget)
    if tranches is None or all(tranche_df.empty for tranche_df in tranches.values()):
        return {
            "message": "No loans available for the selected criteria and budget.",
            "tranche_details": []
        }

    # Define static tranche information.
    static_tranche_info = {
        "Senior Tranche": {
            "Risk": "Lowest Risk",
            "Return": "Lowest Return",
            "Payment Priority": "First to be paid"
        },
        "Mezzanine Tranche": {
            "Risk": "Moderate Risk",
            "Return": "Moderate Return",
            "Payment Priority": "Paid after senior tranche"
        },
        "Subordinated Tranche": {
            "Risk": "High Risk",
            "Return": "High Return",
            "Payment Priority": "Paid after mezzanine"
        },
        "Equity Tranche": {
            "Risk": "Highest Risk",
            "Return": "Highest Return",
            "Payment Priority": "Last to be paid (if anything is left)"
        }
    }
    
    tranche_details = []
    for tranche_key in static_tranche_info.keys():
        df_tranche = tranches.get(tranche_key, pd.DataFrame())
        loans_allocated = len(df_tranche) if not df_tranche.empty else 0
        budget_spent = float(df_tranche['LoanAmount'].sum()) if not df_tranche.empty and 'LoanAmount' in df_tranche.columns else 0.0
        loan_ids = [str(oid) for oid in df_tranche['_id'].tolist()] if not df_tranche.empty and '_id' in df_tranche.columns else []
        
        weighted_risk = (df_tranche['RiskScore'] * df_tranche['LoanAmount']).sum() / df_tranche['LoanAmount'].sum() if not df_tranche.empty and 'RiskScore' in df_tranche.columns and 'LoanAmount' in df_tranche.columns else None
        
        info = static_tranche_info[tranche_key]
        tranche_details.append({
            "tranche_name": tranche_key,
            "risk_category": info["Risk"],
            "return_category": info["Return"],
            "payment_priority": info["Payment Priority"],
            "loans_allocated": loans_allocated,
            "budget_spent": budget_spent,
            "investor_budget": investor_budget,
            "loans": loan_ids,
            "average_risk": weighted_risk
        })
    
    return {
        "message": "Tranches allocated and stored successfully.",
        "tranche_details": tranche_details
    }

@router.get("/generate_report")
def generate_report(criterion: str, suboption: str, investor_budget: float):
    """Generate AI-powered financial report for tranche allocations.

    Creates a comprehensive report analyzing the tranche allocations, including
    risk assessment, return projections, and macroeconomic impact analysis.

    Args:
        criterion (str): Primary criterion for loan selection
        suboption (str): Sub-criterion refining the selection
        investor_budget (float): Total available budget for investment

    Returns:
        dict: Dictionary containing the AI-generated report

    Raises:
        HTTPException: 404 if no loans found or data is empty
        HTTPException: 500 if risk score prediction fails
    """
    loans = list(loans_collection.find({}))
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found in the loan database.")

    df = pd.DataFrame(loans)
    if df.empty:
        raise HTTPException(status_code=404, detail="Loan data is empty after conversion.")

    df = df.drop(columns=["_id", "investor_id", "status", "tranche_type"], errors='ignore')
    predictions = get_risk_score(MODEL_PKL, df)
    if predictions is None:
        raise HTTPException(status_code=500, detail="Risk score predictions failed.")
    df = get_updated_dataset(df, predictions)

    logging.info(f"columns in df are {df.columns}")
    loan_data = process_loan_data(df)
    logging.info(f"columns in loan_data are {loan_data.columns}")
    
    selected_loans_per_tranche = allocate_tranches(loan_data, criterion, suboption, investor_budget)
    tranche_summary = summarize_tranche_allocation(selected_loans_per_tranche, criterion, suboption)
    macro_impact_summary = analyze_macro_impact(selected_loans_per_tranche, loan_data)
    ai_report = generate_ai_report(tranche_summary, macro_impact_summary)
    
    return {"report": ai_report}