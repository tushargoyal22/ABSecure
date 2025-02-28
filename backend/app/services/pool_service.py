from app.config.database import get_database  # Import database connection
import logging
from bson import ObjectId  
from pymongo import InsertOne  

db = get_database()

def group_loans(loan_ids):
    logging.info("🔹 Grouping Loans...")

    # Convert string loan_ids to ObjectId and fetch full loan details
    object_ids = [ObjectId(loan_id) for loan_id in loan_ids]
    logging.info(f"DEBUG - Object IDs to fetch: {object_ids}")

    loans = list(db.loans.find({"_id": {"$in": object_ids}}, {"RiskScore": 1, "_id": 1}))
    logging.info(f"DEBUG - Loans Retrieved: {loans}")

    if not loans:
        logging.warning("⚠️ No valid loans found!")
        return {"message": "No valid loans found in database"}

    grouped_pools = {}

    for loan in loans:
        if not isinstance(loan, dict):
            logging.error(f"❌ Loan is not a dictionary: {loan}")
            continue

        risk_score = loan.get("RiskScore")

        if risk_score is None:
            logging.warning(f"⚠️ Loan {loan['_id']} missing RiskScore!")
            continue

        # Categorize risk levels (e.g., Risk-30, Risk-40, etc.)
        risk_category = f"Risk-{int(risk_score // 10) * 10}"

        if risk_category not in grouped_pools:
            grouped_pools[risk_category] = []

        grouped_pools[risk_category].append(str(loan["_id"]))  # Convert ObjectId to string

    logging.info(f"✅ Loan Pooling Completed! Result: {grouped_pools}")

    # ✅ Insert each risk category as a separate document
    operations = [
        InsertOne({"risk_level": risk, "loans": loan_ids})
        for risk, loan_ids in grouped_pools.items()
    ]

    if operations:
        db.loan_pools.bulk_write(operations)

    logging.info(f"✅ Loan Pools saved to DB successfully!")

    return {"message": "Loan pools created successfully!"}
