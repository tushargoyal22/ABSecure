import os
import logging
import sys
import pandas as pd
import numpy as np
import joblib
import kagglehub
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score


MODEL_FILE = "loan_risk_model.pkl"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_data(data_path, file_name):
    try:
        # Download dataset
        path = kagglehub.dataset_download(data_path)
        
        logging.info(f"Path to dataset files: {path}")
        
        # Check if directory exists
        if not os.path.exists(path):
            logging.error(f"Dataset path {path} does not exist.")
            return None
        
        logging.info(f"Files in dataset: {os.listdir(path)}")
        
        # Construct file path
        file_path = os.path.join(path, file_name)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logging.error(f"File {file_name} not found in dataset")
            return None
        
        # Load dataset
        df = pd.read_csv(file_path)
        logging.info("Dataset loaded successfully.")
        return df
    
    except Exception as e:
        logging.error(f"Error loading dataset: {str(e)}", exc_info=True)
        return None

def preprocess_data(df):
    logging.info("preprocessing started")
    logging.info(f"columns are {df.columns}")
    df = df.drop(columns=["ApplicationDate"], errors='ignore')
    df['Liquidity_Ratio'] = (df['SavingsAccountBalance'] + df['CheckingAccountBalance']) / df['LoanAmount']
    df['Relative_Ratio'] = df['MonthlyIncome'] / (df['LoanAmount'] / df['LoanDuration'])
    df["IncomePerDependent"] = df["AnnualIncome"] / (df["NumberOfDependents"] + 1)
    categories = ['EmploymentStatus', 'EducationLevel', 'MaritalStatus', 'NumberOfDependents',
                  'HomeOwnershipStatus', 'LoanPurpose', 'LoanApproved']
    #identified categorical variables based on domain knowledge
    df = df.drop(columns=categories, errors='ignore')
    #removing them as they didn't show significant prominence in determining risk score(analysed using box and violin plots)
    logging.info("preprocessing successful")
    return df

def train_model(df):

    df=preprocess_data(df)
    logging.info("training started")
    X = df.drop(columns=['RiskScore'])
    y = df['RiskScore']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)
    logging.info("training started")
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    logging.info(f"Model Performance - MSE: {mse}, R2: {r2}")

    joblib.dump(model, MODEL_FILE)
    logging.info("Model saved successfully.")
    
    return model

def load_model(model_pkl):
    if os.path.exists(model_pkl):
        return joblib.load(model_pkl)
    else:
        logging.error("Model file not found.")
        return None

def get_risk_score(model_pkl, input_data):

    try:
        logging.info("getting risk scores")
        model = joblib.load(model_pkl)
        if 'RiskScore' in input_data.columns:
            input_data = input_data.drop(columns=["RiskScore"], errors='ignore')
        input_data=preprocess_data(input_data)
        prediction = model.predict(input_data)
        return prediction
    except Exception as e:

        logging.error(f"ERROR OCCURED at get_risk_score: {e}", exc_info=True)
        return None

import logging

def get_updated_dataset(raw_data, predictions):
    try:
        logging.info("Updating dataset with predictions.")
        
        # Check if raw_data and predictions have the same length
        if len(raw_data) != len(predictions):
            logging.error("Length mismatch: raw_data and predictions must have the same number of rows.")
            return None
        
        raw_data['Predicted_RiskScore'] = predictions  # Add a new column for predictions
        logging.info("Dataset updated successfully with predictions.")
        
        return raw_data
    
    except Exception as e:
        logging.error(f"Error updating dataset: {str(e)}", exc_info=True)
        return None

def load_ml_risk_scores(df: pd.DataFrame):
    """
    Preprocesses the input DataFrame and returns the ML predicted risk scores.
    It reuses the preprocess_data and get_risk_score functions.
    """
    logging.info("Starting ML risk score prediction.")
    logging.info(f"columns are:{df.columns}")
    # If the model file doesn't exist, train the model.
    if not os.path.exists(MODEL_FILE):
        logging.info(f"Model file {MODEL_FILE} not found, training model...")
        sample_input = load_data("lorenzozoppelletto/financial-risk-for-loan-approval",'Loan.csv')
        if sample_input is not None:
            train_model(sample_input)
        else:
            logging.error("Failed to load dataset to train the model.")
            return None

    # Preprocess a copy of the DataFrame.
    df_processed = df.copy()

    # Remove the 'RiskScore' column so that only the input features remain.
    if 'RiskScore' in df_processed.columns:
        df_processed = df_processed.drop(columns=['RiskScore'])
        logging.info("Dropped 'RiskScore' column from processed data.")

    # Explicitly drop any column named '_id' to match the training features.
    df_processed = df_processed.loc[:, ~df_processed.columns.str.match(r'^_id$')]
    if '_id' in df.columns:
        logging.info("Dropped '_id' column from processed data.")

    predictions = get_risk_score(MODEL_FILE, df_processed)

    if predictions is not None:
        logging.info("Successfully obtained risk score predictions.")
    else:
        logging.error("Risk score predictions returned None")

    return predictions