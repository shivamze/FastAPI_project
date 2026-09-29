from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import date
from fastapi import HTTPException
from typing import Optional

from app.db.models.savingsModel import Savings, SavingsTypeEnum
from app.modules.savings.schemas import SavingsCreate, SavingsUpdate
from app.db.models.userModel import User

def create_savings(session: Session, savings_data: SavingsCreate, current_user: User):
    new_savings = Savings(
        user_id=current_user.id,
        savings_type=savings_data.savings_type,
        amount=savings_data.amount,
        source=savings_data.source,
        transaction_date=savings_data.transaction_date or date.today(),
    )

    session.add(new_savings)
    session.commit()
    session.refresh(new_savings)
    return new_savings

def read_savings(
    session: Session, 
    current_user: User, 
    skip: int = 0, 
    limit: int = 5,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    savings_type: Optional[SavingsTypeEnum] = None
):
    query = session.query(Savings).filter(Savings.user_id == current_user.id)

    if start_date:
        query = query.filter(Savings.transaction_date >= start_date)
    if end_date:
        query = query.filter(Savings.transaction_date <= end_date)
    if savings_type:
        query = query.filter(Savings.savings_type == savings_type)

    return query.order_by(desc(Savings.transaction_date)).offset(skip).limit(limit).all()

def update_savings(session: Session, savings_id: int, savings_data: SavingsUpdate, current_user: User):
    db_savings = session.query(Savings).filter(
        Savings.id == savings_id, 
        Savings.user_id == current_user.id
    ).first()

    if not db_savings:
        raise HTTPException(status_code=404, detail="Savings record does not exist")

    update_data = savings_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_savings, key, value)

    session.add(db_savings)
    session.commit()
    session.refresh(db_savings)
    return db_savings

def delete_savings(session: Session, savings_id: int, current_user: User):
    db_savings = session.query(Savings).filter(
        Savings.id == savings_id, 
        Savings.user_id == current_user.id
    ).first()
    
    if not db_savings:
        raise HTTPException(status_code=404, detail="Savings record not found")
    
    session.delete(db_savings)
    session.commit()
    return {"message": "Savings record deleted successfully"}

from sqlalchemy import func

def get_savings_summary(db: Session, user_id: int):
    # Calculate Total Savings/Income
    total_savings = db.query(func.sum(Savings.amount)).filter(Savings.user_id == user_id).scalar() or 0.0
    
    # Group by Savings Type (INCOME, SIP, INVESTMENT, OTHER)
    type_breakdown = db.query(
        Savings.savings_type, 
        func.sum(Savings.amount)
    ).filter(Savings.user_id == user_id).group_by(Savings.savings_type).all()
    
    # Get the 5 most recent transactions
    recent_transactions = db.query(Savings).filter(
        Savings.user_id == user_id
    ).order_by(Savings.transaction_date.desc()).limit(5).all()
    
    return {
        "total_savings": total_savings,
        "breakdown_by_type": [{"type": t[0].value, "amount": t[1]} for t in type_breakdown],
        "recent_transactions": recent_transactions
    }