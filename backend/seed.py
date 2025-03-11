# %%
pip install pandas pymongo dnspython

# %%
import pandas as pd

# 🔹 Load CSV File
csv_file_path = r"C:\DE-Shaw(Project)\Loan.csv"  # Update with actual path
df = pd.read_csv(csv_file_path)

# 🔹 Convert DataFrame to JSON (Records Format)
json_file_path = "financial_risk_data.json"
df.to_json(json_file_path, orient="records", lines=True)

print(f"CSV converted to JSON successfully! Saved as {json_file_path}")


# %%
import json
from pymongo import MongoClient
from bson import ObjectId  # Required to handle MongoDB ObjectId

# 🔹 Step 1: Connect to MongoDB Atlas
MONGO_URI = "mongodb+srv://admin:admin@cluster0.irqpl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  
client = MongoClient(MONGO_URI)
db = client["loan_database"]  # Database Name
collection = db["loans"]  # Collection Name

# 🔹 Step 2: Load JSON File
json_file_path = r"C:\DE-Shaw(Project)\financial_risk_data.json"  
with open(json_file_path, "r") as file:
    data = [json.loads(line) for line in file]  # Read each JSON line separately

# 🔹 Step 3: Insert Only New Records (Avoiding Duplicates)
new_entries = []
skipped_entries = 0  # Count invalid records

for entry in data:
    if "_id" in entry and "$oid" in entry["_id"]:  
        mongo_id = ObjectId(entry["_id"]["$oid"])  # Convert to MongoDB ObjectId
        if not collection.find_one({"_id": mongo_id}):  # Check for existing record
            entry["_id"] = mongo_id  # Set _id correctly
            new_entries.append(entry)
        else:
            skipped_entries += 1  # Count duplicates

# 🔹 Step 4: Insert Data
if new_entries:
    collection.insert_many(new_entries)  # Insert only new records
    print(f"Inserted {len(new_entries)} new records into MongoDB Atlas successfully!")
else:
    print(" No new records to insert. All entries already exist.")

if skipped_entries:
    print(f" Skipped {skipped_entries} duplicate records based on '_id'.")



# %%
for record in collection.find().limit(5):  # Show 5 records
    print(record)


