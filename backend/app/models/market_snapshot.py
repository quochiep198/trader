import uuid
from sqlalchemy import Column, String, BigInteger, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    current_price = Column(Numeric(18, 2), nullable=False)
    open_price = Column(Numeric(18, 2), nullable=False)
    high_price = Column(Numeric(18, 2), nullable=False)
    low_price = Column(Numeric(18, 2), nullable=False)
    close_price = Column(Numeric(18, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    session_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    data_status = Column(String(20), nullable=False, default="fresh")
    fetched_at = Column(DateTime, nullable=False, default=func.now())
    created_at = Column(DateTime, nullable=False, default=func.now())
