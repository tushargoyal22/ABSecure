# backend/app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError
import logging
from app.models.user import User
from app.config.database import get_database
from app.services.email_service import send_verification_email
from app.services.auth_service import (
    create_access_token,
    verify_password,
    get_password_hash,
    verify_token
)

router = APIRouter()

# Connect to MongoDB using PyMongo
db = get_database()
user_collection = db["users"]

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/test-db")
def test_db():
    """Test if the database connection is working by counting documents in the users collection."""
    try:
        count = user_collection.count_documents({})
        return {"message": f"Database connection successful. Users count: {count}"}
    except Exception as e:
        return {"error": str(e)}


@router.post("/register")
def register(user: User):
    """
    Registers a new user.

    - Hashes the password.
    - Generates a verification token.
    - Inserts the user into the database.
    - Sends a verification email.
    - If email sending fails, removes the user from the database to prevent orphaned accounts.
    """
    try:
        user_dict = user.dict(by_alias=True, exclude={"id"})
        user_dict["password"] = get_password_hash(user_dict["password"])
        user_dict["verification_token"] = create_access_token(data={"sub": user_dict["email"]})

        # Insert user into the database
        result = user_collection.insert_one(user_dict)

        if result.inserted_id:
            try:
                send_verification_email(user_dict["email"], user_dict["verification_token"])
                return {"message": "User registered successfully. Please check your email to verify your account."}
            except Exception as e:
                # Rollback user registration if email sending fails
                user_collection.delete_one({"_id": result.inserted_id})
                logging.error(f"Failed to send verification email: {str(e)}")
                raise HTTPException(status_code=500, detail="User registration failed due to email error")

    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        logging.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Logs in a user by verifying email and password.
    
    - Checks if the user exists in the database.
    - Verifies the password.
    - Ensures the email is verified before allowing login.
    - Returns an access token if authentication is successful.
    """
    # Fetch user from the database based on the provided email
    user = user_collection.find_one({"email": form_data.username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.get("is_verified", False):  # Use `.get()` to avoid KeyError
        raise HTTPException(status_code=400, detail="Email not verified")

    # Generate an access token upon successful authentication
    access_token = create_access_token(data={"sub": user["email"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "full_name": user["full_name"],
        "email": user["email"],
        "tranches": user.get("tranches", [])
    }


@router.get("/verify-email")
def verify_email(token: str):
    """
    Verifies a user's email using the token sent via email.
    
    - Decodes the token to extract the email.
    - Checks if the user exists in the database.
    - If already verified, returns a success message.
    - Otherwise, updates the database to mark the email as verified.
    """
    email = verify_token(token)
    
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Fetch user from the database
    user = user_collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("is_verified", False):  # Use `.get()` to avoid KeyError
        return {"message": "Email already verified"}

    # Update the user record to mark the email as verified
    result = user_collection.update_one({"email": email}, {"$set": {"is_verified": True}})

    if result.modified_count == 1:
        return {"message": "Email verified successfully"}
    else:
        return {"message": "Email verification failed. Try again."}
