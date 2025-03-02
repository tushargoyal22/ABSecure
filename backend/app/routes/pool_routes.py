from fastapi import APIRouter, HTTPException
from app.services.pool_service import group_loans
from app.config.database import get_database  # Import the database connection
import logging
from bson import ObjectId  
from pymongo.errors import PyMongoError  # Import error handling for MongoDB

logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Initialize DB
db = get_database()

@router.post("/create-loan-pools/")
async def create_loan_pools():
    logging.info("🔹 Pooling API Triggered!")

    try:
        # ✅ Fetch only the first 100 loan entries, including only their IDs
        loans = list(db.loans.find({}, {"_id": 1}).limit(100))  # Limit to 100 for efficiency

        if not loans:
            logging.warning("⚠️ No loan data found!")
            raise HTTPException(status_code=404, detail="No loans found in database")

        # ✅ Extract loan IDs as strings
        loan_ids = [str(loan["_id"]) for loan in loans]

        # ✅ Pass loan IDs instead of full objects
        result = group_loans(loan_ids)

        logging.info(f"🔹 Pooling API Response: {result}")
        return result

    except PyMongoError as e:
        logging.error(f"❌ Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred. Please try again later.")
    
    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

# ------------------------------------------------------------
#  Changes Implemented:
# 1️. Added database error handling using `PyMongoError` to prevent crashes.
# 2️.Introduced `HTTPException` to return appropriate HTTP status codes:
#    - 404 if no loans are found.
#    - 500 for database errors or unexpected failures.
# 3️.Limited loan retrieval to 100 records for efficiency.
# 4️.Improved logging for debugging and issue tracking.
# ------------------------------------------------------------
