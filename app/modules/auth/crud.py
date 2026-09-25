import logging
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.db.database import engine, SessionLocal
from sqlalchemy.orm import Session
from app.db.models.userModel import User
from app.db.models.refreshModel import RefreshToken
from app.modules.auth.schemas import UserRegister, UserLogin, UserUpdate
from fastapi import HTTPException
from app.core.security import hash_password, create_access_token, verify_password, create_refresh_token, hash_refresh_token
import secrets

logger = logging.getLogger

def register_user(session: Session, user_data: UserRegister):
    if not user_data:
        raise HTTPException(status_code=404, detail="User data not available")

    existing_user = session.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="User Existing Please Login")

    password_hash = hash_password(user_data.password)

    if not password_hash:
        raise HTTPException(status_code=504, detail="password hashing failed")
    
    user_info = User(name=user_data.name, email = user_data.email, password_hash = password_hash)
    session.add(user_info)
    session.commit()
    session.refresh(user_info)
    return user_info


def login_user(session: Session, user_data: UserLogin):

    # 1. Find user by email
    user = session.query(User).filter(
        User.email == user_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="email or password invalid"
        )

    # 2. Verify password
    verify = verify_password(
        user_data.password,
        user.password_hash
    )

    if not verify:
        raise HTTPException(
            status_code=401,
            detail="email or password invalid"
        )

    # 3. Create access token
    access_token = create_access_token(user.id)

    # 4. Create refresh token
    refresh_token = create_refresh_token()

    # 5. Hash refresh token before storing it
    hashed_token = hash_refresh_token(refresh_token)

    # 6. Calculate refresh-token expiry
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    # 7. Create refresh-token database record
    token_update = RefreshToken(
        id=secrets.token_urlsafe(16),
        user_id=user.id,
        token_hash=hashed_token,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc)
    )

    # 8. Save refresh-token record
    session.add(token_update)
    session.commit()
    session.refresh(token_update)

    # 9. Return tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def get_refresh_token(session: Session, refresh_token: str):
    token_hash = hash_refresh_token(refresh_token)

    token_record = session.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    return token_record

def validate_refresh_token(session: Session, refresh_token: str):

    token_record = get_refresh_token(session, refresh_token)

    if not token_record:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh Token"
        )

    if token_record.revoked_at is not None:
        raise HTTPException(
            status_code=401,
            detail="refresh token has been revoked"
        )

    now = datetime.now(timezone.utc)

    if token_record.expires_at <= now:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired"
        )

    return token_record

def refresh_user_token(session: Session, refresh_token: str):
    token_record = validate_refresh_token(session, refresh_token)

    token_record.revoked_at = datetime.now(timezone.utc)

    access_token = create_access_token(
        token_record.user_id
    )

    new_refresh_token = create_refresh_token()

    hashed_token = hash_refresh_token(new_refresh_token)

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    new_token_record = RefreshToken(
        id=secrets.token_urlsafe(16),
        user_id=token_record.user_id,
        token_hash= hashed_token,
        expires_at = expires_at,
        created_at = datetime.now(timezone.utc)
    )

    session.add(new_token_record)

    session.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

def logout_user(session: Session, refresh_token: str):
    token_record = get_refresh_token(session, refresh_token)

    if not token_record:
        raise HTTPException(status_code=401, detail="Invaid or Already revoked Token")

    token_record.revoked_at = datetime.now(timezone.utc)
    session.commit()

    return {"message": "Successfully logged  out"}

def update_user(session: Session, current_user: User, update_data: UserUpdate):
    if update_data.name:
        current_user.name = update_data.name

    if update_data.email:
        # Check if the new email belongs to another user
        existing_user = session.query(User).filter(User.email == update_data.email).first()
        
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=409, detail="Email already in use")
            
        # Safely assign the new email INSIDE the if-block
        current_user.email = update_data.email

    session.commit()
    session.refresh(current_user)

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }
    

def delete_user(session: Session, current_user: User):
    session.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).delete()

    session.delete(current_user)
    session.commit()

    return {"message": "User account deleted successfully"}