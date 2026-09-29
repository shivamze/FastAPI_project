from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db.models.userModel import User
from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user

from app.modules.savings.crud import create_savings, read_savings, update_savings, delete_savings, get_savings_summary
from app.modules.savings.schemas import SavingsCreate, SavingsRead, SavingsUpdate
from app.db.models.savingsModel import SavingsTypeEnum

router = APIRouter(prefix="/savings", tags=["Savings"])

@router.post("/", response_model=SavingsRead)
def add_savings(
    savings_data: SavingsCreate, 
    session: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> SavingsRead:
    return create_savings(session, savings_data, current_user)

@router.get("/savings", response_model=List[SavingsRead])
def get_all_savings(
    skip: int = 0, 
    limit: int = 5, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    savings_type: Optional[SavingsTypeEnum] = None,
    session: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
) -> List[SavingsRead]:
    return read_savings(session, user, skip, limit, start_date, end_date, savings_type)

@router.patch("/{savings_id}", response_model=SavingsRead)
def modify_savings(
    savings_id: int,
    savings_data: SavingsUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    return update_savings(session, savings_id, savings_data, current_user)

@router.delete("/{savings_id}")
def remove_savings(
    savings_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    return delete_savings(session, savings_id, current_user)

from app.modules.savings.crud import get_savings_summary
# ... your existing imports ...

@router.get("/summary")
def get_savings_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns aggregated savings data for the frontend dashboard.
    """
    return get_savings_summary(db=db, user_id=current_user.id)