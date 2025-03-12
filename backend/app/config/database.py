import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")

# Fail fast if MONGO_URI is missing
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set. Please configure it in your .env file.")

# Log in a safe way to avoid exposing sensitive information
logger.debug("MongoDB URI loaded successfully (sanitized).")

#CHANGE 1: Introduced a singleton pattern for MongoDB client  
# This ensures that only one MongoClient instance is used throughout the application  
_client = None  # Global variable to hold the MongoDB client instance

def get_database():
    """
    Returns a **singleton MongoDB client instance**.
    - Prevents creating a new connection on every function call.
    - Ensures efficient resource utilization.
    """
    global _client  # Use the global `_client` variable

    if _client is None:  # Check if the client is already initialized
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # 5s timeout for connection
            logger.info("MongoDB connection established successfully.")
        except ConnectionFailure as e:
            logger.error(f"MongoDB Connection Failed: {str(e)}")
            raise Exception("MongoDB Connection Failed!")

    return _client["loan_database"]  # Return the `loan_database` instance

# Define Collections for Direct Access
db = get_database()
threshold_collection = db["thresholds"]  # Collection for storing threshold values

DEFAULT_THRESHOLDS = {
    "_id": "threshold_values",
    "duration_thresholds": {
        "Short-Term": {"max_duration": 12},
        "Medium-Term": {"min_duration": 13, "max_duration": 60},
        "Long-Term": {"min_duration": 61}
    },
    "custom_risk_thresholds": {
        "Very Low Risk": {
            "min_credit_score": 700,
            "max_monthly_payment": 1500,
            "employment_status": ["Employed", "Self-Employed"]
        },
        "Low Risk": {
            "min_credit_score": 680,
            "max_credit_score": 700,
            "max_monthly_payment": 3000,
            "employment_status": ["Employed", "Self-Employed"]
        },
        "Medium Risk": {
            "min_credit_score": 550,
            "max_credit_score": 680,
            "max_monthly_payment": 6000,
            "employment_status": ["Employed", "Self-Employed", "Part-Time"]
        },
        "High Risk": {
            "max_credit_score": 550,
            "min_monthly_payment": 6000,
            "employment_status": ["Employed", "Self-Employed"]
        }
    },
    "tranche_thresholds": {
        "Senior": 40,
        "Mezzanine": 45,
        "Subordinated": 50
    },
    "creditworthiness_thresholds": {
        "Excellent": {
            "min_credit_score": 800,
            "min_length": 10,
            "min_open_credit_lines": 3,
            "max_open_credit_lines": 7,
            "max_credit_inquiries": 2
        },
        "Good": {
            "min_credit_score": 700,
            "max_credit_score": 800,
            "min_length": 7,
            "min_open_credit_lines": 3,
            "max_open_credit_lines": 12,
            "max_credit_inquiries": 4
        },
        "Fair": {
            "min_credit_score": 600,
            "max_credit_score": 700,
            "min_length": 3,
            "max_credit_inquiries": 5
        },
        "Poor": {
            "max_credit_score": 600,
            "max_length": 3,
            "max_credit_inquiries": 5
        }
    },
    "liquidity_thresholds": {
        "High Liquidity": {"min_liquidity_ratio": 1, "min_relative_ratio": 3},
        "Medium Liquidity": {"min_liquidity_ratio": 0.5, "max_liquidity_ratio": 1, "min_relative_ratio": 2, "max_relative_ratio": 3},
        "Low Liquidity": {"max_liquidity_ratio": 0.5, "max_relative_ratio": 1}
    },
    "debt_analysis_thresholds": {
        "Low Debt": {"max_dti": 30},
        "Moderate Debt": {"min_dti": 30, "max_dti": 50},
        "High Debt": {"min_dti": 50}
    },
    "financial_liabilities_thresholds": {
        "Highly Trustable": {"max_total_dti": 30},
        "Moderate Trustable": {"min_total_dti": 30, "max_total_dti": 50},
        "Not Trustable": {"min_total_dti": 50}
    },
    "age_thresholds": {
        "Young": {"max_age": 30},
        "Mid-Career": {"min_age": 30, "max_age": 50},
        "Senior": {"min_age": 50}
    },
    "financial_status_thresholds": {
        "High Income": {"min_income_per_dependent": 50000, "employment_status": "Employed"},
        "Medium Income": {"min_income_per_dependent": 25000, "max_income_per_dependent": 50000, "employment_status": ["Employed", "Self Employed"]},
        "Low Income": {"max_income_per_dependent": 25000, "employment_status": "Unemployed"}
    }
}

def initialize_default_thresholds():
    """
    Inserts the default thresholds document into the database if it doesn't exist.
    """
    if threshold_collection.find_one({"_id": "threshold_values"}) is None:
        threshold_collection.insert_one(DEFAULT_THRESHOLDS)
        logger.info("Default thresholds inserted into the database.")
    else:
        logger.info("Default thresholds already exist.")
"""
# Changes Implemented after 1st review:
1. **Added validation for `MONGO_URI`** to ensure it is properly set, improving configurability.
2. **Replaced print statements with structured logging** for better debugging and monitoring.
3. **Sanitized logging messages** to prevent exposure of sensitive information.
4. **Removed redundant `client.server_info()` call** to avoid unnecessary network overhead.
"""
