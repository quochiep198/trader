import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class MarketContextLog(Base):
    __tablename__ = "market_context_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    emotion_log_id = Column(UUID(as_uuid=True), ForeignKey("emotion_logs.id", ondelete="CASCADE"), nullable=False)
    trade_id = Column(UUID(as_uuid=True), ForeignKey("trades.id", ondelete="SET NULL"), nullable=True)
    symbol = Column(String(20), nullable=False)
    current_price = Column(Numeric(18, 2), nullable=False)
    price_change_1d = Column(Numeric(5, 2), nullable=False)
    price_change_3d = Column(Numeric(5, 2), nullable=False)
    price_change_5d = Column(Numeric(5, 2), nullable=False)
    price_change_20d = Column(Numeric(5, 2), nullable=False)
    consecutive_up_sessions = Column(Integer, nullable=False)
    consecutive_down_sessions = Column(Integer, nullable=False)
    volume_vs_20d_avg = Column(Numeric(6, 2), nullable=False)
    current_vs_entry_percent = Column(Numeric(5, 2), nullable=False)
    distance_to_stop_loss_percent = Column(Numeric(5, 2), nullable=True)
    distance_to_take_profit_percent = Column(Numeric(5, 2), nullable=True)
    data_status = Column(String(20), nullable=False)
    market_context_risk = Column(String(20), nullable=False)
    market_warnings = Column(String, nullable=False)  # Comma-separated warnings e.g. "market_fomo_context,buying_chase_risk"
    message = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
