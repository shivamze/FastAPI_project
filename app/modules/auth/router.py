from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.models.userModel import User

from app.db.database import SessionLocal
from app.modules.auth.crud import register_user, login_user, refresh_user_token, logout_user, delete_user, update_user
from app.modules.auth.schemas import UserRegister, UserLogin, UserUpdate
from app.modules.auth.dependencies import get_current_user
router = APIRouter(prefix="/auth", tags=["Authentication"])
from app.db.database import get_db


@router.post("/register")
def register(user_data: UserRegister, session: Session=Depends(get_db)):
    return register_user(session, user_data)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db)
):
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    return login_user(session, user_data)

@router.post("/refresh")
def refresh(token: str, session: Session=Depends(get_db)):
    return refresh_user_token(session, token)



@router.post("/logout")
def logout(token: str, session: Session=Depends(get_db)):
    return logout_user(session, token)

@router.put("/update")
def update(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session=Depends(get_db)
):
    return update_user(session, current_user, user_data)

@router.delete("/delete")
def delete(
    current_user: User = Depends(get_current_user),
    session: Session=Depends(get_db)
):
    return delete_user(session, current_user)