from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Any
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.core.messages import MessageProperties

router = APIRouter()

class LoginPayload(BaseModel):
    email: str
    password: str

class RegisterPayload(BaseModel):
    email: str
    password: str
    name: str

@router.post("/register")
def register(payload: RegisterPayload, db: Session = Depends(get_db)) -> Any:
    # 1. Kiểm tra email đã đăng ký chưa
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=MessageProperties.EMAIL_ALREADY_REGISTERED
        )

    # 2. Băm mật khẩu bảo mật
    hashed_pwd = get_password_hash(payload.password)

    # 3. Tạo tài khoản người dùng mới và lưu vào cơ sở dữ liệu
    new_user = User(
        email=payload.email,
        password_hash=hashed_pwd,
        name=payload.name,
        account_size=0.00,  # mặc định
        default_max_risk_per_trade=2.00,  # mặc định
        trading_style="Swing",
        experience_level="Beginner"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. Tự động tạo hạt giống dữ liệu (Seed default rules) cho người dùng mới để kích hoạt kỷ luật
    from app.models.rule import Rule
    default_rules = [
        Rule(user_id=new_user.id, rule_type="require_stop_loss", rule_value="yes", is_active=True),
        Rule(user_id=new_user.id, rule_type="max_risk_per_trade", rule_value="2%", is_active=True),
        Rule(user_id=new_user.id, rule_type="max_consecutive_losses", rule_value="3", is_active=True),
        Rule(user_id=new_user.id, rule_type="max_fomo_score", rule_value="7", is_active=True),
        Rule(user_id=new_user.id, rule_type="max_trades_per_day", rule_value="5", is_active=False),
        Rule(user_id=new_user.id, rule_type="cooldown_after_loss", rule_value="24", is_active=False),
        Rule(user_id=new_user.id, rule_type="prevent_oversized_trade", rule_value="-15", is_active=True),
    ]
    db.add_all(default_rules)
    db.commit()

    return {
        "message": MessageProperties.REGISTER_SUCCESS
    }


@router.post("/login")
def login(payload: LoginPayload, db: Session = Depends(get_db)) -> Any:
    # 1. Tìm tài khoản trong DB theo email
    user = db.query(User).filter(User.email == payload.email).first()

    # 2. Xác thực thông tin tài khoản và mật khẩu nhập từ input chống lại password_hash của database
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail=MessageProperties.INVALID_CREDENTIALS
        )

    # 3. Tạo JWT access token thực tế
    access_token = create_access_token(subject=str(user.id))

    # 4. Trả về token và dữ liệu cấu hình
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "account_size": float(user.account_size),
            "default_max_risk_per_trade": float(user.default_max_risk_per_trade),
            "trading_style": user.trading_style,
            "experience_level": user.experience_level,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    }
