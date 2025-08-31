from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Date, Float, Integer, String, JSON, Index, UniqueConstraint
from typing import Optional

class Base(DeclarativeBase):
    pass

class Transaction(Base):
    __tablename__ = "transactions"

    # Primary key with implicit index (no need for explicit index=True)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Core columns without individual indexes (data is processed in pandas)
    date: Mapped[Date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Optimized indexes based on actual query patterns
    __table_args__ = (
        # Prevent duplicate transactions - this is the most important constraint
        UniqueConstraint('date', 'description', 'amount', name='unique_transaction'),
        
        # Single optimized index for the most common filter: amount < 0 (expenses)
        # This supports the primary query pattern in insights.py
        Index('idx_amount_date', 'amount', 'date'),  # Supports filtering by amount with date ordering
    )
