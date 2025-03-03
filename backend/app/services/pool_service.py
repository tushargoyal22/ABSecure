from app.config.database import get_database  # Import database connection
import logging
from bson import ObjectId  
from pymongo import InsertOne, errors  # Import error handling for bulk writes

db = get_database()

def group_loans(loan_ids):
    logging.info("🔹 Grouping Loans...")

    try:
        # ✅ Convert string loan_ids to ObjectId and fetch full loan details
        object_ids = [ObjectId(loan_id) for loan_id in loan_ids]
        logging.info(f"DEBUG - Object IDs to fetch: {object_ids}")

        # ✅ Fetch only necessary fields (_id and RiskScore) for efficiency
        loans = list(db.loans.find({"_id": {"$in": object_ids}}, {"RiskScore": 1, "_id": 1}))
        logging.info(f"DEBUG - Loans Retrieved: {loans}")

        if not loans:
            logging.warning("⚠️ No valid loans found!")
            return {"message": "No valid loans found in database"}
        
    except Exception as e:
        logging.error(f"❌ Database error while fetching loans: {e}")
        return {"message": "Database error occurred while retrieving loans"}

    grouped_pools = {}

    # ✅ Introduce a dynamic bucket size for flexible risk categorization
    bucket_size = 10  # Change this value if different risk buckets are needed

    for loan in loans:
        if not isinstance(loan, dict):
            logging.error(f"❌ Loan is not a dictionary: {loan}")
            continue  # ✅ Skip invalid loan entries instead of crashing

        risk_score = loan.get("RiskScore")

        if risk_score is None:
            logging.warning(f"⚠️ Loan {loan['_id']} missing RiskScore!")
            continue  # ✅ Skip loans without a RiskScore

        # ✅ Categorize risk levels dynamically based on the bucket size
        risk_category = f"Risk-{int(risk_score // bucket_size) * bucket_size}"

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
        try:
            db.loan_pools.bulk_write(operations)  # ✅ Handle bulk insert operation safely
            logging.info(f"✅ Loan Pools saved to DB successfully!")
        except errors.BulkWriteError as bwe:
            logging.error(f"❌ Bulk write error: {bwe.details}")
            return {"message": "Error while saving loan pools to the database"}
        except Exception as e:
            logging.error(f"❌ Unexpected error during bulk insert: {e}")
            return {"message": "Unexpected error occurred while saving loan pools"}

    return {"message": "Loan pools created successfully!"}
# ============================================
# 🔹 Summary of Changes Made:
# ============================================
# 1️. **Added Error Handling** – Wrapped database queries and bulk writes in `try-except` blocks to prevent crashes.  
# 2️.**Handled Invalid Data** – Skipped loans that are missing `RiskScore` or not dictionaries, logging warnings.  
# 3️.**Dynamic Risk Categorization** – Introduced `bucket_size` for flexible risk grouping instead of hardcoded values.  
# 4️.**Optimized MongoDB Queries** – Fetched only necessary fields (`_id`, `RiskScore`) for better performance.  
# 5️.**Improved Bulk Write Handling** – Caught `BulkWriteError` to ensure smooth database operations.  
# ============================================

