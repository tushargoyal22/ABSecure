import os
import logging
import pandas as pd
import kagglehub
from pymongo import MongoClient
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
KAGGLE_DATASET = "lorenzozoppelletto/financial-risk-for-loan-approval"
FILE_NAME = "Loan.csv"

def fetch_data_from_kaggle():
    """
    Fetches dataset from Kaggle and returns a DataFrame.
    """
    try:
        path = kagglehub.dataset_download(KAGGLE_DATASET)
        file_path = os.path.join(path, FILE_NAME)

        if not os.path.exists(file_path):
            logging.error(f"File {FILE_NAME} not found in Kaggle dataset.")
            return None

        df = pd.read_csv(file_path)
        logging.info("Dataset loaded successfully from Kaggle.")
        return df

    except Exception as e:
        logging.error(f"Error fetching dataset from Kaggle: {str(e)}", exc_info=True)
        return None

def insert_data_to_mongo(df):
    """
    Inserts the dataset into MongoDB.
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client["loan_database"]
        collection = db["loan_data"]

        # Convert DataFrame to JSON
        records = json.loads(df.to_json(orient="records"))

        # Insert only new records
        existing_ids = {doc["_id"] for doc in collection.find({}, {"_id": 1})}
        new_records = [record for record in records if record["_id"] not in existing_ids]

        if new_records:
            collection.insert_many(new_records)
            logging.info(f"Inserted {len(new_records)} new records into MongoDB.")
        else:
            logging.info("No new records to insert.")

    except Exception as e:
        logging.error(f"Error inserting data into MongoDB: {str(e)}", exc_info=True)

if __name__ == "__main__":
    df = fetch_data_from_kaggle()
    if df is not None:
        insert_data_to_mongo(df)
