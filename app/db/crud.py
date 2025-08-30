from sqlalchemy.orm import Session
from db.models import Transaction
from datetime import datetime

def insert_transaction(db: Session, tx: dict):
    transaction = Transaction(
        date=datetime.strptime(tx["date"], "%Y-%m-%d").date(),
        description=tx["description"],
        amount=tx["amount"],
        category=tx.get("category"),
        payment_method=tx.get("payment_method"),
        raw_data=tx,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_db():
    from config import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
