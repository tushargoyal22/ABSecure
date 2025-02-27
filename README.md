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
│── ABSecure_Backend/
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
│   │   │── requirements.txt  # Dependencies
│   │   │── .env  # Environment variables (MongoDB URI)
│   │   │── .gitignore  # Ignore unnecessary files
│   │   │── README.md  # Project documentation
│   │
│   │── frontend/  # Frontend UI components
│   │── database/  # Database configuration
│   │── docs/  # Documentation and guides
│   │── .gitignore
│   │── docker-compose.yml
│   │── LICENSE
│   │── README.md

```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud instance)
- Git

### Backend Setup
```
---

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
pip install -r requirements.txt
```

#### **4️⃣ Install FastAPI and Uvicorn**
If not already included in `requirements.txt`, install them manually:
```bash
pip install fastapi uvicorn
```

#### **5️⃣ Set Up Environment Variables**
Create a `.env` file in the `ABSecure_backend/app/config` directory and add:
```
MONGO_URI="your_mongodb_connection_string"
```

#### **6️⃣ Run the FastAPI Backend**
```bash
uvicorn main:app --reload
```
- This starts the FastAPI server on `http://127.0.0.1:8000`
- You can access API docs at `http://127.0.0.1:8000/docs`

---

```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
Ensure MongoDB is running and update the connection string in `backend/app/main.py`.

### Running the Project
- Start the **backend**: `uvicorn app.main:app --reload`
- Start the **frontend**: `npm run dev`








