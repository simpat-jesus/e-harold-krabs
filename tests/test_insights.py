import pytest
from app.services.insights import get_summary, get_categories, get_monthly_trends
from unittest.mock import Mock

def test_get_summary_empty():
    """Test summary calculation with no transactions"""
    mock_db = Mock()
    mock_db.query.return_value.all.return_value = []

    result = get_summary(mock_db)

    assert result["total_income"] == 0
    assert result["total_expenses"] == 0
    assert result["balance"] == 0
    assert result["transactions"] == 0

def test_get_summary_with_transactions():
    """Test summary calculation with sample transactions"""
    mock_db = Mock()

    # Mock transactions
    mock_transaction1 = Mock()
    mock_transaction1.date = "2025-01-01"
    mock_transaction1.description = "Salary"
    mock_transaction1.amount = 3000.00
    mock_transaction1.category = "Income"

    mock_transaction2 = Mock()
    mock_transaction2.date = "2025-01-02"
    mock_transaction2.description = "Groceries"
    mock_transaction2.amount = -150.00
    mock_transaction2.category = "Food"

    mock_transaction3 = Mock()
    mock_transaction3.date = "2025-01-03"
    mock_transaction3.description = "Gas"
    mock_transaction3.amount = -50.00
    mock_transaction3.category = "Transportation"

    mock_db.query.return_value.all.return_value = [
        mock_transaction1, mock_transaction2, mock_transaction3
    ]

    result = get_summary(mock_db)

    assert result["total_income"] == 3000.00
    assert result["total_expenses"] == -200.00  # -150 + -50
    assert result["balance"] == 2800.00  # 3000 - 200
    assert result["transactions"] == 3

def test_get_categories_empty():
    """Test category aggregation with no transactions"""
    mock_db = Mock()
    mock_db.query.return_value.all.return_value = []

    result = get_categories(mock_db)
    assert isinstance(result, list)
    assert len(result) == 0

def test_get_categories_with_data():
    """Test category aggregation with transactions"""
    mock_db = Mock()

    # Mock transactions
    mock_transaction1 = Mock()
    mock_transaction1.category = "Food"
    mock_transaction1.amount = -100.00

    mock_transaction2 = Mock()
    mock_transaction2.category = "Food"
    mock_transaction2.amount = -50.00

    mock_transaction3 = Mock()
    mock_transaction3.category = "Transportation"
    mock_transaction3.amount = -75.00

    mock_db.query.return_value.all.return_value = [
        mock_transaction1, mock_transaction2, mock_transaction3
    ]

    result = get_categories(mock_db)

    assert isinstance(result, list)
    assert len(result) == 2  # Two categories

    # Find Food category
    food_category = next(cat for cat in result if cat["category"] == "Food")
    assert food_category["amount"] == 150.00  # Absolute value of -150

    # Find Transportation category
    transport_category = next(cat for cat in result if cat["category"] == "Transportation")
    assert transport_category["amount"] == 75.00

def test_get_monthly_trends_empty():
    """Test monthly trends with no transactions"""
    mock_db = Mock()
    mock_db.query.return_value.all.return_value = []

    result = get_monthly_trends(mock_db)
    assert isinstance(result, list)
    assert len(result) == 0

def test_get_monthly_trends_with_data():
    """Test monthly trends aggregation"""
    mock_db = Mock()

    # Mock transactions for different months
    mock_transaction1 = Mock()
    mock_transaction1.date = "2025-01-15"
    mock_transaction1.amount = 1000.00

    mock_transaction2 = Mock()
    mock_transaction2.date = "2025-01-20"
    mock_transaction2.amount = -200.00

    mock_transaction3 = Mock()
    mock_transaction3.date = "2025-02-10"
    mock_transaction3.amount = 1500.00

    mock_db.query.return_value.all.return_value = [
        mock_transaction1, mock_transaction2, mock_transaction3
    ]

    result = get_monthly_trends(mock_db)

    assert isinstance(result, list)
    assert len(result) == 2  # Two months

    # Check January total
    january = next(month for month in result if month["month"] == "2025-01")
    assert january["amount"] == 800.00  # 1000 - 200

    # Check February total
    february = next(month for month in result if month["month"] == "2025-02")
    assert february["amount"] == 1500.00
