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
- **AI:** Generative AI (GeminiAI-based) for risk reporting & scenario analysis
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
│   │   │── ml/
│   │   │   │── risk_model.py   # ML model
│   │   │   │── loan_risk_model.pkl  # pickle file
|   |   |   |__ analysis.py     # Script for generating analysis
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
## Dataset Details
The ABSecure system leverages the [Financial Risk for Loan Approval](https://www.kaggle.com/datasets/lorenzozoppelletto/financial-risk-for-loan-approval) dataset from Kaggle. This dataset provides a rich set of financial, credit, and demographic details on loan applicants and is crucial for:

- **Assessing Loan Risk:**  
  Predicting a **RiskScore** for each loan using a machine learning (Random Forest) model that integrates multiple financial metrics and is used in tranching of loans.
- **Loan Pooling & Tranche Allocation:**  
  Grouping loans based on dynamic criteria chosen by the user—such as duration, creditworthiness, liquidity, and debt metrics—to create investment tranches.  
  *For example:*  
  - **Pooling by Duration:** If a user selects the pooling option **Duration** with the suboption **Short-Term**, the system filters the dataset to include only loans with a duration of 12 months or less.  
  - **Pooling by Creditworthiness:** If a user opts for pooling by **Creditworthiness** with the suboption **Excellent**, then only loans that satisfy the defined excellent criteria (e.g., meeting specified thresholds for CreditScore, LengthOfCreditHistory, and other relevant metrics) are grouped together.

### Key Attributes
- **Applicant Info:**  
  • ApplicationDate, Age, EmploymentStatus, EducationLevel, Experience, MaritalStatus, NumberOfDependents

- **Financial Data:**  
  • AnnualIncome, MonthlyIncome, SavingsAccountBalance, CheckingAccountBalance, NetWorth

- **Credit & Debt Metrics:**  
  • CreditScore, LengthOfCreditHistory, NumberOfOpenCreditLines, NumberOfCreditInquiries, DebtToIncomeRatio, TotalDebtToIncomeRatio, BankruptcyHistory, PreviousLoanDefaults, PaymentHistory, CreditCardUtilizationRate

- **Loan Details:**  
  • LoanAmount, LoanDuration, LoanPurpose, BaseInterestRate, InterestRate, MonthlyLoanPayment

- **Target Variable(IN ML):**  
  • RiskScore

This dataset underpins our machine learning model, which calculates a RiskScore that informs our dynamic pooling logic and subsequent ABS tranche creation.

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

The `seed.py` script populates the database by importing financial loan data from a JSON file into MongoDB.

## Prerequisites

Before running the script, ensure you have:
- **Python 3.x** installed  
- Required dependencies (install using):
  ```bash
  pip install -r requirements.txt
  ```

## Requirements

- A running **MongoDB Atlas or Local MongoDB instance**  
- A valid **JSON file** containing loan data  

## 1️⃣ Dataset Setup  

The loan dataset is required. You can download the original CSV from Kaggle:  

🔗 **[Financial Risk for Loan Approval Dataset](https://www.kaggle.com/datasets/lorenzozoppelletto/financial-risk-for-loan-approval)**  

If you haven't already, convert the CSV to JSON manually and store it as:  

```
data/financial_risk_data.json
```

## 2️⃣ Configuration  

Set up environment variables in `.env` before running the script:  

```ini
MONGO_URI=your_mongodb_connection_string
JSON_FILE_PATH=data/financial_risk_data.json


## 3️⃣ Running the Script  

Execute the script using:

```bash
python backend/seed.py
```

### What the Script Does  
- Loads loan data from the JSON file  
- Inserts **only new** records into MongoDB (avoiding duplicates)  
- Prints a **sample of 5 records** from the database for testing  

## 4️⃣ Troubleshooting  

- **MongoDB connection issues?**  
  - Ensure your **MongoDB Atlas cluster** is active.  
  - Check that your **MONGO_URI** in `.env` is correct.  
  - Make sure your **IP is whitelisted** in MongoDB Atlas.

```

---