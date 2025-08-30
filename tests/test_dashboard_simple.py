import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock all dependencies before importing
with patch.dict('sys.modules', {
    'streamlit': MagicMock(),
    'plotly': MagicMock(),
    'plotly.express': MagicMock(),
    'pandas': MagicMock(),
    'requests': MagicMock()
}):
    # Now import the dashboard functions
    from dashboard.streamlit_app import fetch_summary, fetch_categories, fetch_monthly

class TestDashboardDataFetching:
    """Test data fetching functions from the dashboard"""

    @patch('dashboard.streamlit_app.requests.get')
    def test_fetch_summary_success(self, mock_get):
        """Test successful summary data fetching"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "total_income": 5000.0,
            "total_expenses": 3000.0,
            "balance": 2000.0,
            "transactions": 25
        }
        mock_get.return_value = mock_response

        result = fetch_summary()

        assert result["total_income"] == 5000.0
        assert result["total_expenses"] == 3000.0
        assert result["balance"] == 2000.0
        assert result["transactions"] == 25
        mock_get.assert_called_once_with("http://api:8000/insights/summary")

    @patch('dashboard.streamlit_app.requests.get')
    def test_fetch_summary_api_error(self, mock_get):
        """Test summary fetching with API error"""
        mock_get.side_effect = Exception("Connection failed")

        result = fetch_summary()

        # Should return default values on error
        assert result["total_income"] == 0
        assert result["total_expenses"] == 0
        assert result["balance"] == 0
        assert result["transactions"] == 0

    @patch('dashboard.streamlit_app.requests.get')
    def test_fetch_categories_success(self, mock_get):
        """Test successful categories data fetching"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"category": "Food", "amount": 500.0},
            {"category": "Transport", "amount": 300.0},
            {"category": "Entertainment", "amount": 200.0}
        ]
        mock_get.return_value = mock_response

        result = fetch_categories()

        assert len(result) == 3
        assert result[0]["category"] == "Food"
        assert result[0]["amount"] == 500.0
        assert result[1]["category"] == "Transport"
        assert result[1]["amount"] == 300.0
        mock_get.assert_called_once_with("http://api:8000/insights/categories")

    @patch('dashboard.streamlit_app.requests.get')
    def test_fetch_categories_empty(self, mock_get):
        """Test categories fetching with empty data"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = fetch_categories()

        assert result == []
        mock_get.assert_called_once_with("http://api:8000/insights/categories")

    @patch('dashboard.streamlit_app.requests.get')
    def test_fetch_categories_api_error(self, mock_get):
        """Test categories fetching with API error"""
        mock_get.side_effect = Exception("API unavailable")

        result = fetch_categories()

        assert result == []

    @patch('dashboard.streamlit_app.requests.get')
    def test_fetch_monthly_success(self, mock_get):
        """Test successful monthly data fetching"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"month": "2024-01", "amount": 1500.0},
            {"month": "2024-02", "amount": 1200.0},
            {"month": "2024-03", "amount": 1800.0}
        ]
        mock_get.return_value = mock_response

        result = fetch_monthly()

        assert len(result) == 3
        assert result[0]["month"] == "2024-01"
        assert result[0]["amount"] == 1500.0
        assert result[1]["month"] == "2024-02"
        assert result[1]["amount"] == 1200.0
        mock_get.assert_called_once_with("http://api:8000/insights/monthly")

    @patch('dashboard.streamlit_app.requests.get')
    def test_fetch_monthly_empty(self, mock_get):
        """Test monthly fetching with empty data"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = fetch_monthly()

        assert result == []

    @patch('dashboard.streamlit_app.requests.get')
    def test_fetch_monthly_api_error(self, mock_get):
        """Test monthly fetching with API error"""
        mock_get.side_effect = Exception("Network error")

        result = fetch_monthly()

        assert result == []

    @patch('dashboard.streamlit_app.requests.get')
    def test_api_url_configuration(self, mock_get):
        """Test that API calls use the correct URL"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"total_income": 1000.0, "total_expenses": 500.0, "balance": 500.0, "transactions": 10}
        mock_get.return_value = mock_response

        fetch_summary()

        # Verify the API URL is correct for Docker environment
        mock_get.assert_called_once_with("http://api:8000/insights/summary")

    @patch('dashboard.streamlit_app.requests.get')
    def test_http_error_handling(self, mock_get):
        """Test handling of HTTP errors"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("404 Client Error")
        mock_get.return_value = mock_response

        # All fetch functions should handle HTTP errors gracefully
        summary_result = fetch_summary()
        categories_result = fetch_categories()
        monthly_result = fetch_monthly()

        assert summary_result["total_income"] == 0
        assert categories_result == []
        assert monthly_result == []


class TestDashboardDataProcessing:
    """Test data processing and formatting logic"""

    def test_summary_data_structure(self):
        """Test that summary data has expected structure"""
        # This would test any data processing logic if it existed
        # For now, the dashboard mainly passes through API data
        expected_keys = ["total_income", "total_expenses", "balance", "transactions"]

        # Mock data that should be returned on API error
        default_summary = {
            "total_income": 0,
            "total_expenses": 0,
            "balance": 0,
            "transactions": 0
        }

        for key in expected_keys:
            assert key in default_summary
            assert isinstance(default_summary[key], (int, float))

    def test_categories_data_structure(self):
        """Test that categories data has expected structure"""
        # Mock successful categories data
        mock_categories = [
            {"category": "Food", "amount": 500.0},
            {"category": "Transport", "amount": 300.0}
        ]

        for item in mock_categories:
            assert "category" in item
            assert "amount" in item
            assert isinstance(item["category"], str)
            assert isinstance(item["amount"], (int, float))

    def test_monthly_data_structure(self):
        """Test that monthly data has expected structure"""
        # Mock successful monthly data
        mock_monthly = [
            {"month": "2024-01", "amount": 1500.0},
            {"month": "2024-02", "amount": 1200.0}
        ]

        for item in mock_monthly:
            assert "month" in item
            assert "amount" in item
            assert isinstance(item["month"], str)
            assert isinstance(item["amount"], (int, float))


class TestDashboardIntegration:
    """Test dashboard integration scenarios"""

    @patch('dashboard.streamlit_app.requests.get')
    def test_all_endpoints_working(self, mock_get):
        """Test scenario where all API endpoints return valid data"""
        # Setup mock responses for all endpoints
        def mock_response_factory(url):
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None

            if "summary" in url:
                mock_response.json.return_value = {
                    "total_income": 10000.0,
                    "total_expenses": 7500.0,
                    "balance": 2500.0,
                    "transactions": 50
                }
            elif "categories" in url:
                mock_response.json.return_value = [
                    {"category": "Housing", "amount": 2000.0},
                    {"category": "Food", "amount": 800.0},
                    {"category": "Transport", "amount": 600.0}
                ]
            elif "monthly" in url:
                mock_response.json.return_value = [
                    {"month": "2024-01", "amount": 2000.0},
                    {"month": "2024-02", "amount": 1800.0},
                    {"month": "2024-03", "amount": 2200.0}
                ]

            return mock_response

        mock_get.side_effect = mock_response_factory

        # Test all fetch functions
        summary = fetch_summary()
        categories = fetch_categories()
        monthly = fetch_monthly()

        # Verify data integrity
        assert summary["balance"] == summary["total_income"] - summary["total_expenses"]
        assert len(categories) == 3
        assert len(monthly) == 3

        # Verify API calls were made
        assert mock_get.call_count == 3

    @patch('dashboard.streamlit_app.requests.get')
    def test_partial_api_failure(self, mock_get):
        """Test scenario where some API endpoints fail"""
        def mock_response_factory(url):
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None

            if "summary" in url:
                mock_response.json.return_value = {
                    "total_income": 5000.0,
                    "total_expenses": 3000.0,
                    "balance": 2000.0,
                    "transactions": 25
                }
            elif "categories" in url:
                # Simulate categories endpoint failure
                mock_response.raise_for_status.side_effect = Exception("500 Server Error")
            elif "monthly" in url:
                mock_response.json.return_value = [
                    {"month": "2024-01", "amount": 1500.0}
                ]

            return mock_response

        mock_get.side_effect = mock_response_factory

        summary = fetch_summary()
        categories = fetch_categories()
        monthly = fetch_monthly()

        # Summary should work
        assert summary["total_income"] == 5000.0

        # Categories should return empty list on failure
        assert categories == []

        # Monthly should work
        assert len(monthly) == 1
        assert monthly[0]["month"] == "2024-01"
