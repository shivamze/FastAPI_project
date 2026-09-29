import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, Enum
from datetime import timezone, datetime
from app.db.database import Base

class SavingsTypeEnum(str, enum.Enum):
    INCOME = "Income"
    SIP = "SIP"
    INVESTMENT = "Investment"
    OTHER = "Other"

class Savings(Base):
    __tablename__ = "savings"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    savings_type = Column(Enum(SavingsTypeEnum), nullable=False)
    amount = Column(Float, nullable=False)
    source = Column(String, nullable=False)

    transaction_date = Column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    created_ate = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)