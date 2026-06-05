from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import uuid
import json
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.messages import MessageProperties
from app.models.user import User
from app.models.emotion_log import EmotionLog
from app.schemas.trade_schema import (
    TradeCheckInput,
    TradeCheckAcknowledgeInput,
    TradeCheckResponse,
    AcknowledgeResponse,
    RiskCalculation,
    RuleViolation,
    EmotionScores,
    AIIntervention
)
from app.services.ai_service import AIService
from app.services.risk_calculator import RiskCalculator
from app.services.rule_engine import RuleEngine

router = APIRouter()

DEFAULT_COOLDOWN_QUESTIONS = (
    "1. Lý do vào/thoát lệnh có nằm trong kế hoạch không?\n"
    "2. Nếu sai, bạn mất bao nhiêu?\n"
    "3. Bạn có sẵn sàng chấp nhận mức lỗ đó không?"
)

@router.post("", response_model=TradeCheckResponse)
async def check_trade(
    payload: TradeCheckInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # 1. Calculate Risk Parameters
    if payload.action == "BUY":
        risk_calc_dict = RiskCalculator.calculate_buy_risk(
            entry_price=payload.entry_price,
            quantity=payload.quantity,
            stop_loss=payload.stop_loss,
            account_size=current_user.account_size
        )
    else:  # SELL_TO_CLOSE
        risk_calc_dict = RiskCalculator.calculate_sell_risk(
            sell_price=payload.sell_price,
            quantity=payload.quantity,
            average_entry_price=payload.average_entry_price
        )

    # 2. Call AI Emotion Analysis with Fallback
    ai_service = AIService()
    ai_result = await ai_service.analyze_emotion(
        reason=payload.reason,
        emotion_text=payload.emotion_text
    )

    if ai_result:
        raw_ai_response = json.dumps(ai_result, ensure_ascii=False)
        emotion_tags = ai_result.get("emotion_tags", ["Neutral"])
        
        # Parse emotion scores safely
        emotion_scores_dict = {
            "fomo_score": int(ai_result.get("fomo_score", 0)),
            "panic_score": int(ai_result.get("panic_score", 0)),
            "revenge_score": int(ai_result.get("revenge_score", 0)),
            "overconfidence_score": int(ai_result.get("overconfidence_score", 0)),
            "greed_score": int(ai_result.get("greed_score", 0)),
            "hesitation_score": int(ai_result.get("hesitation_score", 0))
        }
        
        ai_should_cooldown = bool(ai_result.get("should_cooldown", False))
        coach_message = ai_result.get("coach_message", "")
        ai_reflection_question = ai_result.get("reflection_question", None)
    else:
        # Fallback Triggered
        raw_ai_response = "Fallback triggered"
        emotion_tags = ["Neutral"]
        emotion_scores_dict = {
            "fomo_score": 0,
            "panic_score": 0,
            "revenge_score": 0,
            "overconfidence_score": 0,
            "greed_score": 0,
            "hesitation_score": 0
        }
        ai_should_cooldown = False
        coach_message = "Hệ thống không thể phân tích cảm xúc lúc này do sự cố kết nối. Hãy tự rà soát kỷ luật giao dịch của bạn trước khi tiếp tục."
        ai_reflection_question = None

    # 3. Evaluate rules via Rule Engine
    rule_result = RuleEngine.evaluate_rules(
        db=db,
        user_id=current_user.id,
        action=payload.action,
        entry_price=payload.entry_price,
        sell_price=payload.sell_price,
        quantity=payload.quantity,
        stop_loss=payload.stop_loss,
        take_profit=payload.take_profit,
        reason=payload.reason,
        emotion_text=payload.emotion_text,
        confidence_level=payload.confidence_level,
        emotion_scores=emotion_scores_dict,
        account_size=current_user.account_size
    )

    # 4. Merge Cooldown conditions
    should_cooldown = ai_should_cooldown or rule_result["should_cooldown"]

    # If cooldown is triggered, configure intervention
    intervention = None
    if should_cooldown:
        reflection_question = ai_reflection_question or DEFAULT_COOLDOWN_QUESTIONS
        intervention = AIIntervention(
            is_required=True,
            reflection_question=reflection_question
        )

    # 5. Create EmotionLog DB Record
    emotion_log = EmotionLog(
        user_id=current_user.id,
        reason=payload.reason,
        emotion_text=payload.emotion_text,
        emotion_tags=",".join(emotion_tags),
        fomo_score=emotion_scores_dict["fomo_score"],
        panic_score=emotion_scores_dict["panic_score"],
        revenge_score=emotion_scores_dict["revenge_score"],
        overconfidence_score=emotion_scores_dict["overconfidence_score"],
        greed_score=emotion_scores_dict["greed_score"],
        hesitation_score=emotion_scores_dict["hesitation_score"],
        discipline_risk=rule_result["discipline_risk"],
        should_cooldown=should_cooldown,
        coach_message=coach_message,
        raw_ai_response=raw_ai_response
    )
    db.add(emotion_log)
    db.commit()
    db.refresh(emotion_log)

    # 6. Build response object
    return TradeCheckResponse(
        log_id=emotion_log.id,
        discipline_score=rule_result["discipline_score"],
        discipline_risk=rule_result["discipline_risk"],
        should_cooldown=should_cooldown,
        coach_message=coach_message,
        emotion_tags=emotion_tags,
        risk_calculation=RiskCalculation(**risk_calc_dict),
        rule_violations=[RuleViolation(**v) for v in rule_result["violations"]],
        emotion_scores=EmotionScores(**emotion_scores_dict),
        intervention=intervention
    )

@router.post("/{log_id}/acknowledge", response_model=AcknowledgeResponse)
def acknowledge_cooldown(
    log_id: uuid.UUID,
    payload: TradeCheckAcknowledgeInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # 1. Fetch the log and verify ownership
    emotion_log = (
        db.query(EmotionLog)
        .filter(EmotionLog.id == log_id, EmotionLog.user_id == current_user.id)
        .first()
    )
    if not emotion_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MessageProperties.TRADE_CHECK_LOG_NOT_FOUND
        )

    # 2. Update reflection answer and mark acknowledged
    emotion_log.reflective_answer = payload.reflective_answer
    emotion_log.cooldown_acknowledged = True
    db.commit()

    return AcknowledgeResponse(
        success=True,
        message=MessageProperties.TRADE_CHECK_ACKNOWLEDGE_SUCCESS
    )
