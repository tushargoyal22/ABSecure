# ABSecure: Smart ABS Management

## Project Description
ABSecure is a **Smart Asset-Backed Securities (ABS) Management System** that helps financial institutions **bundle loans into ABS**, predict their performance, and facilitate trading. The system utilizes **AI** to assess loan risks, optimize securitization, and enable a **secondary market** for trading ABS.

## Key Features
- **Loan Pool Formation** – Group loans based on risk profiles.
- **Tranche Creation** – Split loan pools into **Senior, Mezzanine, and Equity** tranches.
- **Generative AI-Based Risk Analysis** – AI-generated reports for loan risk assessment.
- **Market-Based Pricing** – Real-time pricing of ABS securities.
- **Portfolio Management** – Optimize investor portfolios using ABS.
- **Secondary Market Trading** – Enable buying & selling of ABS.
- **Audit & Compliance** – Secure tracking of all transactions.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Frontend:** React.js / Vue.js
- **AI:** Generative AI (GPT-based) for risk reporting & scenario analysis
- **Deployment:** AWS / GCP / Render(Future plan)
- **Version Control:** GitHub

## Project Structure
```
ABSecure/
│── backend
│   │── app/
│   │   │── config/
│   │   │   ├── database.py  # MongoDB connection setup
│   │   │
│   │   │── models/
│   │   │   ├── loan.py  # Loan schema using Pydantic
│   │   │   ├── pool.py  # Loan Pool schema
│   │   │
│   │   │── routes/
│   │   │   ├── loan_routes.py  # Loan API endpoints
│   │   │   ├── pool_routes.py  # Loan Pool API endpoints
│   │   │
│   │   │── services/
│   │   │   ├── pool_service.py  # Loan pooling logic
│   │   │
│   │   │── main.py  # FastAPI entry point
│   │── requirements.txt  # Dependencies
│   │── .env  # Environment variables (MongoDB URI)
│   |── .gitignore  # Ignore unnecessary files
│   │   
│   │
│── frontend/
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/  # Core pages and views
│   │   ├── context/ # Global state management using React Context API 
│   │   ├── hooks/ # Custom React hooks
│   │   ├── lib/ # Utility functions and helpers
│   │   ├── App.js  # Root component
│   │   ├── main.jsx  # Entry point for React app
│   ├── public/  # Static assets
│   ├── package.json  # Frontend dependencies
│   ├── vite.config.js  # Vite configuration for fast development
|   |
│   │── database/  # Database configuration
│   │── docs/  # Documentation and guides
│   │── docker-compose.yml
│   │── LICENSE
│   │── README.md
|   |__ .gitignore # Ignore unnecessary files

```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud instance)
- Git

### Backend Setup


### **📌 Setup Instructions for ABSecure Backend**  

#### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/tushargoyal22/ABSecure.git
cd ABSecure
```

#### **2️⃣ Create a Virtual Environment (Recommended)**
```bash
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate  # For Windows
```

#### **3️⃣ Install Dependencies**
```bash
pip install -r backend/requirements.txt
```

#### **4️⃣ Install FastAPI and Uvicorn**
If not already included in `requirements.txt`, install them manually:
```bash
pip install fastapi uvicorn
```

#### **5️⃣ Set Up Environment Variables**
Create a `.env` file in the `backend/config` directory and add:
```bash
MONGO_URI="your_mongodb_connection_string"
```

#### **6️⃣ Run the FastAPI Backend**
```bash
uvicorn backend.main:app --reload
```
- This starts the FastAPI server on `http://127.0.0.1:8000`
- You can access API docs at `http://127.0.0.1:8000/docs`

---

### 📌 Frontend Setup

#### 1️⃣  Navigate to the Frontend Directory
Ensure you're inside the project root folder. Then, navigate to the frontend directory:
```bash
cd frontend
```

#### 2️⃣ Install Dependencies
Run the following command to install all necessary dependencies listed in `package.json`:
```bash
npm install
```

#### 3️⃣ Set Up Environment Variables
Copy the provided `.env.example` file and rename it as .env to configure your environment variables:
```bash
cp .env.example .env
```

#### 4️⃣ Run the Frontend in Development Mode 

```bash
npm run dev
```
- This will launch the Vite development server.
- By default, the app will be available at `http://localhost:5173/` .

### **📌 Database Setup**
Ensure MongoDB is running and update the connection string in `backend/main.py`.

### **📌 Running the Project**
- Start the **backend**:  
  ```bash
  uvicorn backend.main:app --reload
  ```
- Start the **frontend**:  
  ```bash
  npm run dev
  ```

# MongoDB Seeding Script (`seed.py`)

This script imports financial loan data from a CSV file into a MongoDB database.

## Prerequisites
Before running the script, ensure you have:
- **Python 3.x** installed  
- Required dependencies:

  ```bash
  pip install pandas pymongo dnspython
 


## Requirements
- A running **MongoDB Atlas or Local MongoDB instance**  
- A valid **CSV file** containing loan data  

## Usage

### 1️⃣ Update Configuration  
Modify the **file paths** in `seed.py` to match your setup:
- Replace  
  ```python
  csv_file_path = r"C:\DE-Shaw(Project)\Loan.csv"
  ```
  with the actual path of your CSV file.  
- Ensure the JSON file path is correctly set:  
  ```python
  json_file_path = "financial_risk_data.json"
  ```
- Update the **MongoDB connection string** (`MONGO_URI`) with your credentials.

### 2️⃣ Run the Script  
Execute the script using:

```bash
python backend/seed.py
```

### 3️⃣ What the Script Does  
- Loads loan data from the CSV file  
- Converts it into JSON format  
- Inserts **only new** records into MongoDB (avoiding duplicates)  
- Prints a **sample of 5 records** from the database for testing purpose

## Troubleshooting

- **MongoDB connection issues?**  
  - Ensure your **MongoDB Atlas cluster** is active.  
  - Check that your **MONGO_URI** in `seed.py` is correct.  
  - Make sure your IP is whitelisted in MongoDB Atlas.  

- **Duplicate records?**  
  - The script **automatically skips duplicates** based on the `_id` field.  
  - If you want to **force insert all records**, modify the script to remove duplicate checks.  

