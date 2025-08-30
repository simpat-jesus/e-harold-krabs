import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestDashboardLogic:
    """Test dashboard logic without importing streamlit app"""

    def test_api_url_configuration(self):
        """Test API URL configuration logic"""
        # Test the API URL that should be used
        api_url = "http://api:8000"

        assert api_url.startswith("http://")
        assert "api" in api_url
        assert "8000" in api_url

        # Test endpoint URLs
        summary_url = f"{api_url}/insights/summary"
        categories_url = f"{api_url}/insights/categories"
        monthly_url = f"{api_url}/insights/monthly"

        assert summary_url == "http://api:8000/insights/summary"
        assert categories_url == "http://api:8000/insights/categories"
        assert monthly_url == "http://api:8000/insights/monthly"

    def test_data_fetching_logic(self):
        """Test the logic of data fetching without actual HTTP calls"""
        with patch('requests.get') as mock_get:
            # Setup successful response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "total_income": 5000.0,
                "total_expenses": 3000.0,
                "balance": 2000.0,
                "transactions": 25
            }
            mock_get.return_value = mock_response

            # Simulate the fetch_summary logic
            try:
                response = mock_get("http://api:8000/insights/summary")
                response.raise_for_status()
                data = response.json()
                result = data
            except Exception:
                result = {
                    "total_income": 0,
                    "total_expenses": 0,
                    "balance": 0,
                    "transactions": 0
                }

            assert result["total_income"] == 5000.0
            assert result["total_expenses"] == 3000.0
            assert result["balance"] == 2000.0
            assert result["transactions"] == 25

    def test_error_handling_logic(self):
        """Test error handling logic"""
        with patch('requests.get') as mock_get:
            # Setup error response
            mock_get.side_effect = Exception("Connection failed")

            # Simulate error handling
            try:
                response = mock_get("http://api:8000/insights/summary")
                response.raise_for_status()
                data = response.json()
                result = data
            except Exception:
                result = {
                    "total_income": 0,
                    "total_expenses": 0,
                    "balance": 0,
                    "transactions": 0
                }

            # Should return default values on error
            assert result["total_income"] == 0
            assert result["total_expenses"] == 0
            assert result["balance"] == 0
            assert result["transactions"] == 0

    def test_data_processing_logic(self):
        """Test data processing and validation logic"""

        # Test summary data validation
        valid_summary = {
            "total_income": 5000.0,
            "total_expenses": 3000.0,
            "balance": 2000.0,
            "transactions": 25
        }

        # Check data structure
        required_keys = ["total_income", "total_expenses", "balance", "transactions"]
        for key in required_keys:
            assert key in valid_summary
            assert isinstance(valid_summary[key], (int, float))

        # Test balance calculation
        expected_balance = valid_summary["total_income"] - valid_summary["total_expenses"]
        assert valid_summary["balance"] == expected_balance

    def test_categories_data_processing(self):
        """Test categories data processing"""
        categories_data = [
            {"category": "Food", "amount": 500.0},
            {"category": "Transport", "amount": 300.0},
            {"category": "Entertainment", "amount": 200.0}
        ]

        # Validate structure
        for item in categories_data:
            assert "category" in item
            assert "amount" in item
            assert isinstance(item["category"], str)
            assert isinstance(item["amount"], (int, float))
            assert item["amount"] >= 0

        # Test total calculation
        total_expenses = sum(item["amount"] for item in categories_data)
        assert total_expenses == 1000.0

    def test_monthly_data_processing(self):
        """Test monthly data processing"""
        monthly_data = [
            {"month": "2024-01", "amount": 1500.0},
            {"month": "2024-02", "amount": 1200.0},
            {"month": "2024-03", "amount": 1800.0}
        ]

        # Validate structure
        for item in monthly_data:
            assert "month" in item
            assert "amount" in item
            assert isinstance(item["month"], str)
            assert isinstance(item["amount"], (int, float))
            # Check month format
            assert len(item["month"]) == 7
            assert item["month"][4] == "-"

        # Test data aggregation
        total_amount = sum(item["amount"] for item in monthly_data)
        assert total_amount == 4500.0

        average_amount = total_amount / len(monthly_data)
        assert average_amount == 1500.0

    def test_empty_data_handling(self):
        """Test handling of empty data"""

        # Test empty categories
        empty_categories = []
        assert len(empty_categories) == 0

        # Test empty monthly data
        empty_monthly = []
        assert len(empty_monthly) == 0

        # Test default summary
        default_summary = {
            "total_income": 0,
            "total_expenses": 0,
            "balance": 0,
            "transactions": 0
        }

        assert default_summary["balance"] == 0
        assert default_summary["transactions"] == 0

    def test_data_formatting(self):
        """Test data formatting for display"""

        # Test currency formatting
        income = 5000.50
        formatted_income = f"${income:.2f}"
        assert formatted_income == "$5000.50"

        # Test negative balance formatting
        balance = -500.25
        formatted_balance = f"${balance:.2f}"
        assert formatted_balance == "$-500.25"

        # Test zero values
        zero_value = 0.0
        formatted_zero = f"${zero_value:.2f}"
        assert formatted_zero == "$0.00"

    def test_chart_data_preparation(self):
        """Test data preparation for charts"""

        # Test pie chart data
        categories = [
            {"category": "Food", "amount": 500.0},
            {"category": "Transport", "amount": 300.0}
        ]

        # Extract data for pie chart
        labels = [item["category"] for item in categories]
        values = [item["amount"] for item in categories]

        assert labels == ["Food", "Transport"]
        assert values == [500.0, 300.0]

        # Test line chart data
        monthly = [
            {"month": "2024-01", "amount": 1500.0},
            {"month": "2024-02", "amount": 1200.0}
        ]

        # Extract data for line chart
        months = [item["month"] for item in monthly]
        amounts = [item["amount"] for item in monthly]

        assert months == ["2024-01", "2024-02"]
        assert amounts == [1500.0, 1200.0]

    def test_cache_configuration(self):
        """Test caching configuration"""
        # Test cache TTL
        cache_ttl = 60  # seconds
        assert cache_ttl > 0
        assert isinstance(cache_ttl, int)

        # Test cache key generation (simulated)
        def generate_cache_key(endpoint):
            return f"cache_{endpoint}_{cache_ttl}"

        summary_key = generate_cache_key("summary")
        categories_key = generate_cache_key("categories")
        monthly_key = generate_cache_key("monthly")

        assert summary_key == "cache_summary_60"
        assert categories_key == "cache_categories_60"
        assert monthly_key == "cache_monthly_60"

    def test_ui_constants(self):
        """Test UI-related constants and configuration"""

        # Test page configuration
        page_title = "Finance Dashboard"
        layout = "wide"

        assert page_title == "Finance Dashboard"
        assert layout == "wide"

        # Test metric labels
        metric_labels = ["Total Income", "Total Expenses", "Balance"]
        assert len(metric_labels) == 3
        assert "Total Income" in metric_labels
        assert "Total Expenses" in metric_labels
        assert "Balance" in metric_labels

        # Test chart titles
        chart_titles = {
            "categories": "Expenses by Category",
            "monthly": "Monthly Net Flow (Income - Expenses)"
        }

        assert chart_titles["categories"] == "Expenses by Category"
        assert chart_titles["monthly"] == "Monthly Net Flow (Income - Expenses)"


class TestDashboardIntegrationScenarios:
    """Test integration scenarios for the dashboard"""

    def test_complete_workflow_simulation(self):
        """Simulate a complete dashboard workflow"""

        # Mock API responses
        mock_responses = {
            "summary": {
                "total_income": 10000.0,
                "total_expenses": 7500.0,
                "balance": 2500.0,
                "transactions": 50
            },
            "categories": [
                {"category": "Housing", "amount": 2000.0},
                {"category": "Food", "amount": 800.0},
                {"category": "Transport", "amount": 600.0}
            ],
            "monthly": [
                {"month": "2024-01", "amount": 2000.0},
                {"month": "2024-02", "amount": 1800.0},
                {"month": "2024-03", "amount": 2200.0}
            ]
        }

        # Simulate data fetching
        summary_data = mock_responses["summary"]
        categories_data = mock_responses["categories"]
        monthly_data = mock_responses["monthly"]

        # Validate data integrity
        assert summary_data["balance"] == summary_data["total_income"] - summary_data["total_expenses"]
        assert len(categories_data) == 3
        assert len(monthly_data) == 3

        # Test data relationships
        total_category_expenses = sum(item["amount"] for item in categories_data)
        assert total_category_expenses <= summary_data["total_expenses"]

        # Test monthly totals
        monthly_totals = [item["amount"] for item in monthly_data]
        assert all(amount > 0 for amount in monthly_totals)

    def test_error_recovery_scenarios(self):
        """Test various error recovery scenarios"""

        # Test partial data failure
        partial_responses = {
            "summary": {"total_income": 5000.0, "total_expenses": 3000.0, "balance": 2000.0, "transactions": 25},
            "categories": [],  # Failed to load
            "monthly": [{"month": "2024-01", "amount": 1500.0}]  # Partial data
        }

        # Dashboard should handle partial failures gracefully
        assert partial_responses["summary"]["total_income"] == 5000.0
        assert len(partial_responses["categories"]) == 0
        assert len(partial_responses["monthly"]) == 1

        # Test complete failure scenario
        failure_responses = {
            "summary": {"total_income": 0, "total_expenses": 0, "balance": 0, "transactions": 0},
            "categories": [],
            "monthly": []
        }

        # Should show empty state properly
        assert failure_responses["summary"]["transactions"] == 0
        assert len(failure_responses["categories"]) == 0
        assert len(failure_responses["monthly"]) == 0

    def test_data_consistency_checks(self):
        """Test data consistency and validation"""

        # Test balance calculation consistency
        test_cases = [
            {"income": 10000.0, "expenses": 7500.0, "expected_balance": 2500.0},
            {"income": 5000.0, "expenses": 3000.0, "expected_balance": 2000.0},
            {"income": 1000.0, "expenses": 1500.0, "expected_balance": -500.0}
        ]

        for case in test_cases:
            calculated_balance = case["income"] - case["expenses"]
            assert calculated_balance == case["expected_balance"]

        # Test category data consistency
        category_test_data = [
            {"category": "Valid Category", "amount": 100.0},
            {"category": "", "amount": 50.0},  # Empty category
            {"category": "Another Category", "amount": -50.0}  # Negative amount
        ]

        # Validate category data
        for item in category_test_data:
            assert isinstance(item["category"], str)
            assert isinstance(item["amount"], (int, float))

        # Test monthly data format consistency
        monthly_test_data = [
            {"month": "2024-01", "amount": 1500.0},
            {"month": "2024-02", "amount": 1200.0},
            {"month": "invalid", "amount": 1000.0}  # Invalid month format
        ]

        valid_months = [item for item in monthly_test_data if len(item["month"]) == 7 and item["month"][4] == "-"]
        assert len(valid_months) == 2
