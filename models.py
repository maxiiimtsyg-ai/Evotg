from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True)

    receipt_id = Column(String, unique=True, index=True)

    store_id = Column(String)
    device_id = Column(String)
    employee_id = Column(String)
    shift_id = Column(String)

    payment = Column(String)

    amount = Column(Float)

    date = Column(DateTime)


class ReceiptItem(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)

    receipt_id = Column(String, index=True)

    name = Column(String)

    price = Column(Float)

    quantity = Column(Float)
