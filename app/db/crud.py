from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import Transaction
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def insert_transaction(db: Session, tx: dict):
    """
    Insert a transaction, handling duplicates gracefully.
    If a duplicate exists (same date, description, amount), skip insertion.
    """
    try:
        transaction = Transaction(
            date=datetime.strptime(tx["date"], "%Y-%m-%d").date(),
            description=tx["description"],
            amount=tx["amount"],
            category=tx.get("category", "Uncategorized"),
            raw_data=tx,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    except IntegrityError:
        # Duplicate transaction detected, rollback and skip
        db.rollback()
        # Log safely without exposing sensitive data
        logger.info(f"Duplicate transaction skipped - date: {tx.get('date', 'unknown')}, category: {tx.get('category', 'unknown')}")
        return None

def insert_transactions_batch(db: Session, transactions: list):
    """
    Insert multiple transactions efficiently, handling duplicates.
    Returns count of successfully inserted transactions.
    """
    inserted_count = 0
    for tx in transactions:
        result = insert_transaction(db, tx)
        if result:
            inserted_count += 1
    return inserted_count

def get_db():
    from config import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
