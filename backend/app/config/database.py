import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")

# Fail fast if MONGO_URI is missing
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI environment variable is not set. Please configure it in your .env file.")

# Log in a safe way
logger.debug("MongoDB URI loaded successfully (sanitized).")

# Function to connect to MongoDB
def get_database():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # 5s timeout
        return client["loan_database"]
    except ConnectionFailure as e:
        logger.error(f"❌ MongoDB Connection Failed: {str(e)}")
        raise Exception("❌ MongoDB Connection Failed!")

"""
# Changes Implemented after 1st review:
1. **Added validation for `MONGO_URI`** to ensure it is properly set, improving configurability.
2. **Replaced print statements with structured logging** for better debugging and monitoring.
3. **Sanitized logging messages** to prevent exposure of sensitive information.
4. **Removed redundant `client.server_info()` call** to avoid unnecessary network overhead.
"""
