# App/routes/pool_routes.py
import datetime
from fastapi import APIRouter, HTTPException
import pandas as pd
from bson import ObjectId
from app.config.database import get_database
from app.services.pool_service import allocate_tranches
import logging

router = APIRouter()

# Get the loan database and its loans collection.
loan_db = get_database()
loans_collection = loan_db["loans"]



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
        "Equity/Residual Tranche": {
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
