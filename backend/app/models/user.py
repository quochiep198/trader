import uuid
from sqlalchemy import Column, String, DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    verification_token = Column(String(255), nullable=True)
    reset_password_token = Column(String(255), nullable=True)
    reset_password_expires = Column(DateTime, nullable=True)

    # Risk Profile Fields
    account_size = Column(Numeric(18, 2), nullable=False, default=0.00)
    default_max_risk_per_trade = Column(Numeric(5, 2), nullable=False, default=2.00)
    trading_style = Column(String(50), nullable=False, default="Swing")
    experience_level = Column(String(50), nullable=False, default="Beginner")

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
