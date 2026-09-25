from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt 
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models.userModel import User
from app.db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



def get_current_user(token: str = Depends(oauth2_scheme), session: Session=Depends(get_db)):

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        user_id: str = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid Authentication credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invaid Token")

    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    return user