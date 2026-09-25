from sqlalchemy import  Boolean, Integer, String, ForeignKey, Column, DateTime
from datetime import timezone, datetime
from app.db.database import Base
from app.db.models.userModel import User

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)