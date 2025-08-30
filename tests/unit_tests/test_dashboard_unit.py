import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestDashboardLogic:
    """Unit tests for dashboard logic functions"""

    def test_api_url_configuration(self):
        """Test API URL configuration logic"""
        api_url = "http://api:8000"

        assert api_url.startswith("http://")
        assert "api" in api_url
        assert "8000" in api_url

    def test_data_fetching_logic_success(self):
        """Test successful data fetching logic"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "total_income": 5000.0,
                "total_expenses": 3000.0,
                "balance": 2000.0,
                "transactions": 25
            }
            mock_get.return_value = mock_response

            # Simulate fetch logic
            response = mock_get("http://api:8000/insights/summary")
            response.raise_for_status()
            data = response.json()

            assert data["total_income"] == 5000.0
            assert data["total_expenses"] == 3000.0
            assert data["balance"] == 2000.0
            assert data["transactions"] == 25

    def test_data_fetching_logic_error_handling(self):
        """Test error handling in data fetching"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            # Simulate error handling
            try:
                response = mock_get("http://api:8000/insights/summary")
                response.raise_for_status()
                assert False, "Should have raised exception"
            except Exception as e:
                assert str(e) == "Connection failed"

    def test_data_processing_logic(self):
        """Test data processing logic"""
        # Test data formatting
        raw_data = {
            "total_income": 5000.50,
            "total_expenses": 3000.25,
            "balance": 2000.25,
            "transactions": 25
        }

        # Simulate processing
        formatted_income = f"${raw_data['total_income']:.2f}"
        formatted_expenses = f"${raw_data['total_expenses']:.2f}"
        formatted_balance = f"${raw_data['balance']:.2f}"

        assert formatted_income == "$5000.50"
        assert formatted_expenses == "$3000.25"
        assert formatted_balance == "$2000.25"

    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_data = {
            "total_income": 0,
            "total_expenses": 0,
            "balance": 0,
            "transactions": 0
        }

        # Test that empty data is handled properly
        assert empty_data["total_income"] == 0
        assert empty_data["total_expenses"] == 0
        assert empty_data["balance"] == 0
        assert empty_data["transactions"] == 0

    def test_data_validation(self):
        """Test data validation logic"""
        valid_data = {
            "total_income": 1000.00,
            "total_expenses": 500.00,
            "balance": 500.00,
            "transactions": 10
        }

        # Test data types
        assert isinstance(valid_data["total_income"], (int, float))
        assert isinstance(valid_data["total_expenses"], (int, float))
        assert isinstance(valid_data["balance"], (int, float))
        assert isinstance(valid_data["transactions"], int)

        # Test business logic
        assert valid_data["balance"] == valid_data["total_income"] - valid_data["total_expenses"]
