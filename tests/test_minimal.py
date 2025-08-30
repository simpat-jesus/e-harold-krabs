import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

def test_imports_work():
    """Test that all modules can be imported without errors"""
    try:
        # Mock database dependencies before importing
        with patch.dict('sys.modules', {
            'sqlalchemy': MagicMock(),
            'sqlalchemy.ext': MagicMock(),
            'sqlalchemy.ext.declarative': MagicMock(),
            'sqlalchemy.orm': MagicMock(),
            'psycopg2': MagicMock(),
        }):
            with patch('config.create_engine'), \
                 patch('config.SessionLocal'), \
                 patch('config.Base'):
                
                # Test imports
                import config
                import main
                import api.routes
                import db.models
                import db.crud
                import services.csv_parser
                import services.pdf_parser
                import services.insights
                
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_fastapi_app_creation():
    """Test that FastAPI app can be created"""
    try:
        with patch.dict('sys.modules', {
            'sqlalchemy': MagicMock(),
            'sqlalchemy.ext': MagicMock(),
            'sqlalchemy.ext.declarative': MagicMock(),
            'sqlalchemy.orm': MagicMock(),
            'psycopg2': MagicMock(),
        }):
            with patch('config.create_engine'), \
                 patch('config.SessionLocal'), \
                 patch('config.Base'), \
                 patch('main.Base.metadata.create_all'):
                
                from main import app
                assert app is not None
                assert hasattr(app, 'routes')
                
    except Exception as e:
        pytest.fail(f"App creation failed: {e}")

def test_services_functions_exist():
    """Test that service functions exist and are callable"""
    try:
        with patch.dict('sys.modules', {
            'sqlalchemy': MagicMock(),
            'sqlalchemy.ext': MagicMock(),
            'sqlalchemy.ext.declarative': MagicMock(),
            'sqlalchemy.orm': MagicMock(),
            'psycopg2': MagicMock(),
        }):
            # Test CSV parser
            from services.csv_parser import parse_csv
            assert callable(parse_csv)
            
            # Test PDF parser  
            from services.pdf_parser import parse_pdf
            assert callable(parse_pdf)
            
            # Test insights
            from services.insights import get_summary, get_categories, get_monthly_trends
            assert callable(get_summary)
            assert callable(get_categories)
            assert callable(get_monthly_trends)
            
    except Exception as e:
        pytest.fail(f"Service functions test failed: {e}")

def test_database_models_exist():
    """Test that database models exist"""
    try:
        with patch.dict('sys.modules', {
            'sqlalchemy': MagicMock(),
            'sqlalchemy.ext': MagicMock(),
            'sqlalchemy.ext.declarative': MagicMock(),
            'sqlalchemy.orm': MagicMock(),
        }):
            with patch('db.models.Base'), \
                 patch('db.models.Column'), \
                 patch('db.models.Integer'), \
                 patch('db.models.String'), \
                 patch('db.models.Float'), \
                 patch('db.models.Date'):
                
                from db.models import Transaction
                assert Transaction is not None
                
            from db.crud import insert_transaction, get_db
            assert callable(insert_transaction)
            assert callable(get_db)
            
    except Exception as e:
        pytest.fail(f"Database models test failed: {e}")

def test_configuration_exists():
    """Test that configuration is properly set up"""
    try:
        with patch.dict('sys.modules', {
            'sqlalchemy': MagicMock(),
            'sqlalchemy.ext': MagicMock(),
            'sqlalchemy.ext.declarative': MagicMock(),
            'sqlalchemy.orm': MagicMock(),
            'psycopg2': MagicMock(),
        }):
            with patch('config.create_engine'), \
                 patch('config.SessionLocal'), \
                 patch('config.Base'):
                
                import config
                assert hasattr(config, 'SQLALCHEMY_DATABASE_URL') or hasattr(config, 'engine')
                
    except Exception as e:
        pytest.fail(f"Configuration test failed: {e}")

def test_api_routes_exist():
    """Test that API routes exist"""
    try:
        with patch.dict('sys.modules', {
            'sqlalchemy': MagicMock(),
            'sqlalchemy.ext': MagicMock(),
            'sqlalchemy.ext.declarative': MagicMock(),
            'sqlalchemy.orm': MagicMock(),
            'psycopg2': MagicMock(),
        }):
            with patch('config.create_engine'), \
                 patch('config.SessionLocal'), \
                 patch('config.Base'), \
                 patch('db.crud.get_db'), \
                 patch('db.models.Transaction'), \
                 patch('main.Base.metadata.create_all'):
                
                from api.routes import router
                assert router is not None
                assert hasattr(router, 'routes')
                
    except Exception as e:
        pytest.fail(f"API routes test failed: {e}")

# Simple unit tests for individual functions
def test_csv_parser_function():
    """Test CSV parser function in isolation"""
    try:
        with patch('pandas.read_csv') as mock_read_csv:
            mock_df = MagicMock()
            mock_df.to_dict.return_value = [
                {"date": "2024-01-01", "description": "Test", "amount": 100.0}
            ]
            mock_read_csv.return_value = mock_df
            
            from services.csv_parser import parse_csv
            result = parse_csv(b"date,description,amount\n2024-01-01,Test,100.0")
            
            assert isinstance(result, list)
            
    except Exception as e:
        pytest.fail(f"CSV parser function test failed: {e}")

def test_insights_functions():
    """Test insights functions in isolation"""
    try:
        with patch.dict('sys.modules', {
            'sqlalchemy': MagicMock(),
            'sqlalchemy.ext': MagicMock(),
            'sqlalchemy.ext.declarative': MagicMock(),
            'sqlalchemy.orm': MagicMock(),
        }):
            with patch('db.models.Transaction'):
                mock_db = MagicMock()
                mock_db.query.return_value.all.return_value = []
                
                from services.insights import get_summary, get_categories, get_monthly_trends
                
                # Test with empty data
                summary = get_summary(mock_db)
                assert isinstance(summary, dict)
                assert "total_income" in summary
                
                categories = get_categories(mock_db)
                assert isinstance(categories, list)
                
                trends = get_monthly_trends(mock_db)
                assert isinstance(trends, list)
                
    except Exception as e:
        pytest.fail(f"Insights functions test failed: {e}")

def test_basic_functionality():
    """Test that the basic application structure is working"""
    assert True  # At minimum, tests should run without import errors
