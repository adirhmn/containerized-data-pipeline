from sqlalchemy import Column, String, Text, Date, Numeric, TIMESTAMP
from sqlalchemy.orm import Mapped
from database import Base
from sqlalchemy.sql import func

class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = Column(String(50), primary_key=True, index=True)
    first_name: Mapped[str] = Column(String(100), nullable=False)
    last_name: Mapped[str] = Column(String(100), nullable=False)
    email: Mapped[str] = Column(String(255), nullable=False)
    phone: Mapped[str] = Column(String(20), nullable=True)
    address: Mapped[str] = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    account_balance = Column(Numeric(15, 2), nullable=True)
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )