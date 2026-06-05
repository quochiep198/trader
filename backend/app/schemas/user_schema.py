from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    account_size: Optional[Decimal] = Decimal('0.00')
    default_max_risk_per_trade: Optional[Decimal] = Decimal('2.00')
    trading_style: Optional[str] = 'Swing'
    experience_level: Optional[str] = 'Beginner'

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    account_size: Optional[Decimal] = None
    default_max_risk_per_trade: Optional[Decimal] = None
    trading_style: Optional[str] = None
    experience_level: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
