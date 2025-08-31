"""
Utility functions for masking sensitive data in logs and error messages.
"""
import re
from typing import Any, Dict, List, Union


def mask_transaction_description(description: str) -> str:
    """
    Mask sensitive parts of transaction descriptions while keeping useful info.
    
    Args:
        description: Original transaction description
        
    Returns:
        Masked description safe for logging
    """
    if not description:
        return "N/A"
    
    # Keep first 3 and last 2 characters, mask the middle
    if len(description) <= 5:
        return "*" * len(description)
    
    return f"{description[:3]}***{description[-2:]}"


def mask_amount(amount: float) -> str:
    """
    Mask transaction amounts for logging.
    
    Args:
        amount: Transaction amount
        
    Returns:
        Masked amount string
    """
    if amount == 0:
        return "$0.00"
    
    # Show only the magnitude (positive/negative) and rough order
    if abs(amount) < 10:
        return "$*.xx"
    elif abs(amount) < 100:
        return "$**.xx"
    elif abs(amount) < 1000:
        return "$***.xx"
    else:
        return "$*****.xx"


def mask_transaction_data(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a masked version of transaction data safe for logging.
    
    Args:
        transaction: Original transaction dictionary
        
    Returns:
        Masked transaction data
    """
    masked = transaction.copy()
    
    if 'description' in masked:
        masked['description'] = mask_transaction_description(masked['description'])
    
    if 'amount' in masked:
        masked['amount'] = mask_amount(masked['amount'])
    
    # Keep safe fields as-is
    safe_fields = ['date', 'category', 'id']
    
    return {k: v for k, v in masked.items() if k in safe_fields or k in ['description', 'amount']}


def mask_sql_query(query: str) -> str:
    """
    Mask sensitive data in SQL queries for logging.
    
    Args:
        query: SQL query string
        
    Returns:
        Masked query safe for logging
    """
    # Remove potential sensitive data from VALUES clauses
    query = re.sub(r"VALUES\s*\([^)]+\)", "VALUES (**MASKED**)", query, flags=re.IGNORECASE)
    
    # Mask WHERE clause values
    query = re.sub(r"=\s*'[^']+'", "= '***'", query)
    query = re.sub(r"=\s*\d+\.\d+", "= ***.**", query)
    
    return query


def sanitize_error_message(error_msg: str) -> str:
    """
    Remove sensitive data from error messages.
    
    Args:
        error_msg: Original error message
        
    Returns:
        Sanitized error message
    """
    # Remove potential transaction data patterns
    error_msg = re.sub(r'\$\d+\.?\d*', '$***.**', error_msg)
    error_msg = re.sub(r"'[^']{10,}'", "'***MASKED***'", error_msg)
    
    return error_msg


def get_safe_transaction_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a safe summary of transactions for logging.
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Safe summary data
    """
    if not transactions:
        return {"count": 0, "categories": [], "date_range": None}
    
    categories = list(set(tx.get('category', 'Unknown') for tx in transactions))
    dates = [tx.get('date') for tx in transactions if tx.get('date')]
    
    return {
        "count": len(transactions),
        "categories": categories,
        "date_range": {
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None
        },
        "amount_ranges": {
            "has_income": any(tx.get('amount', 0) > 0 for tx in transactions),
            "has_expenses": any(tx.get('amount', 0) < 0 for tx in transactions)
        }
    }
