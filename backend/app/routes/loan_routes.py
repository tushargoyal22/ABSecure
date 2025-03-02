import logging
from fastapi import APIRouter, HTTPException
from app.models.loan import Loan
from app.config.database import get_database
from pymongo.errors import DuplicateKeyError
from bson import ObjectId, errors

logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Connect to MongoDB
db = get_database()
loan_collection = db["loans"]

# 🆕 Helper function to validate and convert ObjectId
def validate_object_id(loan_id: str) -> ObjectId:
    try:
        return ObjectId(loan_id)
    except errors.InvalidId:
        logging.error(f"❌ Invalid loan_id format: {loan_id}")
        raise HTTPException(status_code=400, detail="Invalid loan ID format")

# 🆕 Helper function to convert ObjectId to string
def fix_id(loan: dict) -> dict:
    loan["_id"] = str(loan["_id"])
    return loan

# 🔹 CREATE LOAN
@router.post("/loans/")
async def create_loan(loan: Loan):
    try:
        loan_dict = loan.dict(by_alias=True, exclude={"id"})  # ✅ Fix `_id` handling
        logging.info(f"📌 Received Loan Data: {loan_dict}")

        result = loan_collection.insert_one(loan_dict)
        return {"id": str(result.inserted_id)}

    except DuplicateKeyError:
        logging.warning("⚠️ Loan already exists.")
        raise HTTPException(status_code=400, detail="Loan already exists.")
    except Exception as e:
        logging.error(f"❌ Error creating loan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# 🔹 READ LOAN BY ID
@router.get("/loans/{loan_id}")
async def read_loan(loan_id: str):
    try:
        logging.info(f"📌 Reading loan with ID: {loan_id}")
        object_id = validate_object_id(loan_id)  # ✅ Validate loan_id before conversion

        loan = loan_collection.find_one({"_id": object_id})
        if loan:
            logging.info(f"✅ Loan found: {loan}")
            return fix_id(loan)

        logging.warning(f"⚠️ Loan with ID: {loan_id} not found")
        raise HTTPException(status_code=404, detail="Loan not found")

    except Exception as e:
        logging.error(f"❌ Error reading loan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# 🔹 UPDATE LOAN
@router.put("/loans/{loan_id}")
async def update_loan(loan_id: str, loan: Loan):
    try:
        logging.info(f"📌 Updating loan with ID: {loan_id}")
        object_id = validate_object_id(loan_id)  # ✅ Validate loan_id before conversion
        updated_loan = loan.dict(exclude_unset=True)
        logging.info(f"🔄 Updated loan data: {updated_loan}")

        result = loan_collection.update_one({"_id": object_id}, {"$set": updated_loan})
        if result.modified_count > 0:
            logging.info(f"✅ Loan with ID: {loan_id} updated successfully")
            return {"msg": "Loan updated successfully"}

        logging.warning(f"⚠️ Loan with ID: {loan_id} not found")
        raise HTTPException(status_code=404, detail="Loan not found")

    except Exception as e:
        logging.error(f"❌ Error updating loan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# 🔹 DELETE LOAN
@router.delete("/loans/{loan_id}")
async def delete_loan(loan_id: str):
    try:
        logging.info(f"📌 Deleting loan with ID: {loan_id}")
        object_id = validate_object_id(loan_id)  # ✅ Validate loan_id before conversion

        result = loan_collection.delete_one({"_id": object_id})
        if result.deleted_count > 0:
            logging.info(f"✅ Loan with ID: {loan_id} deleted successfully")
            return {"msg": "Loan deleted successfully"}

        logging.warning(f"⚠️ Loan with ID: {loan_id} not found")
        raise HTTPException(status_code=404, detail="Loan not found")

    except Exception as e:
        logging.error(f"❌ Error deleting loan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ============================================
#Summary of Changes:
# ============================================
# 1️. **Added Loan ID Validation** – Ensures `loan_id` is a valid ObjectId format.
# 2️.**Refactored ObjectId Handling** – Used `validate_object_id()` for consistency.
# 3️.**Improved Logging** – More detailed logs for better debugging.
# 4️.**Better Exception Handling** – Specific error messages for `InvalidId` cases.
# These changes enhance API stability, clarity, and error handling!   
# ============================================
