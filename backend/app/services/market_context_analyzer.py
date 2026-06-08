from typing import Dict, Any, List, Optional
from decimal import Decimal

class MarketContextAnalyzer:
    @staticmethod
    def get_close_ago(sessions: List[Dict[str, Any]], days: int) -> float:
        if not sessions:
            return 0.0
        # sessions is sorted oldest to newest. sessions[-1] is current/latest.
        idx = -(days + 1)
        if abs(idx) <= len(sessions):
            return float(sessions[idx]["close"])
        return float(sessions[0]["close"])

    @classmethod
    def compute_metrics(
        cls,
        current_price: float,
        volume: int,
        sessions: List[Dict[str, Any]],
        action: str,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        average_entry_price: Optional[float] = None
    ) -> Dict[str, Any]:
        if not sessions:
            return {
                "price_change_1d": 0.0,
                "price_change_3d": 0.0,
                "price_change_5d": 0.0,
                "price_change_20d": 0.0,
                "consecutive_up_sessions": 0,
                "consecutive_down_sessions": 0,
                "volume_vs_20d_avg": 1.0,
                "current_vs_entry_percent": 0.0,
                "distance_to_stop_loss_percent": None,
                "distance_to_take_profit_percent": None
            }

        close_1d = cls.get_close_ago(sessions, 1)
        close_3d = cls.get_close_ago(sessions, 3)
        close_5d = cls.get_close_ago(sessions, 5)
        close_20d = cls.get_close_ago(sessions, 20)

        # Changes in percentage
        price_change_1d = ((current_price - close_1d) / close_1d * 100) if close_1d else 0.0
        price_change_3d = ((current_price - close_3d) / close_3d * 100) if close_3d else 0.0
        price_change_5d = ((current_price - close_5d) / close_5d * 100) if close_5d else 0.0
        price_change_20d = ((current_price - close_20d) / close_20d * 100) if close_20d else 0.0

        # Streak calculation (comparing sequential closes from latest back to start)
        consecutive_up = 0
        for i in range(len(sessions) - 1, 0, -1):
            if sessions[i]["close"] > sessions[i-1]["close"]:
                consecutive_up += 1
            else:
                break

        consecutive_down = 0
        for i in range(len(sessions) - 1, 0, -1):
            if sessions[i]["close"] < sessions[i-1]["close"]:
                consecutive_down += 1
            else:
                break

        # Volume ratio vs 20-day average
        session_volumes = [s["volume"] for s in sessions if s.get("volume")]
        avg_volume = sum(session_volumes) / len(session_volumes) if session_volumes else 1.0
        volume_vs_20d_avg = volume / avg_volume if avg_volume > 0 else 1.0

        # Plan-relative metrics
        current_vs_entry_percent = 0.0
        if action == "BUY" and entry_price and entry_price > 0:
            current_vs_entry_percent = (current_price - entry_price) / entry_price * 100
        elif action == "SELL_TO_CLOSE" and average_entry_price and average_entry_price > 0:
            current_vs_entry_percent = (current_price - average_entry_price) / average_entry_price * 100

        distance_to_stop_loss_percent = None
        if action == "BUY" and stop_loss and stop_loss > 0:
            distance_to_stop_loss_percent = (current_price - stop_loss) / current_price * 100

        distance_to_take_profit_percent = None
        if action == "BUY" and take_profit and take_profit > 0:
            distance_to_take_profit_percent = (take_profit - current_price) / current_price * 100

        return {
            "price_change_1d": round(price_change_1d, 2),
            "price_change_3d": round(price_change_3d, 2),
            "price_change_5d": round(price_change_5d, 2),
            "price_change_20d": round(price_change_20d, 2),
            "consecutive_up_sessions": consecutive_up,
            "consecutive_down_sessions": consecutive_down,
            "volume_vs_20d_avg": round(volume_vs_20d_avg, 2),
            "current_vs_entry_percent": round(current_vs_entry_percent, 2),
            "distance_to_stop_loss_percent": round(distance_to_stop_loss_percent, 2) if distance_to_stop_loss_percent is not None else None,
            "distance_to_take_profit_percent": round(distance_to_take_profit_percent, 2) if distance_to_take_profit_percent is not None else None
        }

    @classmethod
    def generate_warnings_and_risk(
        cls,
        metrics: Dict[str, Any],
        emotion_scores: Dict[str, int],
        data_status: str,
        action: str
    ) -> Dict[str, Any]:
        warnings = []
        
        # 1. Check data status first
        if data_status == "unavailable":
            warnings.append("unavailable_market_data")
            return {
                "market_warnings": warnings,
                "market_context_risk": "low",
                "message": "Không có dữ liệu giá đủ mới. Kết quả kiểm tra hiện chỉ dựa trên rule, risk và cảm xúc của bạn."
            }
        elif data_status == "stale":
            warnings.append("stale_market_data")

        # Extract metrics
        p_change_3d = metrics["price_change_3d"]
        up_streak = metrics["consecutive_up_sessions"]
        down_streak = metrics["consecutive_down_sessions"]
        vol_ratio = metrics["volume_vs_20d_avg"]
        entry_dist = metrics["current_vs_entry_percent"]
        dist_sl = metrics["distance_to_stop_loss_percent"]
        dist_tp = metrics["distance_to_take_profit_percent"]

        # Extract emotion scores
        fomo_score = emotion_scores.get("fomo_score", 0)
        panic_score = emotion_scores.get("panic_score", 0)

        # 2. Warning Evaluation
        # market_fomo_context
        if (p_change_3d >= 7.0 or up_streak >= 3) and fomo_score >= 6:
            warnings.append("market_fomo_context")

        # buying_chase_risk (BUY only)
        if action == "BUY" and entry_dist >= 3.0:
            warnings.append("buying_chase_risk")

        # panic_context
        if (p_change_3d <= -7.0 or down_streak >= 3) and panic_score >= 6:
            warnings.append("panic_context")

        # near_stop_loss (BUY only)
        if action == "BUY" and dist_sl is not None and 0.0 < dist_sl <= 2.0:
            warnings.append("near_stop_loss")

        # near_take_profit (BUY only)
        if action == "BUY" and dist_tp is not None and 0.0 < dist_tp <= 2.0:
            warnings.append("near_take_profit")

        # volume_spike_context
        if vol_ratio >= 2.0:
            warnings.append("volume_spike_context")

        # 3. Determine Risk Rating
        risk_level = "low"
        if "market_fomo_context" in warnings or "panic_context" in warnings or (action == "BUY" and entry_dist >= 5.0):
            risk_level = "high"
        elif "buying_chase_risk" in warnings or "near_stop_loss" in warnings or "volume_spike_context" in warnings:
            risk_level = "medium"

        # 4. Formulate localized message
        msg_parts = []
        if "market_fomo_context" in warnings:
            msg_parts.append("Giá đã tăng nhanh nhiều phiên kết hợp điểm FOMO cao, tăng nguy cơ mua đuổi cảm tính.")
        elif "buying_chase_risk" in warnings:
            msg_parts.append(f"Giá hiện tại cao hơn entry kế hoạch {entry_dist}%, đây là bối cảnh dễ kích hoạt mua đuổi.")
            
        if "panic_context" in warnings:
            msg_parts.append("Giá đang giảm mạnh nhiều phiên kết hợp điểm hoảng loạn cao, dễ khiến bạn bán tháo mất kiểm soát.")
            
        if "near_stop_loss" in warnings:
            msg_parts.append("Giá đang rất gần Stop-loss kế hoạch. Hãy kiên định chấp nhận sai, tuyệt đối không dời Stop-loss do cảm xúc.")
        elif "near_take_profit" in warnings:
            msg_parts.append("Giá đang tiệm cận Take-profit. Hãy tuân thủ kế hoạch chốt lời thay vì tham lam giữ thêm.")

        if not msg_parts:
            if data_status == "stale":
                msg_parts.append("Dữ liệu giá thị trường hiện tại có độ trễ lớn, vui lòng cẩn trọng khi tham khảo.")
            else:
                msg_parts.append("Bối cảnh giá thị trường hiện tại ổn định và nằm trong vùng kiểm soát kế hoạch giao dịch của bạn.")

        message = " ".join(msg_parts)

        return {
            "market_warnings": warnings,
            "market_context_risk": risk_level,
            "message": message
        }
