import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import io
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Create a comprehensive mock setup
def setup_comprehensive_mocks():
    """Setup all necessary mocks for the application"""
    mock_engine = MagicMock()
    mock_session_local = MagicMock()
    mock_base = MagicMock()
    
    # Create mock Transaction class with proper attributes
    mock_transaction_class = MagicMock()
    mock_transaction_class.__tablename__ = "transactions"
    mock_transaction_class.__name__ = "Transaction"
    
    return {
        'engine': mock_engine,
        'session_local': mock_session_local,
        'base': mock_base,
        'transaction_class': mock_transaction_class
    }

mocks = setup_comprehensive_mocks()

# Comprehensive patching for all SQLAlchemy and database dependencies
with patch.dict('sys.modules', {
    'sqlalchemy': MagicMock(),
    'sqlalchemy.ext': MagicMock(),
    'sqlalchemy.ext.declarative': MagicMock(),
    'sqlalchemy.orm': MagicMock(),
    'psycopg2': MagicMock(),
}):
    with patch('app.config.create_engine', return_value=mocks['engine']), \
         patch('app.config.SessionLocal', return_value=mocks['session_local']), \
         patch('app.config.Base', mocks['base']), \
         patch('app.main.Base.metadata.create_all'), \
         patch('app.db.models.Base', mocks['base']), \
         patch('app.db.models.Column'), \
         patch('app.db.models.Transaction', mocks['transaction_class']), \
         patch('app.api.routes.get_db') as mock_get_db, \
         patch('app.api.routes.insert_transaction') as mock_insert_transaction:
        
        # Setup database dependency
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_insert_transaction.return_value = {"id": 1}
        
        from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Finance Assistant API" in response.json()["message"]

@patch('app.api.routes.get_summary')
def test_insights_summary_empty(mock_get_summary):
    mock_get_summary.return_value = {
        "total_income": 0,
        "total_expenses": 0,
        "balance": 0,
        "transactions": 0
    }
    response = client.get("/insights/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_income" in data
    assert "total_expenses" in data
    assert "balance" in data
    assert "transactions" in data
    assert data["total_income"] == 0
    assert data["total_expenses"] == 0
    assert data["balance"] == 0
    assert data["transactions"] == 0

@patch('app.api.routes.get_categories')
def test_insights_categories_empty(mock_get_categories):
    mock_get_categories.return_value = []
    response = client.get("/insights/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

@patch('app.api.routes.get_monthly_trends')
def test_insights_monthly_empty(mock_get_monthly):
    mock_get_monthly.return_value = []
    response = client.get("/insights/monthly")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

@patch('app.api.routes.parse_csv')
def test_csv_upload_invalid_file(mock_parse_csv):
    # Test with empty file and proper error mocking
    mock_parse_csv.side_effect = Exception("No columns to parse from file")
    
    response = client.post("/upload-csv", files={"file": ("test.csv", b"", "text/csv")})
    assert response.status_code == 200
    data = response.json()
    # Should handle error gracefully
    assert "error" in data
    assert "Failed to process CSV" in data["error"]

@patch('app.api.routes.parse_pdf')
def test_pdf_upload_invalid_file(mock_parse_pdf):
    # Test with non-PDF file
    mock_parse_pdf.side_effect = Exception("Invalid PDF format")
    
    response = client.post("/upload-pdf", files={"file": ("test.txt", b"not a pdf", "text/plain")})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Failed to process PDF" in data["error"]

def test_export_csv_empty():
    with patch('app.api.routes.Transaction') as mock_transaction:
        mock_db = MagicMock()
        with patch('app.api.routes.get_db', return_value=mock_db):
            mock_db.query.return_value.all.return_value = []
            
            response = client.get("/export/csv")
            # Should return 404 for empty data
            assert response.status_code == 404
