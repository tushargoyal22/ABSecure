import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # Default to Gmail SMTP
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Default to 587 for TLS
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Ensure required environment variables are set
if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not SMTP_SERVER:
    raise ValueError("Missing required email configuration. Check your .env file.")

def send_verification_email(email: str, token: str):
    """Sends a verification email to the given email address with a verification link."""
    subject = "Verify Your Email"
    verification_link = f"http://localhost:8000/auth/verify-email?token={token}"
    body = f"Please verify your email by clicking the following link:\n\n{verification_link}"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        logger.info(f"Verification email sent successfully to {email}.")
    except Exception as e:
        logger.error(f"Error sending email to {email}: {e}")
