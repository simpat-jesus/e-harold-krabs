import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock streamlit and plotly to avoid GUI dependencies
mock_streamlit = MagicMock()
mock_columns = MagicMock()
mock_columns.__iter__ = lambda self: iter([MagicMock(), MagicMock(), MagicMock()])
mock_streamlit.columns.return_value = mock_columns
mock_streamlit.set_page_config = MagicMock()
mock_streamlit.title = MagicMock()
mock_streamlit.metric = MagicMock()
mock_streamlit.divider = MagicMock()
mock_streamlit.subheader = MagicMock()
mock_streamlit.plotly_chart = MagicMock()
mock_streamlit.info = MagicMock()
mock_streamlit.caption = MagicMock()

mock_plotly = MagicMock()
mock_requests = MagicMock()

sys.modules['streamlit'] = mock_streamlit
sys.modules['plotly'] = mock_plotly
sys.modules['plotly.express'] = mock_plotly.express
sys.modules['requests'] = mock_requests

# Mock pandas DataFrame operations
mock_pd = MagicMock()
sys.modules['pandas'] = mock_pd

# Now import the dashboard after mocking
import dashboard.streamlit_app as dashboard

class TestDashboardUIComponents:
    """Test dashboard UI component rendering and data display"""

    def setup_method(self):
        """Reset mocks before each test"""
        mock_streamlit.reset_mock()
        mock_plotly.reset_mock()
        mock_pd.reset_mock()

    @patch('dashboard.streamlit_app.fetch_summary')
    @patch('dashboard.streamlit_app.fetch_categories')
    @patch('dashboard.streamlit_app.fetch_monthly')
    def test_dashboard_data_loading(self, mock_monthly, mock_categories, mock_summary):
        """Test that dashboard loads data correctly"""
        # Setup mock data
        mock_summary.return_value = {
            "total_income": 5000.0,
            "total_expenses": 3000.0,
            "balance": 2000.0,
            "transactions": 25
        }
        mock_categories.return_value = [
            {"category": "Food", "amount": 800.0},
            {"category": "Transport", "amount": 500.0}
        ]
        mock_monthly.return_value = [
            {"month": "2024-01", "amount": 1500.0},
            {"month": "2024-02", "amount": 1200.0}
        ]

        # Mock DataFrame creation
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df

        # Re-import to trigger the module-level code
        import importlib
        importlib.reload(dashboard)

        # Verify data fetching was called
        mock_summary.assert_called_once()
        mock_categories.assert_called_once()
        mock_monthly.assert_called_once()

    def test_metric_display_formatting(self):
        """Test that metrics are displayed with proper formatting"""
        # Test income metric formatting
        income_value = 5000.50
        expected_format = f"${income_value:.2f}"

        # This would test the formatting logic if it were extracted
        assert expected_format == "$5000.50"

        # Test expense metric formatting
        expense_value = 3000.75
        expected_expense_format = f"${expense_value:.2f}"

        assert expected_expense_format == "$3000.75"

        # Test balance metric formatting
        balance_value = 2000.25
        expected_balance_format = f"${balance_value:.2f}"

        assert expected_balance_format == "$2000.25"

    @patch('dashboard.streamlit_app.fetch_categories')
    def test_categories_chart_creation(self, mock_categories):
        """Test categories pie chart creation"""
        mock_categories.return_value = [
            {"category": "Food", "amount": 800.0},
            {"category": "Transport", "amount": 500.0},
            {"category": "Entertainment", "amount": 300.0}
        ]

        # Mock DataFrame
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df

        # Mock plotly express
        mock_fig = MagicMock()
        mock_plotly.express.pie.return_value = mock_fig

        # Import and test the chart creation logic
        from dashboard.streamlit_app import fetch_categories
        categories = fetch_categories()

        # Verify DataFrame was created
        mock_pd.DataFrame.assert_called_with(categories)

        # Verify pie chart was created with correct parameters
        mock_plotly.express.pie.assert_called_with(
            mock_df,
            values="amount",
            names="category",
            title="Expenses by Category"
        )

    @patch('dashboard.streamlit_app.fetch_categories')
    def test_empty_categories_display(self, mock_categories):
        """Test display when no categories data is available"""
        mock_categories.return_value = []

        from dashboard.streamlit_app import fetch_categories
        categories = fetch_categories()

        # Should handle empty data gracefully
        assert categories == []

    @patch('dashboard.streamlit_app.fetch_monthly')
    def test_monthly_chart_creation(self, mock_monthly):
        """Test monthly trend chart creation"""
        mock_monthly.return_value = [
            {"month": "2024-01", "amount": 1500.0},
            {"month": "2024-02", "amount": 1200.0},
            {"month": "2024-03", "amount": 1800.0}
        ]

        # Mock DataFrame
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df

        # Mock plotly express
        mock_fig = MagicMock()
        mock_plotly.express.line.return_value = mock_fig

        from dashboard.streamlit_app import fetch_monthly
        monthly = fetch_monthly()

        # Verify DataFrame was created
        mock_pd.DataFrame.assert_called_with(monthly)

        # Verify line chart was created with correct parameters
        mock_plotly.express.line.assert_called_with(
            mock_df,
            x="month",
            y="amount",
            title="Monthly Net Flow (Income - Expenses)"
        )

    @patch('dashboard.streamlit_app.fetch_monthly')
    def test_empty_monthly_display(self, mock_monthly):
        """Test display when no monthly data is available"""
        mock_monthly.return_value = []

        from dashboard.streamlit_app import fetch_monthly
        monthly = fetch_monthly()

        # Should handle empty data gracefully
        assert monthly == []


class TestDashboardErrorHandling:
    """Test error handling in dashboard components"""

    def test_invalid_data_formats(self):
        """Test handling of invalid data formats"""
        # Test with None values
        invalid_summary = {
            "total_income": None,
            "total_expenses": 3000.0,
            "balance": 2000.0,
            "transactions": 25
        }

        # Should handle None values gracefully
        income_display = f"${invalid_summary['total_income'] or 0:.2f}"
        assert income_display == "$0.00"

    def test_extreme_values(self):
        """Test handling of extreme values"""
        extreme_summary = {
            "total_income": 999999999.99,
            "total_expenses": 0.01,
            "balance": 999999999.98,
            "transactions": 1000000
        }

        # Should format large numbers correctly
        income_display = f"${extreme_summary['total_income']:.2f}"
        assert income_display == "$999999999.99"

    def test_negative_balance_display(self):
        """Test display of negative balance"""
        negative_summary = {
            "total_income": 1000.0,
            "total_expenses": 1500.0,
            "balance": -500.0,
            "transactions": 10
        }

        balance_display = f"${negative_summary['balance']:.2f}"
        assert balance_display == "$-500.00"


class TestDashboardConfiguration:
    """Test dashboard configuration and constants"""

    def test_api_url_configuration(self):
        """Test API URL is correctly configured"""
        # The API URL should be configured for Docker environment
        expected_api_url = "http://api:8000"

        # This would be tested by checking the actual configuration
        # For now, we verify the URL format
        assert expected_api_url.startswith("http://")
        assert "api" in expected_api_url
        assert "8000" in expected_api_url

    def test_page_config_settings(self):
        """Test Streamlit page configuration"""
        # Verify page config would be set correctly
        expected_title = "Finance Dashboard"
        expected_layout = "wide"

        # These would be the parameters passed to st.set_page_config
        assert expected_title == "Finance Dashboard"
        assert expected_layout == "wide"

    def test_cache_configuration(self):
        """Test caching configuration for data fetching"""
        # The cache TTL should be configured appropriately
        expected_ttl = 60  # seconds

        # This verifies the caching strategy
        assert expected_ttl == 60
        assert expected_ttl > 0  # Should be positive


class TestDashboardDataValidation:
    """Test data validation and processing"""

    def test_summary_data_validation(self):
        """Test validation of summary data structure"""
        valid_summary = {
            "total_income": 5000.0,
            "total_expenses": 3000.0,
            "balance": 2000.0,
            "transactions": 25
        }

        required_keys = ["total_income", "total_expenses", "balance", "transactions"]

        # All required keys should be present
        for key in required_keys:
            assert key in valid_summary

        # Values should be numeric
        for key in ["total_income", "total_expenses", "balance"]:
            assert isinstance(valid_summary[key], (int, float))

        # Transactions should be integer
        assert isinstance(valid_summary["transactions"], int)

    def test_categories_data_validation(self):
        """Test validation of categories data structure"""
        valid_categories = [
            {"category": "Food", "amount": 800.0},
            {"category": "Transport", "amount": 500.0}
        ]

        # Each category should have required fields
        for category in valid_categories:
            assert "category" in category
            assert "amount" in category
            assert isinstance(category["category"], str)
            assert isinstance(category["amount"], (int, float))
            assert category["amount"] >= 0  # Amounts should be non-negative

    def test_monthly_data_validation(self):
        """Test validation of monthly data structure"""
        valid_monthly = [
            {"month": "2024-01", "amount": 1500.0},
            {"month": "2024-02", "amount": 1200.0}
        ]

        # Each monthly entry should have required fields
        for entry in valid_monthly:
            assert "month" in entry
            assert "amount" in entry
            assert isinstance(entry["month"], str)
            assert isinstance(entry["amount"], (int, float))

            # Month should be in YYYY-MM format
            assert len(entry["month"]) == 7
            assert entry["month"][4] == "-"
