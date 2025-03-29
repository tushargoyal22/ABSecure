"""Email service module for sending verification emails.

This module handles the configuration and sending of verification emails
using SMTP. It requires proper SMTP server configuration through environment variables.
"""

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

def send_verification_email(email: str, token: str) -> None:
    """Send an email verification link to the specified email address.

    Constructs and sends a verification email containing a link with the provided
    verification token. The email is sent using the configured SMTP server.

    Args:
        email (str): The recipient's email address
        token (str): The verification token to include in the link

    Returns:
        None: This function doesn't return anything but logs the operation status

    Raises:
        SMTPException: If there's an error during the SMTP communication
        Exception: For any other unexpected errors during email sending

    Note:
        The function logs success or failure information using the module's logger.
    """
    subject = "Verify Your Email"
    verification_link = f"http://localhost:5173/verify?token={token}"
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