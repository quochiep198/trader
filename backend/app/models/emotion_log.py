import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    trade_id = Column(UUID(as_uuid=True), ForeignKey("trades.id", ondelete="SET NULL"), nullable=True)
    reason = Column(String, nullable=False)
    emotion_text = Column(String, nullable=False)
    emotion_tags = Column(String(255), nullable=False)
    fomo_score = Column(Integer, nullable=False, default=0)
    panic_score = Column(Integer, nullable=False, default=0)
    revenge_score = Column(Integer, nullable=False, default=0)
    overconfidence_score = Column(Integer, nullable=False, default=0)
    greed_score = Column(Integer, nullable=False, default=0)
    hesitation_score = Column(Integer, nullable=False, default=0)
    discipline_risk = Column(String(50), nullable=False)
    should_cooldown = Column(Boolean, nullable=False, default=False)
    reflective_answer = Column(String, nullable=True)
    cooldown_acknowledged = Column(Boolean, nullable=False, default=False)
    coach_message = Column(String, nullable=False)
    raw_ai_response = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
