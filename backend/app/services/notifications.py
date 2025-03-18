# services/notifications.py
import requests
import smtplib
from email.mime.text import MIMEText
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

# Load environment variables (or use default values)
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "demo")
SMTP_SENDER = os.getenv("SMTP_SENDER", "your_email@gmail.com")
SMTP_RECEIVER = os.getenv("SMTP_RECEIVER", "receiver_email@example.com")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "your_app_password")
SPIKE_THRESHOLD_PERCENT = float(os.getenv("SPIKE_THRESHOLD_PERCENT", "0.1"))

def fetch_cpi_data():
    """
    Fetches CPI data from Alpha Vantage API.
    Expects the JSON response to have a "data" key containing a list of records.
    """
    url = f"https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey={ALPHAVANTAGE_API_KEY}"
    r = requests.get(url)
    data = r.json()
    if "data" in data:
        return data["data"]
    else:
        print("Error fetching CPI data:", data)
        return []

def detect_cpi_spike(cpi_data, threshold_percent=SPIKE_THRESHOLD_PERCENT):
    """
    Converts CPI data (list of dicts) to a DataFrame, sorts it by date,
    and checks if the percentage change between the latest and previous values exceeds the threshold.
    Returns (spike_detected, latest_value, previous_value, percentage_change).
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

def send_email_notification(subject, body):
    """
    Sends an email notification using SMTP.
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

def process_macro_alert():
    """
    Main function: fetches CPI data, detects a spike, and sends an email alert if a spike is detected.
    Returns a status string.
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
