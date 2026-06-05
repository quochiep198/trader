import uuid
from sqlalchemy import Column, String, Boolean, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # 'BUY' hoặc 'SELL'
    entry_price = Column(Numeric(18, 2), nullable=False)
    exit_price = Column(Numeric(18, 2), nullable=True)
    quantity = Column(Integer, nullable=False)
    stop_loss = Column(Numeric(18, 2), nullable=True)
    take_profit = Column(Numeric(18, 2), nullable=True)
    reason = Column(String, nullable=False)
    emotion_text = Column(String, nullable=False)
    status = Column(String(20), nullable=False, default="planned")  # 'planned', 'opened', 'closed', 'cancelled'
    profit_loss_amount = Column(Numeric(18, 2), nullable=True)
    profit_loss_percent = Column(Numeric(5, 2), nullable=True)
    discipline_score = Column(Integer, nullable=False)
    had_cooldown = Column(Boolean, nullable=False, default=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime, nullable=True)
