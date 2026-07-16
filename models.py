from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True)

    receipt_id = Column(String, unique=True)

    date = Column(DateTime)

    payment = Column(String)

    amount = Column(Float)


class ReceiptItem(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)

    receipt_id = Column(String)

    name = Column(String)

    price = Column(Float)
