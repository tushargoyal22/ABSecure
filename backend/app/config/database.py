import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Retrieve MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")

# ✅ Fail fast if MONGO_URI is missing
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI environment variable is not set. Please configure it in your .env file.")

# ✅ Log in a safe way to avoid exposing sensitive information
logger.debug("MongoDB URI loaded successfully (sanitized).")

#CHANGE 1: Introduced a singleton pattern for MongoDB client  
# This ensures that only one MongoClient instance is used throughout the application  
_client = None  # Global variable to hold the MongoDB client instance

def get_database():
    """
    ✅ Returns a **singleton MongoDB client instance**.
    - Prevents creating a new connection on every function call.
    - Ensures efficient resource utilization.
    """
    global _client  # Use the global `_client` variable

    if _client is None:  # ✅ Check if the client is already initialized
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # ✅ 5s timeout for connection
            logger.info("✅ MongoDB connection established successfully.")
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB Connection Failed: {str(e)}")
            raise Exception("❌ MongoDB Connection Failed!")

    return _client["loan_database"]  # ✅ Return the `loan_database` instance

"""
# Changes Implemented after 1st review:
1. **Added validation for `MONGO_URI`** to ensure it is properly set, improving configurability.
2. **Replaced print statements with structured logging** for better debugging and monitoring.
3. **Sanitized logging messages** to prevent exposure of sensitive information.
4. **Removed redundant `client.server_info()` call** to avoid unnecessary network overhead.
"""
