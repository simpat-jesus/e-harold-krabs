import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock all database-related modules before importing anything from app
mock_engine = MagicMock()
mock_session_local = MagicMock()
mock_base = MagicMock()

with patch.dict('sys.modules', {
    'sqlalchemy': MagicMock(),
    'sqlalchemy.ext': MagicMock(),
    'sqlalchemy.ext.declarative': MagicMock(),
    'sqlalchemy.orm': MagicMock(),
    'psycopg2': MagicMock(),
}):
    with patch('app.config.create_engine', return_value=mock_engine), \
         patch('app.config.SessionLocal', return_value=mock_session_local), \
         patch('app.config.Base', mock_base), \
         patch('app.db.models.Base', mock_base), \
         patch('app.db.models.Column'), \
         patch('app.main.Base.metadata.create_all'):
        from app.db.models import Transaction
        from app.db.crud import insert_transaction

def test_transaction_model_creation():
    """Test Transaction model can be created with proper attributes"""
    # This is more of a smoke test since we're using SQLAlchemy
    # In a real scenario, you'd test with an actual database

    # Mock the SQLAlchemy base and column setup
    with patch('db.models.Base') as mock_base:
        with patch('db.models.Column') as mock_column:
            # The model should have the expected attributes
            assert hasattr(Transaction, '__tablename__')
            assert Transaction.__tablename__ == "transactions"

def test_insert_transaction():
    """Test insert_transaction function"""
    mock_db = Mock()
    mock_transaction = Mock()

    # Mock the database session and transaction creation
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()

    # Mock Transaction class
    with patch('db.crud.Transaction') as mock_transaction_class:
        mock_transaction_class.return_value = mock_transaction

        test_tx_data = {
            "date": "2025-01-01",
            "description": "Test Transaction",
            "amount": -50.00,
            "category": "Food",
            "payment_method": "Credit Card"
        }

        result = insert_transaction(mock_db, test_tx_data)

        # Verify Transaction was created with correct data
        mock_transaction_class.assert_called_once()
        call_args = mock_transaction_class.call_args[1]

        assert call_args["date"] == datetime(2025, 1, 1).date()
        assert call_args["description"] == "Test Transaction"
        assert call_args["amount"] == -50.00
        assert call_args["category"] == "Food"
        assert call_args["payment_method"] == "Credit Card"
        assert call_args["raw_data"] == test_tx_data

        # Verify database operations were called
        mock_db.add.assert_called_once_with(mock_transaction)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_transaction)

        assert result == mock_transaction

def test_insert_transaction_missing_optional_fields():
    """Test insert_transaction with missing optional fields"""
    mock_db = Mock()
    mock_transaction = Mock()

    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()

    with patch('db.crud.Transaction') as mock_transaction_class:
        mock_transaction_class.return_value = mock_transaction

        test_tx_data = {
            "date": "2025-01-01",
            "description": "Test Transaction",
            "amount": 100.00
            # category and payment_method are optional
        }

        result = insert_transaction(mock_db, test_tx_data)

        # Verify optional fields default to None
        call_args = mock_transaction_class.call_args[1]
        assert call_args["category"] is None
        assert call_args["payment_method"] is None

def test_get_db_dependency():
    """Test get_db dependency function structure"""
    from app.db.crud import get_db

    # get_db is a generator function that yields a database session
    # In FastAPI, this would be used as a dependency
    assert callable(get_db)

    # Test that it's a generator function
    gen = get_db()
    assert hasattr(gen, '__iter__')
    assert hasattr(gen, '__next__')
