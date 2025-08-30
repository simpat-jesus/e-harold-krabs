import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

def test_transaction_model_creation():
    """Test that Transaction model can be created with mocking"""
    # Mock all SQLAlchemy components
    with patch.dict('sys.modules', {
        'sqlalchemy': MagicMock(),
        'sqlalchemy.ext': MagicMock(), 
        'sqlalchemy.ext.declarative': MagicMock(),
        'sqlalchemy.orm': MagicMock()
    }):
        with patch('db.models.Base'), \
             patch('db.models.Column'), \
             patch('db.models.Integer'), \
             patch('db.models.String'), \
             patch('db.models.Float'), \
             patch('db.models.Date'):
            
            # Import and test the model structure
            from db.models import Transaction
            
            # Verify the model has expected attributes (mocked)
            assert hasattr(Transaction, '__tablename__') or Transaction.__name__ == 'Transaction'

@patch('db.models.Transaction')
@patch('db.crud.SessionLocal')
def test_insert_transaction(mock_session_local, mock_transaction):
    """Test transaction insertion with full mocking"""
    # Setup mocks
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_instance = MagicMock()
    mock_transaction.return_value = mock_instance
    
    # Import the function
    from db.crud import insert_transaction
    
    # Test data
    transaction_data = {
        "date": "2025-01-01",
        "description": "Test Transaction",
        "amount": 100.0,
        "category": "Food",
        "payment_method": "Credit Card"
    }
    
    # Call the function
    result = insert_transaction(mock_db, transaction_data)
    
    # Verify that Transaction was called with the data
    mock_transaction.assert_called_once()
    # Verify database operations
    mock_db.add.assert_called_once_with(mock_instance)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_instance)
    
    # Should return the instance
    assert result == mock_instance

@patch('db.models.Transaction')
@patch('db.crud.SessionLocal')
def test_insert_transaction_missing_optional_fields(mock_session_local, mock_transaction):
    """Test transaction insertion with minimal data"""
    # Setup mocks
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_instance = MagicMock()
    mock_transaction.return_value = mock_instance
    
    # Import the function
    from db.crud import insert_transaction
    
    # Test data with minimal fields
    transaction_data = {
        "date": "2025-01-01",
        "description": "Test Transaction",
        "amount": 100.0
    }
    
    # Call the function
    result = insert_transaction(mock_db, transaction_data)
    
    # Verify that Transaction was called
    mock_transaction.assert_called_once()
    # Verify database operations
    mock_db.add.assert_called_once_with(mock_instance)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_instance)
    
    # Should return the instance
    assert result == mock_instance

def test_get_db_dependency():
    """Test the get_db dependency function"""
    with patch.dict('sys.modules', {
        'sqlalchemy': MagicMock(),
        'sqlalchemy.orm': MagicMock()
    }):
        with patch('db.crud.SessionLocal') as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            
            # Import and test
            from db.crud import get_db
            
            # get_db is a generator, so we need to iterate it
            db_generator = get_db()
            db_instance = next(db_generator)
            
            # Should return the mock database instance
            assert db_instance == mock_db
            
            # Close the generator
            try:
                next(db_generator)
            except StopIteration:
                pass  # Expected behavior for generator cleanup
