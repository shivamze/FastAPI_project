from sqlalchemy.orm import Session
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