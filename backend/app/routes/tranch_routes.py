from fastapi import APIRouter, HTTPException
from pymongo.collection import Collection
from bson import ObjectId
import logging
from typing import List
from app.models.tranche import Tranche
from app.config.database import get_database

router = APIRouter()
tranche_collection: Collection = get_database()["tranches"]

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
                tranche_collection.insert_one(tranche_dict)

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

        return {
            "message": "Tranche purchased successfully",
            "tranche_id": tranche_id,
            "investor_id": investor_id
        }

    except Exception as e:
        logging.error(f"Error purchasing tranche: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to purchase tranche")
