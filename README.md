# 🦀 e-harold-krabs

> "Your crabby AI accountant — turning PDFs into insights."

e-harold-krabs is an AI-powered personal finance assistant.
It parses your bank statements (PDF/CSV), extracts transactions, stores them in PostgreSQL (JSONB), and generates dashboards & insights powered by AI.

---

## 🚀 Features

- 📄 **Bank Statement Parsing**
  - Upload PDFs or CSV files
  - Extract structured transactions (date, description, amount, category)
- 🗄️ **Smart Storage**
  - PostgreSQL with JSONB for flexible transaction storage
  - Ready for analytics and AI queries
- 🤖 **AI-Powered Categorization**
  - Uses LLMs (Ollama, OpenAI, etc.) to auto-tag expenses
  - Detects recurring payments, anomalies, and lifestyle patterns
- 📊 **Dashboards & Insights**
  - Monthly spending trends
  - Top categories & merchants
  - Predictions for next month
  - Fun insights like:
    - "You spent $1,200 on delivery this year — that's a new laptop 🖥️."

---

## 📂 Project Structure

```bash
e-harold-krabs/
│
├── app/                     # Core application
│   ├── main.py               # Entry point (FastAPI)
│   ├── config.py             # Settings (DB connection, API keys)
│   ├── services/             # Business logic
│   │   ├── pdf_parser.py     # Extract text from PDFs
│   │   ├── csv_parser.py     # Load CSV files
│   │   ├── ai_parser.py      # Call Ollama/OpenAI → JSON
│   │   ├── categorizer.py    # Assign categories (AI + rules)
│   │   ├── insights.py       # Totals, trends, forecasts
│   │
│   ├── db/
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── crud.py           # Insert/query helpers
│   │
│   └── api/
│       ├── routes.py         # Endpoints for upload/insights
│
├── dashboard/                # Frontend
│   ├── streamlit_app.py      # Streamlit dashboards
│
├── tests/                    # Unit tests
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md
│   ├── REQUIREMENTS.md
│   ├── STRUCTURE.md
│
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker setup
└── README.md
```

---

---

## 🛠️ Tech Stack

- **Backend:** Python (FastAPI / Flask)
- **Database:** PostgreSQL with JSONB
- **AI Layer:** Ollama (local LLM) / OpenAI (optional)
- **Dashboard:** Streamlit
- **PDF Parsing:** PyPDF / pdfplumber
- **ETL/Automation:** Pandas + SQLAlchemy

---

---

## 📈 Roadmap

- **Phase 1 – Foundations**
  - Upload PDFs & CSVs
  - Extract transactions into JSON
  - Store in PostgreSQL
- **Phase 2 – AI Layer**
  - Categorize expenses automatically
  - Detect recurring payments
  - Provide natural-language insights
- **Phase 3 – Dashboards & Forecasts**
  - Streamlit dashboards (categories, trends, anomalies)
  - Predict next month's spending
  - Lifestyle insights & financial health score

---

---

## 🧑‍💻 Getting Started

### Quick Start (Recommended)
```bash
# Clone the repo
git clone https://github.com/simpat-jesus/e-harold-krabs.git
cd e-harold-krabs

# Run the project (includes virtual env setup and all services)
./run.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Start the API server on http://localhost:8000
- Start the Streamlit dashboard on http://localhost:8501

### Manual Setup
```bash
# Clone the repo
git clone https://github.com/simpat-jesus/e-harold-krabs.git
cd e-harold-krabs

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start API
uvicorn app.main:app --reload

# Start dashboard (in another terminal)
streamlit run dashboard/streamlit_app.py
```

### Docker Setup
```bash
# Ensure Docker is running
docker-compose up --build
```

### Database Setup
The application uses PostgreSQL. For local development:
- Install PostgreSQL and create a database
- Update `.env` with your database URL
- Or use Docker: `docker-compose up -d db`

---

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request.

---

## 💡 Inspiration

The name comes from Mr. Krabs (SpongeBob), because this app is crabby about your money 🦀💰.
