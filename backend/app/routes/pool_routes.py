# App/routes/pool_routes.py
from fastapi import APIRouter, HTTPException
import pandas as pd
from app.config.database import get_database
from app.services.pool_service import allocate_tranches
from app.ml.risk_model import load_ml_risk_scores, get_updated_dataset, get_risk_score
from app.ml.analysis import generate_ai_report,summarize_tranche_allocation,analyze_macro_impact,process_loan_data
import logging

router = APIRouter()

# Get the loan database and its loans collection.
loan_db = get_database()
loans_collection = loan_db["loans"]
MODEL_PKL = 'loan_risk_model.pkl'


@router.post("/allocate")
def allocate_tranches_endpoint(criterion: str, suboption: str, investor_budget: float):
    """
    Fetches loans from the loan database, pools them based on the selected criterion and suboption,
    applies the investor_budget constraint during tranche allocation,
    stores the tranche records in the separate tranche database,
    and returns a summary.
    """
    # Fetch all loans from the loans collection.
    loans = list(loans_collection.find({}))
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found in the loan database.")

    # Convert MongoDB records into a pandas DataFrame.
    df = pd.DataFrame(loans)
    if df.empty:
        raise HTTPException(status_code=404, detail="Loan data is empty after conversion.")

    # Call the pooling and tranche allocation function from the service,
    # passing investor_budget as an additional parameter.

    df = df.drop(columns=["_id", "investor_id", "status", "tranche_type"], errors='ignore')

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

    # Prepare and store tranche data in the separate tranche database.
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
    
    # Prepare the detailed output per tranche.
    tranche_details = []
    # Ensure we output all four tranche types, even if no loans were allocated.
    for tranche_key in static_tranche_info.keys():
        # Use the computed allocation if available, otherwise an empty DataFrame.
        if tranche_key in tranches:
            df_tranche = tranches[tranche_key]
        else:
            # For the equity tranche, our service might return "Equity Tranche" instead.
            if "Equity Tranche" in tranches:
                df_tranche = tranches["Equity Tranche"]
            else:
                df_tranche = pd.DataFrame()

        loans_allocated = len(df_tranche) if not df_tranche.empty else 0
        budget_spent = float(df_tranche['LoanAmount'].sum()) if not df_tranche.empty and 'LoanAmount' in df_tranche.columns else 0.0
        info = static_tranche_info[tranche_key]
        tranche_details.append({
            "tranche_name": tranche_key,
            "risk_category": info["Risk"],
            "return_category": info["Return"],
            "payment_priority": info["Payment Priority"],
            "loans_allocated": loans_allocated,
            "budget_spent": budget_spent,
            "investor_budget": investor_budget
        })
    
    
    # Return the detailed tranche allocation information as JSON.
    return {
        "message": "Tranches allocated and stored successfully.",
        "tranche_details": tranche_details
    }


@router.get("/generate_report")
def generate_report(criterion: str, suboption: str, investor_budget: float):
    loans = list(loans_collection.find({}))
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found in the loan database.")

    # Convert MongoDB records into a pandas DataFrame.
    df = pd.DataFrame(loans)
    if df.empty:
        raise HTTPException(status_code=404, detail="Loan data is empty after conversion.")

    # Call the pooling and tranche allocation function from the service,
    # passing investor_budget as an additional parameter.
    df = df.drop(columns=["_id", "investor_id", "status", "tranche_type"], errors='ignore')

    predictions = get_risk_score(MODEL_PKL,df)
    if predictions is None:
        raise HTTPException(status_code=500, detail="Risk score predictions failed.")

    df = get_updated_dataset(df, predictions)

    logging.info(f"columns in df are {df.columns}")

    loan_data = process_loan_data(df)
    logging.info(f"columns in loan_data are {loan_data.columns}")

    selected_loans_per_tranche = allocate_tranches(loan_data, criterion, suboption,investor_budget)
    tranche_summary = summarize_tranche_allocation(selected_loans_per_tranche, criterion, suboption)
    macro_impact_summary = analyze_macro_impact(selected_loans_per_tranche, loan_data)
    ai_report = generate_ai_report(tranche_summary, macro_impact_summary)
    return {"report": ai_report}


