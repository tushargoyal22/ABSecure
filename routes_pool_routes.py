from fastapi import APIRouter, HTTPException
import pandas as pd
from bson import ObjectId
from App.config.database import get_database, get_tranche_database
from App.services.pool_service import allocate_tranches
import logging
import datetime
import json

router = APIRouter()

# Get the loan database and its loans collection.
loan_db = get_database()
loans_collection = loan_db["loans"]

# Get the separate tranche database and its tranches collection.
tranche_db = get_tranche_database()
tranches_collection = tranche_db["tranches"]

@router.post("/allocate")
def allocate_tranches_endpoint(criterion: str, suboption: str):
    # Fetch all loans from the loans collection.
    loans = list(loans_collection.find({}))
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found in the loan database.")

    # Convert MongoDB records into a pandas DataFrame.
    df = pd.DataFrame(loans)
    if df.empty:
        raise HTTPException(status_code=404, detail="Loan data is empty after conversion.")

    # Call the pooling and tranche allocation function from the service.
    tranches = allocate_tranches(df, criterion, suboption)
    if tranches is None or all(tranche_df.empty for tranche_df in tranches.values()):
        raise HTTPException(status_code=404, detail="No loans available for the selected criteria.")

    # Prepare and store tranche data in the separate tranche database.
    stored_tranches = []
    tranche_summary = {}

    for tranche_name, tranche_df in tranches.items():
        count = len(tranche_df)
        tranche_summary[tranche_name] = count
        if count > 0:
            # Convert DataFrame to list of dictionaries
            records = tranche_df.to_dict(orient="records")
            for record in records:
                # Remove the original _id field so MongoDB assigns a new one
                if "_id" in record:
                    del record["_id"]
                record["Tranche"] = tranche_name
                record["pooled_by"] = criterion
                record["suboption"] = suboption
                record["timestamp"] = datetime.datetime.utcnow()
                stored_tranches.append(record)

    if stored_tranches:
        tranches_collection.insert_many(stored_tranches)

    return {
        "message": "Tranches allocated and stored successfully in the tranche database.",
        "tranche_counts": tranche_summary
    }

@router.get("/tranches")
def get_stored_tranches():
    records = list(tranches_collection.find({}, {"_id": 0}))
    if not records:
        raise HTTPException(status_code=404, detail="No tranches found in the tranche database.")
    return {"tranches": records}

