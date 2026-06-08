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
from app.models.market_snapshot import MarketSnapshot
from app.models.market_context_log import MarketContextLog
from app.schemas.trade_schema import (
    TradeCheckInput,
    TradeCheckAcknowledgeInput,
    TradeCheckResponse,
    AcknowledgeResponse,
    RiskCalculation,
    RuleViolation,
    EmotionScores,
    AIIntervention,
    MarketSnapshotResponse,
    MarketContextResponse,
    MarketContextCheckInput
)
from app.services.ai_service import AIService
from app.services.risk_calculator import RiskCalculator
from app.services.rule_engine import RuleEngine
from app.services.market_data_service import MockMarketDataProvider
from app.services.market_context_analyzer import MarketContextAnalyzer


router = APIRouter()
market_provider = MockMarketDataProvider()

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
    # 1. Fetch market snapshot and sessions
    symbol = payload.symbol.strip().upper()
    try:
        snapshot = await market_provider.get_snapshot(symbol)
        sessions = await market_provider.get_ohlcv_sessions(symbol, sessions=20)
        
        # Calculate metrics
        market_metrics = MarketContextAnalyzer.compute_metrics(
            current_price=snapshot["current_price"],
            volume=snapshot["volume"],
            sessions=sessions,
            action=payload.action,
            entry_price=float(payload.entry_price) if payload.entry_price else None,
            stop_loss=float(payload.stop_loss) if payload.stop_loss else None,
            take_profit=float(payload.take_profit) if payload.take_profit else None,
            average_entry_price=float(payload.average_entry_price) if payload.average_entry_price else None
        )
        data_status = snapshot["data_status"]
        current_price = snapshot["current_price"]
    except Exception as e:
        print(f"Market data fetch failed: {e}")
        # Fallback to unavailable
        market_metrics = MarketContextAnalyzer.compute_metrics(
            current_price=0.0,
            volume=0,
            sessions=[],
            action=payload.action
        )
        data_status = "unavailable"
        current_price = 0.0

    # 2. Calculate Risk Parameters
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

    # 3. Call AI Emotion Analysis with Fallback
    ai_service = AIService()
    ai_market_context = {
        "current_price": current_price,
        "price_change_3d": market_metrics["price_change_3d"],
        "consecutive_up_sessions": market_metrics["consecutive_up_sessions"],
        "consecutive_down_sessions": market_metrics["consecutive_down_sessions"],
        "volume_vs_20d_avg": market_metrics["volume_vs_20d_avg"],
        "current_vs_entry_percent": market_metrics["current_vs_entry_percent"]
    } if data_status != "unavailable" else None

    ai_result = await ai_service.analyze_emotion(
        reason=payload.reason,
        emotion_text=payload.emotion_text,
        market_context=ai_market_context
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

    # Calculate warnings using AI scores and calculated metrics
    warnings_and_risk = MarketContextAnalyzer.generate_warnings_and_risk(
        metrics=market_metrics,
        emotion_scores=emotion_scores_dict,
        data_status=data_status,
        action=payload.action
    )

    # 4. Evaluate rules via Rule Engine
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

    # 5. Merge Cooldown conditions
    should_cooldown = ai_should_cooldown or rule_result["should_cooldown"]

    # If cooldown is triggered, configure intervention
    intervention = None
    if should_cooldown:
        reflection_question = ai_reflection_question or DEFAULT_COOLDOWN_QUESTIONS
        intervention = AIIntervention(
            is_required=True,
            reflection_question=reflection_question
        )

    # 6. Create EmotionLog DB Record
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

    # 7. Create MarketContextLog DB Record
    market_log = MarketContextLog(
        user_id=current_user.id,
        emotion_log_id=emotion_log.id,
        symbol=symbol,
        current_price=current_price,
        price_change_1d=market_metrics["price_change_1d"],
        price_change_3d=market_metrics["price_change_3d"],
        price_change_5d=market_metrics["price_change_5d"],
        price_change_20d=market_metrics["price_change_20d"],
        consecutive_up_sessions=market_metrics["consecutive_up_sessions"],
        consecutive_down_sessions=market_metrics["consecutive_down_sessions"],
        volume_vs_20d_avg=market_metrics["volume_vs_20d_avg"],
        current_vs_entry_percent=market_metrics["current_vs_entry_percent"],
        distance_to_stop_loss_percent=market_metrics["distance_to_stop_loss_percent"],
        distance_to_take_profit_percent=market_metrics["distance_to_take_profit_percent"],
        data_status=data_status,
        market_context_risk=warnings_and_risk["market_context_risk"],
        market_warnings=",".join(warnings_and_risk["market_warnings"]),
        message=warnings_and_risk["message"]
    )
    db.add(market_log)
    db.commit()

    market_context_resp = MarketContextResponse(
        symbol=symbol,
        current_price=current_price,
        price_change_1d=market_metrics["price_change_1d"],
        price_change_3d=market_metrics["price_change_3d"],
        price_change_5d=market_metrics["price_change_5d"],
        price_change_20d=market_metrics["price_change_20d"],
        consecutive_up_sessions=market_metrics["consecutive_up_sessions"],
        consecutive_down_sessions=market_metrics["consecutive_down_sessions"],
        volume_vs_20d_avg=market_metrics["volume_vs_20d_avg"],
        current_vs_entry_percent=market_metrics["current_vs_entry_percent"],
        distance_to_stop_loss_percent=market_metrics["distance_to_stop_loss_percent"],
        distance_to_take_profit_percent=market_metrics["distance_to_take_profit_percent"],
        data_status=data_status,
        market_context_risk=warnings_and_risk["market_context_risk"],
        market_warnings=warnings_and_risk["market_warnings"],
        message=warnings_and_risk["message"]
    )

    # 8. Build response object
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
        intervention=intervention,
        market_context=market_context_resp
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

@router.get("/market/snapshot", response_model=MarketSnapshotResponse)
async def get_market_snapshot(
    symbol: str,
    db: Session = Depends(get_db)
) -> Any:
    symbol = symbol.strip().upper()
    try:
        snapshot = await market_provider.get_snapshot(symbol)
        sessions = await market_provider.get_ohlcv_sessions(symbol, sessions=20)
        
        # Calculate historical metrics for snapshot
        metrics = MarketContextAnalyzer.compute_metrics(
            current_price=snapshot["current_price"],
            volume=snapshot["volume"],
            sessions=sessions,
            action="BUY" # default
        )
        
        # Cache snapshot in database
        db_snap = MarketSnapshot(
            symbol=symbol,
            provider=snapshot["provider"],
            current_price=snapshot["current_price"],
            open_price=snapshot["open_price"],
            high_price=snapshot["high_price"],
            low_price=snapshot["low_price"],
            close_price=snapshot["close_price"],
            volume=snapshot["volume"],
            session_date=snapshot["session_date"],
            data_status=snapshot["data_status"],
            fetched_at=snapshot["fetched_at"]
        )
        db.add(db_snap)
        db.commit()
        
        return MarketSnapshotResponse(
            symbol=symbol,
            provider=snapshot["provider"],
            current_price=snapshot["current_price"],
            fetched_at=snapshot["fetched_at"],
            data_status=snapshot["data_status"],
            price_change_1d=metrics["price_change_1d"],
            price_change_3d=metrics["price_change_3d"],
            price_change_5d=metrics["price_change_5d"],
            price_change_20d=metrics["price_change_20d"],
            consecutive_up_sessions=metrics["consecutive_up_sessions"],
            consecutive_down_sessions=metrics["consecutive_down_sessions"],
            volume_vs_20d_avg=metrics["volume_vs_20d_avg"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy dữ liệu thị trường cho {symbol}: {str(e)}"
        )

@router.post("/market/context-check", response_model=Dict[str, Any])
async def check_market_context(
    payload: MarketContextCheckInput,
    current_user: User = Depends(get_current_user)
) -> Any:
    symbol = payload.symbol.strip().upper()
    try:
        snapshot = await market_provider.get_snapshot(symbol)
        sessions = await market_provider.get_ohlcv_sessions(symbol, sessions=20)
        
        metrics = MarketContextAnalyzer.compute_metrics(
            current_price=snapshot["current_price"],
            volume=snapshot["volume"],
            sessions=sessions,
            action=payload.action,
            entry_price=payload.entry_price,
            stop_loss=payload.stop_loss,
            take_profit=payload.take_profit,
            average_entry_price=payload.average_entry_price
        )
        
        emotion_scores_dict = {
            "fomo_score": payload.emotion_scores.fomo_score,
            "panic_score": payload.emotion_scores.panic_score,
            "revenge_score": payload.emotion_scores.revenge_score,
            "overconfidence_score": payload.emotion_scores.overconfidence_score,
            "greed_score": payload.emotion_scores.greed_score,
            "hesitation_score": payload.emotion_scores.hesitation_score
        }
        
        warnings_and_risk = MarketContextAnalyzer.generate_warnings_and_risk(
            metrics=metrics,
            emotion_scores=emotion_scores_dict,
            data_status=snapshot["data_status"],
            action=payload.action
        )
        
        return {
            "market_context": {
                "symbol": symbol,
                "current_price": snapshot["current_price"],
                "price_change_1d": metrics["price_change_1d"],
                "price_change_3d": metrics["price_change_3d"],
                "price_change_5d": metrics["price_change_5d"],
                "price_change_20d": metrics["price_change_20d"],
                "consecutive_up_sessions": metrics["consecutive_up_sessions"],
                "consecutive_down_sessions": metrics["consecutive_down_sessions"],
                "volume_vs_20d_avg": metrics["volume_vs_20d_avg"],
                "current_vs_entry_percent": metrics["current_vs_entry_percent"],
                "distance_to_stop_loss_percent": metrics["distance_to_stop_loss_percent"],
                "distance_to_take_profit_percent": metrics["distance_to_take_profit_percent"],
                "data_status": snapshot["data_status"],
                "market_context_risk": warnings_and_risk["market_context_risk"],
                "market_warnings": warnings_and_risk["market_warnings"],
                "message": warnings_and_risk["message"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi phân tích bối cảnh thị trường cho {symbol}: {str(e)}"
        )
