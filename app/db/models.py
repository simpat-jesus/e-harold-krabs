from sqlalchemy import Column, Integer, String, Float, Date, JSON
from config import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    description = Column(String)
    amount = Column(Float)
    category = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    raw_data = Column(JSON)
