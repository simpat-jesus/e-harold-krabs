"""
Secure logging configuration for finance application.
Filters out sensitive data and provides safe logging utilities.
"""
import logging
import re
from typing import Any


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter to remove sensitive data from log records.
    """
    
    # Patterns that might contain sensitive data
    SENSITIVE_PATTERNS = [
        (r'\$\d+\.?\d*', '$***.**'),                    # Dollar amounts
        (r'amount["\']?\s*:\s*["\']?-?\d+\.?\d*', 'amount: ***.**'),  # Amount fields
        (r'description["\']?\s*:\s*["\'][^"\']*["\']', 'description: "***"'),  # Description fields
        (r'account["\']?\s*:\s*["\']?\d{4,}["\']?', 'account: "***"'),  # Account numbers
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '****-****-****-****'),  # Credit card numbers
        (r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****'),     # SSN pattern
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record to remove sensitive data.
        
        Args:
            record: Log record to filter
            
        Returns:
            True to allow the record, False to block it
        """
        if hasattr(record, 'msg') and record.msg:
            message = str(record.msg)
            
            # Apply all sensitive data patterns
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
            
            record.msg = message
        
        return True


def setup_secure_logging():
    """
    Set up secure logging configuration for the application.
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # Add sensitive data filter
    sensitive_filter = SensitiveDataFilter()
    handler.addFilter(sensitive_filter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    
    return root_logger


def log_transaction_summary(logger: logging.Logger, transactions: list, operation: str = "processed"):
    """
    Safely log transaction summary without exposing sensitive data.
    
    Args:
        logger: Logger instance
        transactions: List of transactions
        operation: Operation performed (e.g., "inserted", "processed", "skipped")
    """
    if not transactions:
        logger.info(f"No transactions {operation}")
        return
    
    # Create safe summary
    categories = list(set(tx.get('category', 'Unknown') for tx in transactions))
    dates = [tx.get('date') for tx in transactions if tx.get('date')]
    
    summary = {
        "count": len(transactions),
        "categories": categories[:5],  # Limit to first 5 categories
        "date_range": {
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None
        }
    }
    
    logger.info(f"Transactions {operation}: {summary}")


def log_database_operation(logger: logging.Logger, operation: str, table: str, success: bool, count: int = None):
    """
    Safely log database operations without exposing sensitive data.
    
    Args:
        logger: Logger instance
        operation: Database operation (e.g., "INSERT", "UPDATE", "DELETE")
        table: Table name
        success: Whether operation was successful
        count: Number of records affected (optional)
    """
    status = "successful" if success else "failed"
    count_msg = f" ({count} records)" if count is not None else ""
    
    logger.info(f"Database {operation} on {table} - {status}{count_msg}")


# Configure secure logging on module import
setup_secure_logging()
