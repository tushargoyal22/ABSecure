from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
#print("Bcrypt version:", bcrypt.__version__)  # Debugging line
# Secret keys and encryption settings
SECRET_KEY = os.getenv("SECRET_KEY")
#print(os.getenv("SECRET_KEY"))  
#print("SECRET_KEY:", SECRET_KEY)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Function to hash a password
def get_password_hash(password: str):
    return pwd_context.hash(password)


# Function to verify a password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# Function to create a JWT access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to verify a JWT token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


# Function to send a verification email
def send_verification_email(to_email: str, token: str):
    subject = "Verify Your Email"
    verification_link = f"http://localhost:8000/auth/verify-email?token={token}"
    body = f"Click the link below to verify your email:\n\n{verification_link}"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print("Verification email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)
