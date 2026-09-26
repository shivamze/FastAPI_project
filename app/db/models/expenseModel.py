import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, Enum, JSON
from datetime import timezone, datetime
from app.db.database import Base

class CategoryEnum(str, enum.Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    UTILITIES = "Utilities"
    RENT = "Rent"
    ENTERTAINMENT = "Entertainment"
    HEALTHCARE = "Healthcare"
    SHOPING = "Shoping"
    OTHER = "Other"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    category = Column(Enum(CategoryEnum), nullable=False)
    amount = Column(Float, nullable=False)
    title = Column(String, nullable=False)

    tags = Column(JSON, default=list, nullable=True)

    expense_date = Column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    