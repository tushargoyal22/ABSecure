import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Function to connect to MongoDB
def get_database():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # 5s timeout
        db = client["loan_database"]
        # Test connection
        client.server_info()
        return db
    except ConnectionFailure:
        raise Exception("❌ MongoDB Connection Failed!")
