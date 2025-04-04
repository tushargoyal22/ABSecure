"""Macroeconomic Alert System for CPI Monitoring.

This module provides functionality to monitor Consumer Price Index (CPI) data,
detect significant spikes, and send email alerts when thresholds are exceeded.
It integrates with Alpha Vantage API for data and SMTP for notifications.
"""

import requests
import smtplib
from email.mime.text import MIMEText
import pandas as pd
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv
load_dotenv()

# Load environment variables (or use default values)
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "demo")
SMTP_SENDER = os.getenv("SMTP_SENDER", "your_email@gmail.com")
SMTP_RECEIVER = os.getenv("SMTP_RECEIVER", "receiver_email@example.com")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "your_app_password")
SPIKE_THRESHOLD_PERCENT = float(os.getenv("SPIKE_THRESHOLD_PERCENT", "0.1"))

def fetch_cpi_data() -> list:
    """Fetch CPI data from Alpha Vantage API.

    Returns:
        list: List of dictionaries containing CPI data points (date and value)
              Returns empty list on error.
    """
    url = f"https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey={ALPHAVANTAGE_API_KEY}"

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CPI data: {e}")
        return []

def detect_cpi_spike(cpi_data: list, threshold_percent: float = SPIKE_THRESHOLD_PERCENT) -> tuple:
    """Analyze CPI data for significant spikes.

    Args:
        cpi_data: List of CPI data points (dicts with 'date' and 'value')
        threshold_percent: Percentage change threshold to consider a spike

    Returns:
        tuple: (spike_detected: bool, latest_value: float, 
                previous_value: float, percentage_change: float)
    """
    if not cpi_data or len(cpi_data) < 2:
        return False, None, None, None

    df = pd.DataFrame(cpi_data)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = df['value'].astype(float)
    df = df.sort_values(by='date')

    latest_value = df.iloc[-1]['value']
    previous_value = df.iloc[-2]['value']

    if previous_value == 0:
        return False, latest_value, previous_value, 0.0

    percentage_change = ((latest_value - previous_value) / previous_value) * 100
    spike_detected = percentage_change > threshold_percent
    return spike_detected, latest_value, previous_value, percentage_change

def send_email_notification(subject: str, body: str) -> None:
    """Send email notification via SMTP.

    Args:
        subject: Email subject line
        body: Email message content
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_SENDER
    msg["To"] = SMTP_RECEIVER

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_SENDER, SMTP_APP_PASSWORD)
            server.sendmail(SMTP_SENDER, SMTP_RECEIVER, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)

def process_macro_alert() -> str:
    """Orchestrate the complete CPI monitoring workflow.

    Returns:
        str: Status message indicating:
             - "No data" if API call failed
             - "Spike detected and email sent" if alert triggered
             - "No spike detected" otherwise
    """
    cpi_data = fetch_cpi_data()
    if not cpi_data:
        print("No CPI data retrieved. Exiting.")
        return "No data"

    spike, latest, previous, change = detect_cpi_spike(cpi_data)
    if spike:
        subject = "CPI Spike Alert"
        body = (
            f"Alert from ABSecure!! A spike was detected in the Consumer Price Index (CPI).\n\n"
            f"Latest CPI: {latest}\n"
            f"Previous CPI: {previous}\n"
            f"Percentage Change: {change:.2f}%\n\n"
            "This may indicate rising inflation. Please review your investment strategy."
        )
        send_email_notification(subject, body)
        return "Spike detected and email sent."
    else:
        print("No significant CPI spike detected.")
        return "No spike detected."