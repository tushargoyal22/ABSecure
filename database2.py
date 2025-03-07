# App/config/database.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
print("MONGO_URI:", MONGO_URI)  # Ensure it's being read correctly

# Function to connect to the loan database
def get_database():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # 5s timeout
        db = client["loan_database"]
        # Test connection
        client.server_info()
        return db
    except ConnectionFailure as e:
        print(f"Error: {str(e)}")
        raise Exception(" MongoDB Connection Failed!")

# Function to connect to the tranche database
def get_tranche_database():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client["tranche_database"]
        # Test connection
        client.server_info()
        return db
    except ConnectionFailure as e:
        print(f"Error: {str(e)}")
        raise Exception(" MongoDB Connection Failed!")

