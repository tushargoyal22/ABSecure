"""Authentication API Routes.

This module contains FastAPI routes for user authentication including:
- User registration with email verification
- User login with JWT token generation
- Email verification
- Database connection testing
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
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

# Initialize FastAPI router
router = APIRouter(tags=["Authentication"])

# Database connection setup
db = get_database()
user_collection = db["users"]

# OAuth2 authentication scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/test-db", summary="Test database connection")
def test_db() -> dict:
    """Test database connectivity by counting user documents.
    
    Returns:
        dict: Dictionary containing either:
            - Success message with user count
            - Error message if connection fails
            
    Example:
        >>> GET /test-db
        {"message": "Database connection successful. Users count: 5"}
    """
    try:
        count = user_collection.count_documents({})
        return {"message": f"Database connection successful. Users count: {count}"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register new user")
def register(user: User) -> dict:
    """Register a new user with email verification.
    
    Args:
        user: User object containing registration details
        
    Returns:
        dict: Success message or error details
        
    Raises:
        HTTPException: 
            - 400 if email already registered
            - 500 if registration fails
            
    Flow:
        1. Hashes password
        2. Generates verification token
        3. Stores user in database
        4. Sends verification email
        5. Rolls back on email failure
    """
    try:
        user_dict = user.dict(by_alias=True, exclude={"id"})
        user_dict["password"] = get_password_hash(user_dict["password"])
        user_dict["verification_token"] = create_access_token(data={"sub": user_dict["email"]})

        result = user_collection.insert_one(user_dict)

        if result.inserted_id:
            try:
                send_verification_email(user_dict["email"], user_dict["verification_token"])
                return {"message": "User registered successfully. Please check your email to verify your account."}
            except Exception as e:
                user_collection.delete_one({"_id": result.inserted_id})
                logging.error(f"Failed to send verification email: {str(e)}")
                raise HTTPException(status_code=500, detail="User registration failed due to email error")

    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        logging.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/login", summary="Authenticate user")
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """Authenticate user and return JWT access token.
    
    Args:
        form_data: OAuth2 password request form containing:
            - username (email)
            - password
            
    Returns:
        dict: Dictionary containing:
            - access_token: JWT token
            - user details
            
    Raises:
        HTTPException:
            - 400 for invalid credentials
            - 400 for unverified email
    """
    user = user_collection.find_one({"email": form_data.username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.get("is_verified", False):
        raise HTTPException(status_code=400, detail="Email not verified")

    access_token = create_access_token(data={"sub": user["email"]})
    tranches = [str(t) for t in user.get("tranches", []) if isinstance(t, ObjectId)]
    return {
        "id": str(user["_id"]),
        "access_token": access_token,
        "token_type": "bearer",
        "full_name": user["full_name"],
        "email": user["email"],
        "tranches": tranches
    }

@router.get("/verify-email", summary="Verify email address")
def verify_email(token: str) -> dict:
    """Verify user's email using JWT verification token.
    
    Args:
        token: Verification token sent to user's email
        
    Returns:
        dict: Verification status message
        
    Raises:
        HTTPException:
            - 400 for invalid token
            - 404 if user not found
    """
    email = verify_token(token)
    
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = user_collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("is_verified", False):
        return {"message": "Email already verified"}

    result = user_collection.update_one({"email": email}, {"$set": {"is_verified": True}})

    if result.modified_count == 1:
        return {"message": "Email verified successfully"}
    else:
        return {"message": "Email verification failed. Try again."}