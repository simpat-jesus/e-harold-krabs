import pytest
from unittest.mock import Mock

class TestInsightsUnit:
    """Unit tests for insights calculations"""

    def test_calculate_total_income(self):
        """Test calculation of total income from transactions"""
        # Mock transactions with positive amounts (income)
        transactions = [
            Mock(amount=1000.00, category="Salary"),
            Mock(amount=500.00, category="Freelance"),
            Mock(amount=-200.00, category="Food"),  # Expense
        ]

        # Simulate income calculation logic
        total_income = sum(t.amount for t in transactions if t.amount > 0)

        assert total_income == 1500.00

    def test_calculate_total_expenses(self):
        """Test calculation of total expenses from transactions"""
        transactions = [
            Mock(amount=1000.00, category="Salary"),  # Income
            Mock(amount=-200.00, category="Food"),
            Mock(amount=-150.00, category="Transport"),
        ]

        # Simulate expense calculation logic
        total_expenses = sum(t.amount for t in transactions if t.amount < 0)

        assert total_expenses == -350.00

    def test_calculate_balance(self):
        """Test balance calculation"""
        total_income = 1500.00
        total_expenses = -350.00

        balance = total_income + total_expenses  # expenses are negative

        assert balance == 1150.00

    def test_transaction_count(self):
        """Test counting transactions"""
        transactions = [
            Mock(amount=1000.00),
            Mock(amount=-200.00),
            Mock(amount=500.00),
            Mock(amount=-150.00),
        ]

        count = len(transactions)

        assert count == 4

    def test_empty_transaction_list(self):
        """Test handling of empty transaction list"""
        transactions = []

        total_income = sum(t.amount for t in transactions if hasattr(t, 'amount') and t.amount > 0)
        total_expenses = sum(t.amount for t in transactions if hasattr(t, 'amount') and t.amount < 0)
        balance = total_income + total_expenses
        count = len(transactions)

        assert total_income == 0
        assert total_expenses == 0
        assert balance == 0
        assert count == 0

    def test_category_filtering(self):
        """Test filtering transactions by category"""
        transactions = [
            Mock(amount=1000.00, category="Salary"),
            Mock(amount=-200.00, category="Food"),
            Mock(amount=-150.00, category="Food"),
            Mock(amount=500.00, category="Freelance"),
        ]

        # Filter by category
        food_transactions = [t for t in transactions if t.category == "Food"]
        income_transactions = [t for t in transactions if t.category in ["Salary", "Freelance"]]

        assert len(food_transactions) == 2
        assert len(income_transactions) == 2

        food_total = sum(t.amount for t in food_transactions)
        assert food_total == -350.00
