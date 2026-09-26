from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.models.userModel import User
from app.db.database import get_db
from app.modules.expenses.crud import create_expense, read_expense, update_expense, delete_expense
from app.modules.expenses.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/expense", tags=["Expenses"])

@router.post("/", response_model=ExpenseRead)
def add_expense(expense_data: ExpenseCreate, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ExpenseRead:
    return create_expense(session, expense_data, current_user)


@router.get("/", response_model=List[ExpenseRead])
def get_all_expense(skip: int=0, limit: int=5, session: Session=Depends(get_db), user: User=Depends(get_current_user)) -> List[ExpenseRead]:
    return read_expense(session, user, skip, limit)

@router.patch("/{expense_id}", response_model=ExpenseRead)
def modify_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: User=Depends(get_current_user),
    session: Session=Depends(get_db)
):
    return update_expense(session, expense_id, expense_data, current_user)

@router.delete("/{expense_id}")
def remove_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    return delete_expense(session, expense_id, current_user)