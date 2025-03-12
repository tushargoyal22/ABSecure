import os
import pandas as pd
import json
import tempfile
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")  # MongoDB connection string
CSV_FILE = os.getenv("CSV_FILE", "Loan.csv")  # Default CSV file path if not set in .env

# Step 1: Read CSV File
try:
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded CSV file: {CSV_FILE}")
except FileNotFoundError:
    print(f"Error: CSV file {CSV_FILE} not found.")
    exit(1)

# Step 2: Convert CSV Data to JSON and store in a temporary file
with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_json:
    temp_json_path = temp_json.name  # Get temporary file path
    df.to_json(temp_json_path, orient="records", lines=True)
    print(f"Converted CSV to JSON: {temp_json_path}")

# Step 3: Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)  # Establish a connection to MongoDB
    db = client["loan_database"]  # Specify the database name
    collection = db["loans"]  # Specify the collection name
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# Step 4: Insert Data into MongoDB
try:
    with open(temp_json_path, "r") as file:
        data = [json.loads(line) for line in file]  # Read JSON file line by line

    # OPTIONAL: If you want to define a custom `_id`, uncomment the following lines:
    # for entry in data:
    #     entry["_id"] = f"{entry['ApplicationDate']}_{entry['Age']}"

    if data:
        collection.insert_many(data)  # Directly insert the data
        print(f"Inserted {len(data)} records into MongoDB.")
    else:
        print("No records found in the JSON file.")

except Exception as e:
    print(f"Error inserting data into MongoDB: {e}")

# Step 5: Cleanup Temporary JSON File
try:
    os.remove(temp_json_path)  # Delete the temporary file after use
    print(f"Deleted temporary file: {temp_json_path}")
except Exception as e:
    print(f"Warning: Unable to delete temporary file: {e}")
