from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class TradeCheckInput(BaseModel):
    symbol: str = Field(..., min_length=1, description="Ticker symbol")
    action: str = Field(..., description="Action type: BUY or SELL_TO_CLOSE")
    entry_price: Optional[Decimal] = Field(None, description="Entry price (required for BUY)")
    sell_price: Optional[Decimal] = Field(None, description="Sell price (required for SELL_TO_CLOSE)")
    quantity: int = Field(..., description="Quantity")
    stop_loss: Optional[Decimal] = Field(None, description="Stop-loss price")
    take_profit: Optional[Decimal] = Field(None, description="Take-profit price")
    average_entry_price: Optional[Decimal] = Field(None, description="Average entry price (optional for SELL_TO_CLOSE)")
    reason: str = Field(..., min_length=1, description="Strategic rationale")
    emotion_text: str = Field(..., min_length=1, description="Mental state description")
    confidence_level: int = Field(..., ge=0, le=10, description="Conviction level 0-10")

    @field_validator('symbol')
    @classmethod
    def symbol_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Mã chứng khoán không được rỗng")
        return v.strip().upper()

    @field_validator('action')
    @classmethod
    def action_valid(cls, v: str) -> str:
        if v not in ("BUY", "SELL_TO_CLOSE"):
            raise ValueError("Hành động chỉ có thể là BUY hoặc SELL_TO_CLOSE")
        return v

    @field_validator('quantity')
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Số lượng phải là số nguyên dương")
        return v

    @model_validator(mode='after')
    def validate_prices(self):
        if self.action == "BUY":
            if self.entry_price is None or self.entry_price <= 0:
                raise ValueError("Giá vào lệnh phải là số dương đối với lệnh BUY")
            if self.stop_loss is not None:
                if self.stop_loss <= 0:
                    raise ValueError("Giá Stop-loss phải là số dương")
                if self.stop_loss >= self.entry_price:
                    raise ValueError("Giá Stop-loss phải nhỏ hơn giá vào lệnh (Entry Price)")
            if self.take_profit is not None and self.take_profit <= 0:
                raise ValueError("Giá Take-profit phải là số dương")
        elif self.action == "SELL_TO_CLOSE":
            if self.sell_price is None or self.sell_price <= 0:
                raise ValueError("Giá bán phải là số dương đối với lệnh SELL_TO_CLOSE")
            if self.average_entry_price is not None and self.average_entry_price <= 0:
                raise ValueError("Giá vào trung bình phải là số dương")
        return self

class TradeCheckAcknowledgeInput(BaseModel):
    reflective_answer: str = Field(..., description="Mandatory reflection answer")

    @field_validator('reflective_answer')
    @classmethod
    def check_min_length(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Câu trả lời phản tỉnh phải có độ dài tối thiểu 10 ký tự")
        return v.strip()

class RiskCalculation(BaseModel):
    risk_per_share: Optional[Decimal] = None
    total_risk: Optional[Decimal] = None
    risk_percent: Optional[float] = None
    trade_value: Optional[Decimal] = None
    estimated_pnl_amount: Optional[Decimal] = None
    estimated_pnl_percent: Optional[float] = None

class RuleViolation(BaseModel):
    rule_type: str
    message: str
    severity: str
    penalty: int

class EmotionScores(BaseModel):
    fomo_score: int
    panic_score: int
    revenge_score: int
    overconfidence_score: int
    greed_score: int
    hesitation_score: int

class AIIntervention(BaseModel):
    is_required: bool
    reflection_question: str

class MarketContextResponse(BaseModel):
    symbol: str
    current_price: float
    price_change_1d: float
    price_change_3d: float
    price_change_5d: float
    price_change_20d: float
    consecutive_up_sessions: int
    consecutive_down_sessions: int
    volume_vs_20d_avg: float
    current_vs_entry_percent: float
    distance_to_stop_loss_percent: Optional[float] = None
    distance_to_take_profit_percent: Optional[float] = None
    data_status: str
    market_context_risk: str
    market_warnings: List[str]
    message: str

class MarketSnapshotResponse(BaseModel):
    symbol: str
    provider: str
    current_price: float
    fetched_at: datetime
    data_status: str
    price_change_1d: float
    price_change_3d: float
    price_change_5d: float
    price_change_20d: float
    consecutive_up_sessions: int
    consecutive_down_sessions: int
    volume_vs_20d_avg: float

class TradeCheckResponse(BaseModel):
    log_id: UUID
    discipline_score: int
    discipline_risk: str
    should_cooldown: bool
    coach_message: str
    emotion_tags: List[str]
    risk_calculation: RiskCalculation
    rule_violations: List[RuleViolation]
    emotion_scores: EmotionScores
    intervention: Optional[AIIntervention] = None
    market_context: Optional[MarketContextResponse] = None

class MarketContextCheckInput(BaseModel):
    symbol: str
    action: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    average_entry_price: Optional[float] = None
    emotion_scores: EmotionScores

class AcknowledgeResponse(BaseModel):
    success: bool
    message: str


