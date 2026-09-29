from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from app.db.models.savingsModel import SavingsTypeEnum

class SavingsCreate(BaseModel):
    savings_type: SavingsTypeEnum
    amount: float
    source: str
    transaction_date: Optional[date] = None

class SavingsUpdate(BaseModel):
    savings_type: Optional[SavingsTypeEnum] = None
    amount: Optional[float] = None
    source: Optional[str] = None
    transaction_date: Optional[date] = None

class SavingsRead(BaseModel):
    id: int
    user_id: int
    savings_type: SavingsTypeEnum
    amount: float
    source: str
    transaction_date: date
    
    model_config = ConfigDict(from_attributes=True)