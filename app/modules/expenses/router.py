from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from datetime import date
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.userModel import User
from app.db.models.expenseModel import CategoryEnum
from app.db.database import get_db
from app.modules.expenses.crud import create_expense, read_expense, update_expense, delete_expense, get_dashboard_summary
from app.modules.expenses.services import receipt_to_expense
from app.modules.expenses.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate, DashboardSummary
from app.modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/expense", tags=["Expenses"])

@router.post("/", response_model=ExpenseRead)
def add_expense(expense_data: ExpenseCreate, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ExpenseRead:
    return create_expense(session, expense_data, current_user)


@router.get("/", response_model=List[ExpenseRead])
def get_all_expense(
    skip: int=0, 
    limit: int=5, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[CategoryEnum] = None,
    session: Session=Depends(get_db), 
    user: User=Depends(get_current_user),
) -> List[ExpenseRead]:
    return read_expense(session, user, skip, limit, start_date, end_date, category)

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


@router.get("/summary", response_model=DashboardSummary)
def get_expense_summary(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_dashboard_summary(session, current_user)


@router.post("/extract")
async def extract_expense_from_receipt(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are supported.")

    try:
        file_bytes = await file.read()
        extracted_data = receipt_to_expense(file_bytes)
        return extracted_data
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))