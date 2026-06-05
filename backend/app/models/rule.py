import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rule_type = Column(String(50), nullable=False)
    rule_value = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Ràng buộc UNIQUE tránh trùng lặp cùng một rule trên một user
    __table_args__ = (
        UniqueConstraint("user_id", "rule_type", name="uq_user_rule_type"),
    )
