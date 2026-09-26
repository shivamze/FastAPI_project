from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date
from fastapi import HTTPException
from app.db.models.expenseModel import Expense
from app.modules.expenses.schemas import ExpenseCreate, ExpenseUpdate, ExpenseRead
from app.db.models.userModel import User

def create_expense(session: Session, expense_data: ExpenseCreate, current_user: User):
    new_expense = Expense(
        user_id= current_user.id,
        category = expense_data.category,
        amount = expense_data.amount,
        title = expense_data.title,
        tags = expense_data.tags,
        expense_date = expense_data.expense_date or date.today(),
    )

    session.add(new_expense)
    session.commit()
    session.refresh(new_expense)
    return new_expense

def read_expense(session: Session, current_user: User, skip: int = 0, limit: int = 5):

    expenses = session.query(Expense).filter(Expense.user_id == current_user.id).offset(skip).limit(limit).all()

    return expenses

def update_expense(session: Session, expense_id: int, expense_data: ExpenseUpdate, current_user: User):
    db_expense = session.query(Expense).filter(Expense.id == expense_id).first()

    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense Does not Exist")

    update_data = expense_data.model_dump(exclude_unset=True)

    # 3. Apply the updated values directly to the SQLAlchemy object attributes
    for key, value in update_data.items():
        setattr(db_expense, key, value)

    session.commit()
    session.refresh(db_expense)
    return db_expense

def delete_expense(session: Session, expense_id: int, current_user: User):
    db_expense = session.query(Expense).filter(
        Expense.id == expense_id, 
        Expense.user_id == current_user.id
    ).first()
    
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    session.delete(db_expense)
    session.commit()
    return {"message": "Expense deleted successfully"}

def get_dashboard_summary(session: Session, current_user: User):
    # Get the first day of the current month
    today = date.today()
    start_of_month = today.replace(day=1)

    # 1. Core KPI: Total spent this month
    month_total = session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= start_of_month
    ).scalar() or 0.0

    # 2. Pie Chart Data: Category breakdown for this month
    category_data = session.query(
        Expense.category, 
        func.sum(Expense.amount).label("total")
    ).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= start_of_month
    ).group_by(Expense.category).all()

    # 3. Line Graph Data: Daily trend for this month
    daily_data = session.query(
        Expense.expense_date, 
        func.sum(Expense.amount).label("total")
    ).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= start_of_month
    ).group_by(Expense.expense_date).order_by(Expense.expense_date).all()

    # 4. Feed: 5 most recent transactions (overall)
    recent = session.query(Expense).filter(
        Expense.user_id == current_user.id
    ).order_by(desc(Expense.expense_date)).limit(5).all()

    # Format the raw database rows to match our Pydantic schemas
    return {
        "current_month_total": month_total,
        "category_breakdown": [{"category": row.category.value, "total": row.total} for row in category_data],
        "daily_trend": [{"date": row.expense_date, "total": row.total} for row in daily_data],
        "recent_transactions": recent
    }