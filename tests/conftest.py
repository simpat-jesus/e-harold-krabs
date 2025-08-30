import pytest
import sys
import os
from unittest.mock import Mock, patch

# Set testing environment variable to prevent database table creation
os.environ["TESTING"] = "true"

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test configuration
@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing"""
    return {
        "date": "2025-01-01",
        "description": "Test Transaction",
        "amount": -50.00,
        "category": "Food",
        "payment_method": "Credit Card"
    }

@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing"""
    return """date,description,amount,category,payment_method
2025-01-01,Salary,3000.00,Income,Bank Transfer
2025-01-02,Groceries,-150.00,Food,Credit Card
2025-01-03,Gas,-50.00,Transportation,Debit Card
2025-01-04,Netflix,-15.99,Entertainment,Credit Card
"""

@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    return Mock()

@pytest.fixture(autouse=True)
def mock_database():
    """Mock database connections and operations for all tests"""
    with patch('app.config.create_engine'), \
         patch('app.config.SessionLocal'), \
         patch('app.config.Base'), \
         patch('app.main.Base.metadata.create_all'), \
         patch('app.db.models.Base'), \
         patch('app.db.models.Column'), \
         patch('app.db.models.Integer'), \
         patch('app.db.models.String'), \
         patch('app.db.models.Float'), \
         patch('app.db.models.Date'), \
         patch('app.db.models.JSON'), \
         patch('app.db.crud.Transaction') as mock_transaction_class:
        # Create a proper mock for the Transaction class
        mock_transaction = Mock()
        mock_transaction.__tablename__ = "transactions"
        mock_transaction_class.return_value = mock_transaction
        yield
