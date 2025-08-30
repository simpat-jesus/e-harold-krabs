# Finance Assistant – Project Structure

## Folder Layout

```bash
finance-assistant/
│
├── app/                     # Core application
│   ├── main.py               # Entry point (FastAPI or Flask)
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
│   └── (or React app)
│
├── tests/                    # Unit tests
│
├── requirements.txt          # Python dependencies
└── README.md
```

## Key Libraries

- **PDF/CSV parsing**: pdfplumber, pandas
- **AI integration**: openai, ollama-py (or requests)
- **DB**: SQLAlchemy, psycopg2
- **Forecasting/Stats**: prophet, statsmodels, scikit-learn
- **Web API**: FastAPI
- **Dashboard**: streamlit (fast) or React + recharts (fancy)
- **Utils**: python-dotenv, loguru
