import os
import json
import tempfile
import logging
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_environment_variables():
    """Load and validate environment variables."""
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    csv_file = os.getenv("CSV_FILE", "Loan.csv")
    
    if not mongo_uri:
        logging.error("MONGO_URI is not set in the .env file.")
        exit(1)
    
    return mongo_uri, csv_file

def load_csv(file_path):
    """Load a CSV file into a pandas DataFrame."""
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            logging.error("The CSV file is empty.")
            exit(1)
        logging.info(f"Loaded CSV file: {file_path}")
        return df
    except FileNotFoundError:
        logging.error(f"CSV file {file_path} not found.")
        exit(1)

def convert_csv_to_json(df):
    """Convert a DataFrame to JSON and save it to a temporary file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_json:
        temp_json_path = temp_json.name
        df.to_json(temp_json_path, orient="records", lines=True)
        logging.info(f"Converted CSV to JSON: {temp_json_path}")
        return temp_json_path

def connect_to_mongodb(mongo_uri, db_name="loan_database", collection_name="loans"):
    """Connect to MongoDB and return the specified collection."""
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        logging.info("Connected to MongoDB")
        return collection
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        exit(1)

def insert_data_into_mongodb(collection, json_file_path, batch_size=1000):
    """Insert data from a JSON file into a MongoDB collection."""
    try:
        with open(json_file_path, "r") as file:
            data = [json.loads(line) for line in file]
        
        if data:
            collection.insert_many(data)  # Batch insert
            logging.info(f"Inserted {len(data)} records into MongoDB.")
        else:
            logging.warning("No records found in the JSON file.")
    except Exception as e:
        logging.error(f"Error inserting data into MongoDB: {e}")

def cleanup_temp_file(file_path):
    """Delete a temporary file."""
    try:
        os.remove(file_path)
        logging.info(f"Deleted temporary file: {file_path}")
    except Exception as e:
        logging.warning(f"Unable to delete temporary file: {e}")

def main():
    """Main function to execute the script."""
    mongo_uri, csv_file = load_environment_variables()
    df = load_csv(csv_file)
    temp_json_path = convert_csv_to_json(df)
    collection = connect_to_mongodb(mongo_uri)
    insert_data_into_mongodb(collection, temp_json_path)
    cleanup_temp_file(temp_json_path)

if __name__ == "__main__":
    main()
