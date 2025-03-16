# backend/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.user import User
from app.config.database import get_database
from app.services.auth_service import (
    create_access_token,
    verify_password,
    get_password_hash,
    send_verification_email,
    verify_token
)

router = APIRouter()

# Connect to MongoDB using async motor client
db = get_database()
user_collection = db["users"]

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/test-db")
async def test_db():
    """Test if the database connection is working."""
    try:
        count = await user_collection.count_documents({})
        return {"message": f"Database connection successful. Users count: {count}"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/register")
async def register(user: User):
    try:
        user_dict = user.dict(by_alias=True, exclude={"id"})
        user_dict["password"] = get_password_hash(user_dict["password"])
        user_dict["verification_token"] = create_access_token(data={"sub": user_dict["email"]})

        result = user_collection.insert_one(user_dict)  


        if result.inserted_id:
            send_verification_email(user_dict["email"], user_dict["verification_token"])
            return {"message": "User registered successfully. Please check your email to verify your account."}

    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        logging.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_collection.find_one({"email": form_data.username})  # Use await for async find_one

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user["is_verified"]:
        raise HTTPException(status_code=400, detail="Email not verified")

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}
@router.get("/verify-email")
async def verify_email(token: str):
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = user_collection.find_one({"email": email})  #  Correct

    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("is_verified", False):  # Use `.get()` to avoid KeyError
        return {"message": "Email already verified"}

    result = user_collection.update_one({"email": email}, {"$set": {"is_verified": True}})

    
    if result.modified_count == 1:
        return {"message": "Email verified successfully"}
    else:
        return {"message": "Email verification failed. Try again."}
