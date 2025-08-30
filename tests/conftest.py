import pytest
import sys
import os

# Add the app directory to the Python path for testing
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
    from unittest.mock import Mock
    return Mock()
