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
- **Deployment:** AWS / GCP / Render
- **Version Control:** GitHub

## Project Structure
```
ABSecure/
│── backend/  # Backend API and logic
│── frontend/  # Frontend UI components
│── database/  # Database configuration
│── docs/  # Documentation and guides
│── .gitignore
│── docker-compose.yml
│── LICENSE
│── README.md
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud instance)
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
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








