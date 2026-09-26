from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date
from app.db.models.expenseModel import CategoryEnum

class ExpenseCreate(BaseModel):
    category: CategoryEnum
    amount: float
    title: str
    tags: Optional[List[str]] = []
    expense_date: Optional[date] = None

class ExpenseUpdate(BaseModel):
    category: Optional[CategoryEnum] = None
    amount: Optional[float] = None
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    expense_date: Optional[date] = None

class ExpenseRead(BaseModel):
    id: int
    user_id: int
    category: CategoryEnum
    amount: float
    title: str
    tags: List[str]
    expense_date: date
    
    model_config = ConfigDict(from_attributes=True)

class CategoryTotal(BaseModel):
    category: str
    total: float

class DailyTrend(BaseModel):
    date: date
    total: float

class DashboardSummary(BaseModel):
    current_month_total: float
    category_breakdown: List[CategoryTotal]
    daily_trend: List[DailyTrend]
    recent_transactions: List[ExpenseRead]