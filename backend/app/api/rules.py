from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Any
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.rule import Rule
from app.models.user import User
from app.schemas.rule_schema import RuleResponse, RuleValueUpdate, RuleToggleResponse
from app.core.messages import MessageProperties

router = APIRouter()

@router.get("/", response_model=List[RuleResponse])
def get_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Lấy toàn bộ danh sách quy tắc giao dịch cá nhân của user hiện tại
    rules = db.query(Rule).filter(Rule.user_id == current_user.id).all()
    
    # Nếu chưa có rule nào (do đăng ký từ trước khi cập nhật code), tự động khởi tạo mặc định (lazy seeding)
    if not rules:
        default_rules = [
            Rule(user_id=current_user.id, rule_type="require_stop_loss", rule_value="yes", is_active=True),
            Rule(user_id=current_user.id, rule_type="max_risk_per_trade", rule_value="2%", is_active=True),
            Rule(user_id=current_user.id, rule_type="max_consecutive_losses", rule_value="3", is_active=True),
            Rule(user_id=current_user.id, rule_type="max_fomo_score", rule_value="7", is_active=True),
            Rule(user_id=current_user.id, rule_type="max_trades_per_day", rule_value="5", is_active=False),
            Rule(user_id=current_user.id, rule_type="cooldown_after_loss", rule_value="24", is_active=False),
            Rule(user_id=current_user.id, rule_type="prevent_oversized_trade", rule_value="-15", is_active=True),
        ]
        db.add_all(default_rules)
        db.commit()
        # Lấy lại danh sách rule sau khi seed
        rules = db.query(Rule).filter(Rule.user_id == current_user.id).all()
        
    return rules

@router.put("/{rule_id}/toggle", response_model=RuleToggleResponse)
def toggle_rule(
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # 1. Kiểm tra sự tồn tại của rule và kiểm tra quyền sở hữu của user hiện tại
    rule = db.query(Rule).filter(Rule.id == rule_id, Rule.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MessageProperties.RULE_NOT_FOUND
        )

    # 2. Đảo trạng thái active
    rule.is_active = not rule.is_active
    db.commit()
    db.refresh(rule)

    return {
        "id": rule.id,
        "is_active": rule.is_active,
        "message": MessageProperties.RULE_TOGGLE_SUCCESS
    }

@router.put("/{rule_id}/value")
def update_rule_value(
    rule_id: uuid.UUID,
    payload: RuleValueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # 1. Kiểm tra sự tồn tại của rule và quyền sở hữu
    rule = db.query(Rule).filter(Rule.id == rule_id, Rule.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MessageProperties.RULE_NOT_FOUND
        )

    val_str = payload.rule_value.strip()

    # 2. Thực hiện kiểm tra tính hợp lệ nghiệp vụ dựa trên loại quy tắc
    if rule.rule_type == "max_risk_per_trade":
        # Chấp nhận dạng số có hoặc không có dấu '%' ở cuối, ví dụ '2%' hoặc '2'
        clean_val = val_str.rstrip('%').strip()
        try:
            val = float(clean_val)
            if val <= 0 or val >= 100:
                raise ValueError()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MessageProperties.RULE_VALUE_INVALID
            )
        # Đồng bộ lưu trữ dạng số + % cho hiển thị thống nhất
        if not val_str.endswith('%'):
            val_str = f"{clean_val}%"

    elif rule.rule_type in ["max_consecutive_losses", "max_trades_per_day", "cooldown_after_loss"]:
        try:
            val = int(val_str)
            if val <= 0:
                raise ValueError()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MessageProperties.RULE_VALUE_INVALID
            )

    elif rule.rule_type == "max_fomo_score":
        try:
            val = int(val_str)
            if val < 1 or val > 10:
                raise ValueError()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MessageProperties.RULE_VALUE_INVALID
            )

    elif rule.rule_type == "prevent_oversized_trade":
        try:
            # Cho phép số nguyên âm hoặc dương
            int(val_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MessageProperties.RULE_VALUE_INVALID
            )

    elif rule.rule_type == "require_stop_loss":
        if val_str.lower() not in ["true", "false", "yes", "no"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MessageProperties.RULE_VALUE_INVALID
            )

    # 3. Cập nhật và lưu vào cơ sở dữ liệu
    rule.rule_value = val_str
    db.commit()
    db.refresh(rule)

    return {
        "message": MessageProperties.RULE_UPDATE_SUCCESS,
        "rule": {
            "id": str(rule.id),
            "rule_type": rule.rule_type,
            "rule_value": rule.rule_value,
            "is_active": rule.is_active
        }
    }
