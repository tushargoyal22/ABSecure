"""Loan Management API Routes.

This module contains FastAPI routes for CRUD operations on loan records,
including creation, retrieval, updating, and deletion of loan data.
"""

import logging
from fastapi import APIRouter, HTTPException
from app.models.loan import Loan, LoanInput
from app.config.database import get_database
from pymongo.errors import DuplicateKeyError
from bson import ObjectId, errors

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI router
router = APIRouter(tags=["Loan Management"])

# Database connection setup
db = get_database()
loan_collection = db["loans"]

def validate_object_id(loan_id: str) -> ObjectId:
    """Validate and convert string loan_id to MongoDB ObjectId.
    
    Args:
        loan_id: The loan ID string to validate
        
    Returns:
        ObjectId: Valid MongoDB ObjectId
        
    Raises:
        HTTPException: 400 if ID format is invalid
    """
    try:
        return ObjectId(loan_id)
    except errors.InvalidId:
        logging.error(f"Invalid loan_id format: {loan_id}")
        raise HTTPException(status_code=400, detail="Invalid loan ID format")

def fix_id(loan: dict) -> dict:
    """Convert MongoDB ObjectId to string in loan document.
    
    Args:
        loan: Loan document from MongoDB
        
    Returns:
        dict: Loan document with _id converted to string
    """
    loan["_id"] = str(loan["_id"])
    return loan

@router.post("/loans/", status_code=201, summary="Create a new loan")
async def create_loan(loan: LoanInput) -> dict:
    """Create a new loan record in the database.
    
    Args:
        loan: LoanInput object containing loan details
        
    Returns:
        dict: Dictionary containing the ID of created loan
        
    Raises:
        HTTPException:
            - 400 for duplicate key errors
            - 500 for other server errors
    """
    try:
        loan_dict = loan.dict(by_alias=True, exclude={"id"})  # Fix `_id` handling
        logging.info(f" Received Loan Data: {loan_dict}")

        result = loan_collection.insert_one(loan_dict)
        return {"id": str(result.inserted_id)}

    except DuplicateKeyError as e:
        logging.warning(f"Duplicate key error: {str(e)}")
        duplicate_field = str(e.details.get('keyValue', 'unknown field'))  # Extract duplicate key field
        raise HTTPException(status_code=400, detail=f"Duplicate key error: {duplicate_field} already exists.")
        
    except Exception as e:
        logging.error(f"Error creating loan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/loans/{loan_id}", summary="Get loan by ID")
async def read_loan(loan_id: str) -> dict:
    """Retrieve a single loan by its ID.
    
    Args:
        loan_id: The ID of the loan to retrieve
        
    Returns:
        dict: Complete loan document with _id as string
        
    Raises:
        HTTPException:
            - 400 for invalid ID format
            - 404 if loan not found
            - 500 for other server errors
    """
    try:
        logging.info(f"Reading loan with ID: {loan_id}")
        object_id = validate_object_id(loan_id)  # Validate loan_id before conversion

        loan = loan_collection.find_one({"_id": object_id})
        if loan:
            logging.info(f"Loan found: {loan}")
            return fix_id(loan)

        logging.info(f"Loan with ID: {loan_id} not found")
        raise HTTPException(status_code=404, detail="Loan not found")

    except Exception as e:
        logging.error(f"Error reading loan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/loans/{loan_id}", summary="Update loan details")
async def update_loan(loan_id: str, loan: Loan) -> dict:
    """Update an existing loan record.
    
    Args:
        loan_id: The ID of the loan to update
        loan: Loan object containing updated fields
        
    Returns:
        dict: Success/status message
        
    Raises:
        HTTPException:
            - 400 for invalid ID format
            - 404 if loan not found
            - 500 for other server errors
    """
    try:
        logging.info(f"Updating loan with ID: {loan_id}")

        # Validate loan_id before conversion
        object_id = validate_object_id(loan_id)

        # Check if the loan exists before updating
        existing_loan = loan_collection.find_one({"_id": object_id})
        if not existing_loan:
            logging.warning(f"Loan with ID: {loan_id} not found")
            raise HTTPException(status_code=404, detail="Loan not found")

        # Convert loan data, excluding unset fields
        updated_loan = loan.dict(exclude_unset=True)
        logging.info(f"Updated loan data: {updated_loan}")

        # Perform the update operation
        result = loan_collection.update_one({"_id": object_id}, {"$set": updated_loan})

        if result.modified_count > 0:
            logging.info(f"Loan with ID: {loan_id} updated successfully")
            return {"msg": "Loan updated successfully"}

        # Handle the case where no modifications were made
        logging.info(f"Loan with ID: {loan_id} exists but no changes were detected")
        return {"msg": "No changes made to the loan"}

    except Exception as e:
        logging.error(f"Error updating loan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/loans/{loan_id}", summary="Delete a loan")
async def delete_loan(loan_id: str) -> dict:
    """Permanently delete a loan record.
    
    Args:
        loan_id: The ID of the loan to delete
        
    Returns:
        dict: Success/status message
        
    Raises:
        HTTPException:
            - 400 for invalid ID format
            - 404 if loan not found
            - 500 for other server errors
    """
    try:
        logging.info(f"Deleting loan with ID: {loan_id}")
        object_id = validate_object_id(loan_id)  # Validate loan_id before conversion

        result = loan_collection.delete_one({"_id": object_id})
        if result.deleted_count > 0:
            logging.info(f"Loan with ID: {loan_id} deleted successfully")
            return {"msg": "Loan deleted successfully"}

        logging.warning(f"Loan with ID: {loan_id} not found")
        raise HTTPException(status_code=404, detail="Loan not found")

    except Exception as e:
        logging.error(f"Error deleting loan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")