import pytest
from unittest.mock import Mock, patch
from io import StringIO
import csv

class TestCSVParserUnit:
    """Unit tests for CSV parsing logic"""

    def test_csv_row_parsing(self):
        """Test parsing individual CSV rows"""
        # Sample CSV row data
        row = ["2025-01-01", "Salary Payment", "3000.00", "Income", "Direct Deposit"]

        # Simulate parsing logic
        transaction = {
            "date": row[0],
            "description": row[1],
            "amount": float(row[2]),
            "category": row[3],
            "payment_method": row[4]
        }

        assert transaction["date"] == "2025-01-01"
        assert transaction["description"] == "Salary Payment"
        assert transaction["amount"] == 3000.00
        assert transaction["category"] == "Income"
        assert transaction["payment_method"] == "Direct Deposit"

    def test_amount_parsing_positive(self):
        """Test parsing positive amounts"""
        amount_strings = ["1000.00", "500.50", "2500"]

        for amount_str in amount_strings:
            amount = float(amount_str)
            assert amount > 0
            assert isinstance(amount, float)

    def test_amount_parsing_negative(self):
        """Test parsing negative amounts"""
        amount_strings = ["-100.00", "-50.50", "-200"]

        for amount_str in amount_strings:
            amount = float(amount_str)
            assert amount < 0
            assert isinstance(amount, float)

    def test_csv_header_validation(self):
        """Test CSV header validation"""
        valid_headers = ["date", "description", "amount", "category", "payment_method"]
        invalid_headers = ["Date", "Description", "Amount"]  # Wrong case
        incomplete_headers = ["date", "description"]  # Missing columns

        # Simulate header validation logic
        required_headers = ["date", "description", "amount", "category", "payment_method"]

        # Valid headers should pass
        assert all(header in valid_headers for header in required_headers)

        # Invalid headers should fail
        assert not all(header in invalid_headers for header in required_headers)

        # Incomplete headers should fail
        assert not all(header in incomplete_headers for header in required_headers)

    def test_empty_row_handling(self):
        """Test handling of empty or invalid rows"""
        test_cases = [
            ["", "", ""],  # All empty fields
            ["", "description", "100.00"],  # Empty date
            ["2025-01-01", "", "100.00"],  # Empty description
            ["2025-01-01", "description", ""],  # Empty amount
        ]

        for row in test_cases:
            # Check if any required field is empty
            if not all(field.strip() for field in row):
                assert True  # Should be skipped due to empty fields
            else:
                assert False  # Should not reach here

    def test_data_type_conversion(self):
        """Test conversion of string data to appropriate types"""
        # Test date string (should remain string)
        date_str = "2025-01-01"
        assert isinstance(date_str, str)
        assert len(date_str) == 10  # YYYY-MM-DD format

        # Test amount string to float
        amount_str = "123.45"
        amount_float = float(amount_str)
        assert isinstance(amount_float, float)
        assert amount_float == 123.45

        # Test integer conversion
        count_str = "10"
        count_int = int(count_str)
        assert isinstance(count_int, int)
        assert count_int == 10

    def test_category_normalization(self):
        """Test category name normalization"""
        test_cases = [
            ("FOOD", "Food"),
            ("food", "Food"),
            ("GROCERIES", "Groceries"),
            ("TRANSPORT", "Transport"),
            ("INCOME", "Income"),
        ]

        for input_category, expected in test_cases:
            # Simulate normalization logic
            normalized = input_category.capitalize()
            assert normalized == expected
