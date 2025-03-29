"""Authentication and security utilities.

This module provides functions for password hashing/verification and JWT token
creation/verification. It handles all security-related operations for the application.
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from app.services.email_service import send_verification_email
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Secret keys and encryption settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Generate a secure hash of the provided password.

    Args:
        password (str): The plain text password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password (str): The plain text password to verify
        hashed_password (str): The stored hashed password

    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create a JWT access token with expiration.

    Args:
        data (dict): The data to encode in the token (typically contains 'sub' with user identity)

    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> str | None:
    """Verify and decode a JWT token.

    Args:
        token (str): The JWT token to verify

    Returns:
        str | None: The email (subject) from the token if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None