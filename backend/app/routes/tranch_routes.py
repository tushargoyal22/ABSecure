from fastapi import APIRouter, HTTPException, Query
from pymongo.collection import Collection
from bson import ObjectId
import logging
from typing import List
from app.models.tranche import Tranche
from app.config.database import get_database

router = APIRouter()
database = get_database()
tranche_collection: Collection = database["tranches"]
user_collection: Collection = database["users"]

@router.post("/checkout")
async def upload_tranches(tranches: List[Tranche]):
    try:
        for tranche in tranches:
            tranche_dict = tranche.dict(by_alias=True)

            if tranche_dict.get("_id"):
                tranche_dict["_id"] = ObjectId(tranche_dict["_id"])
            else:
                tranche_dict.pop("_id", None) 
            
            if tranche_dict.get("investor_id"):
                tranche_dict["investor_id"] = ObjectId(tranche_dict["investor_id"])
            
            tranche_dict["loans"] = [ObjectId(loan) for loan in tranche_dict["loans"]]

            if "_id" in tranche_dict:
                tranche_collection.update_one(
                    {"_id": tranche_dict["_id"]},
                    {"$set": tranche_dict},
                    upsert=True
                )
            else:
                result = tranche_collection.insert_one(tranche_dict)
                inserted_tranche_id = result.inserted_id  # Get the MongoDB generated _id

                # Now update the user's tranche list with this new tranche ID
                if tranche_dict.get("investor_id"):
                    user_collection.update_one(
                        {"_id": ObjectId(tranche_dict["investor_id"])},
                        {"$addToSet": {"tranches": inserted_tranche_id}}  # Add the tranche ID to the user's list
                    )

        return {"message": "Tranches uploaded successfully", "uploaded_count": len(tranches)}

    except Exception as e:
        logging.error(f"Error uploading tranches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available", response_model=List[Tranche])
async def get_available_tranches():
    try:
        tranches = list(tranche_collection.find({"investor_id": None}))

        for tranche in tranches:
            tranche["_id"] = str(tranche["_id"])
            tranche["loans"] = [str(loan) for loan in tranche.get("loans", [])]

        return tranches

    except Exception as e:
        logging.error(f"Error retrieving available tranches: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve available tranches")
    
@router.post("/buy-tranche")
async def buy_tranche(tranche_id: str, investor_id: str):
    try:
        tranche = tranche_collection.find_one({"_id": ObjectId(tranche_id), "investor_id": None})
        
        if not tranche:
            raise HTTPException(status_code=404, detail="Tranche not available for purchase")

        tranche_collection.update_one(
            {"_id": ObjectId(tranche_id)},
            {"$set": {"investor_id": ObjectId(investor_id)}}
        )
        
        user_collection.update_one(
            {"_id": ObjectId(investor_id)},
            {"$addToSet": {"tranches": ObjectId(tranche_id)}}
        )

        return {
            "message": "Tranche purchased successfully",
            "tranche_id": tranche_id,
            "investor_id": investor_id
        }

    except Exception as e:
        logging.error(f"Error purchasing tranche: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to purchase tranche")

@router.get("/tranche")
async def get_tranche_details(tranche_id: str):
    try:
        tranche = tranche_collection.find_one({"_id": ObjectId(tranche_id)})

        if not tranche:
            raise HTTPException(status_code=404, detail="Tranche not found")

        # Convert ObjectId fields to string for JSON response
        tranche["_id"] = str(tranche["_id"])
        tranche["loans"] = [str(loan) for loan in tranche.get("loans", [])]
        if tranche.get("investor_id"):
            tranche["investor_id"] = str(tranche["investor_id"])

        return tranche

    except Exception as e:
        logging.error(f"Error fetching tranche details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch tranche details")

@router.get("/user-tranches")
async def get_user_tranches(user_id: str = Query(..., title="User ID")):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid User ID format")

        user = user_collection.find_one({"_id": ObjectId(user_id)})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        tranches = [str(tranche) for tranche in user.get("tranches", [])]

        return {"tranches": tranches}

    except HTTPException as e:
        raise e  # Pass FastAPI exceptions directly

    except Exception as e:
        logging.error(f"Error fetching user tranches: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user tranches")
