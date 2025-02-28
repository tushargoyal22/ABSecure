from fastapi import APIRouter
from app.services.pool_service import group_loans
from app.config.database import get_database  # Import the database connection
import logging
from bson import ObjectId  # Import ObjectId to handle MongoDB IDs

logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Initialize DB
db = get_database()

@router.post("/create-loan-pools/")
async def create_loan_pools():
    logging.info("🔹 Pooling API Triggered!")

    # ✅ Fetch only the first 100 loan entries, including only their IDs
    loans = list(db.loans.find({}, {"_id": 1}))  # Fetch only the loan IDs

    if not loans:
        logging.warning("⚠️ No loan data found!")
        return {"message": "No loans found in database"}

    # ✅ Extract loan IDs as strings
    loan_ids = [str(loan["_id"]) for loan in loans]

    # ✅ Pass loan IDs instead of full objects
    result = group_loans(loan_ids)

    logging.info(f"🔹 Pooling API Response: {result}")
    return result

@router.get("/test")
async def test_pool():
    return {"message": "Pooling Routes Working!"}

logging.info("✅ Pool Routes Loaded!")  # ✅ Debugging
