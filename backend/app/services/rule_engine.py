from decimal import Decimal
from typing import Optional, Dict, Any, List
from datetime import datetime
import pytz
from sqlalchemy.orm import Session
from app.models.rule import Rule
from app.models.trade import Trade

class RuleEngine:
    @staticmethod
    def get_historical_stats(db: Session, user_id: Any) -> Dict[str, Any]:
        # 1. Calculate consecutive losses
        # Fetch last closed trades ordered by created_at desc
        closed_trades = (
            db.query(Trade)
            .filter(Trade.user_id == user_id, Trade.status == "closed")
            .order_by(Trade.created_at.desc())
            .all()
        )
        consecutive_losses = 0
        for t in closed_trades:
            if t.profit_loss_amount is not None and t.profit_loss_amount < 0:
                consecutive_losses += 1
            else:
                break

        # 2. Count trades today in Asia/Ho_Chi_Minh timezone
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vn = datetime.now(vn_tz)
        start_of_today_vn = now_vn.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_today_utc = start_of_today_vn.astimezone(pytz.utc).replace(tzinfo=None)

        trades_today = (
            db.query(Trade)
            .filter(Trade.user_id == user_id, Trade.created_at >= start_of_today_utc)
            .count()
        )

        # 3. Calculate median trade value for last 20 trades
        last_20_trades = (
            db.query(Trade)
            .filter(Trade.user_id == user_id)
            .order_by(Trade.created_at.desc())
            .limit(20)
            .all()
        )
        trade_values = []
        for t in last_20_trades:
            # use entry_price if available, else exit_price (for SELL_TO_CLOSE if average entry is missing)
            price = t.entry_price or t.exit_price or Decimal(0)
            val = price * t.quantity
            if val > 0:
                trade_values.append(val)

        if not trade_values:
            median_trade_value_last_20 = Decimal(0)
        else:
            trade_values.sort()
            n = len(trade_values)
            if n % 2 == 1:
                median_trade_value_last_20 = trade_values[n // 2]
            else:
                median_trade_value_last_20 = (trade_values[n // 2 - 1] + trade_values[n // 2]) / Decimal(2)

        # 4. Total trades count
        total_trades_count = db.query(Trade).filter(Trade.user_id == user_id).count()

        return {
            "consecutive_losses": consecutive_losses,
            "trades_today": trades_today,
            "median_trade_value_last_20": median_trade_value_last_20,
            "total_trades_count": total_trades_count
        }

    @classmethod
    def evaluate_rules(
        cls,
        db: Session,
        user_id: Any,
        action: str,
        entry_price: Optional[Decimal],
        sell_price: Optional[Decimal],
        quantity: int,
        stop_loss: Optional[Decimal],
        take_profit: Optional[Decimal],
        reason: str,
        emotion_text: str,
        confidence_level: int,
        emotion_scores: Dict[str, int],
        account_size: Decimal
    ) -> Dict[str, Any]:
        # Fetch stats
        stats = cls.get_historical_stats(db, user_id)
        consecutive_losses = stats["consecutive_losses"]
        trades_today = stats["trades_today"]
        median_trade_value_last_20 = stats["median_trade_value_last_20"]
        total_trades_count = stats["total_trades_count"]

        # Fetch user's rules
        rules = db.query(Rule).filter(Rule.user_id == user_id).all()
        rules_dict = {r.rule_type: r for r in rules}

        def get_rule(rule_type: str, default_active: bool, default_val: str):
            r = rules_dict.get(rule_type)
            if r:
                return r.is_active, r.rule_value
            return default_active, default_val

        require_sl_active, _ = get_rule("require_stop_loss", True, "true")
        max_risk_active, max_risk_val = get_rule("max_risk_per_trade", True, "2")
        max_loss_active, max_loss_val = get_rule("max_consecutive_losses", True, "3")
        max_fomo_active, max_fomo_val = get_rule("max_fomo_score", True, "7")
        max_trades_active, max_trades_val = get_rule("max_trades_per_day", False, "5")
        prevent_oversized_active, _ = get_rule("prevent_oversized_trade", True, "true")

        violations = []

        # 1. Stop loss check (for BUY)
        if action == "BUY":
            if not stop_loss and require_sl_active:
                violations.append({
                    "rule_type": "require_stop_loss",
                    "message": "Lệnh BUY chưa có Stop-Loss.",
                    "severity": "high",
                    "penalty": 25,
                    "group": "stop_loss_missing"
                })
        
        # 2. Max risk per trade check (for BUY)
        if action == "BUY" and stop_loss and entry_price:
            risk_per_share = entry_price - stop_loss
            total_risk = risk_per_share * quantity
            if account_size > 0:
                risk_percent = (total_risk / account_size) * Decimal(100)
                try:
                    max_risk_limit = Decimal(max_risk_val.replace("%", "").strip())
                except:
                    max_risk_limit = Decimal(2)
                if max_risk_active and risk_percent > max_risk_limit:
                    violations.append({
                        "rule_type": "max_risk_per_trade",
                        "message": f"Rủi ro lệnh ({risk_percent:.2f}%) vượt mức tối đa cho phép ({max_risk_limit}%).",
                        "severity": "high",
                        "penalty": 20,
                        "group": "max_risk_exceeded"
                    })

        # 3. Consecutive losses check
        try:
            max_losses_limit = int(max_loss_val)
        except:
            max_losses_limit = 3
        if max_loss_active and consecutive_losses >= max_losses_limit:
            violations.append({
                "rule_type": "max_consecutive_losses",
                "message": f"Số trận thua liên tiếp hiện tại ({consecutive_losses}) đã chạm hoặc vượt giới hạn kỷ luật ({max_losses_limit}).",
                "severity": "critical",
                "penalty": 20,
                "group": "consecutive_losses"
            })

        # 4. FOMO check
        try:
            max_fomo_limit = int(max_fomo_val)
        except:
            max_fomo_limit = 7
        fomo_score = emotion_scores.get("fomo_score", 0)
        if max_fomo_active and fomo_score > max_fomo_limit:
            violations.append({
                "rule_type": "max_fomo_score",
                "message": f"Điểm FOMO ({fomo_score}) vượt giới hạn kỷ luật cho phép ({max_fomo_limit}).",
                "severity": "high",
                "penalty": 15,
                "group": "fomo"
            })
        elif fomo_score >= 8:
            violations.append({
                "rule_type": "fomo_high",
                "message": f"Điểm FOMO ({fomo_score}) quá cao, vi phạm quy tắc tâm lý.",
                "severity": "high",
                "penalty": 15,
                "group": "fomo"
            })

        # 5. Trades per day check
        try:
            max_trades_limit = int(max_trades_val)
        except:
            max_trades_limit = 5
        if max_trades_active and trades_today >= max_trades_limit:
            violations.append({
                "rule_type": "max_trades_per_day",
                "message": f"Số lượng giao dịch hôm nay ({trades_today}) đã vượt giới hạn hàng ngày ({max_trades_limit}).",
                "severity": "medium",
                "penalty": 15,
                "group": "trades_today"
            })

        # 6. Oversized trade check (for BUY)
        oversized_triggered = False
        oversized_severity = "medium"
        oversized_cooldown = False
        oversized_message = ""

        if action == "BUY" and prevent_oversized_active and entry_price:
            trade_value = entry_price * quantity
            risk_percent = Decimal(0)
            if stop_loss and account_size > 0:
                risk_percent = ((entry_price - stop_loss) * quantity) / account_size * Decimal(100)

            try:
                max_risk_limit = Decimal(max_risk_val.replace("%", "").strip())
            except:
                max_risk_limit = Decimal(2)

            # Condition 1
            if stop_loss and risk_percent >= Decimal('1.5') * max_risk_limit:
                oversized_triggered = True
                oversized_severity = "critical"
                oversized_cooldown = True
                oversized_message = f"Lệnh có rủi ro quá lớn ({risk_percent:.2f}% vượt 1.5 lần giới hạn rủi ro)."
            # Condition 4
            elif consecutive_losses >= 2 and median_trade_value_last_20 > 0 and trade_value >= Decimal('1.5') * median_trade_value_last_20:
                oversized_triggered = True
                oversized_severity = "critical"
                oversized_cooldown = True
                oversized_message = f"Giao dịch quá cỡ sau chuỗi thua ({consecutive_losses} trận thua liên tiếp, giá trị vị thế {trade_value:.2f} vượt 1.5 lần trung vị {median_trade_value_last_20:.2f})."
            # Condition 2
            elif median_trade_value_last_20 > 0 and trade_value >= Decimal('2') * median_trade_value_last_20:
                oversized_triggered = True
                oversized_severity = "medium"
                oversized_message = f"Giá trị vị thế ({trade_value:.2f}) vượt quá 2 lần trung vị giao dịch trước đó ({median_trade_value_last_20:.2f})."
            # Condition 3
            elif total_trades_count < 5 and account_size > 0 and trade_value > Decimal('0.5') * account_size:
                oversized_triggered = True
                oversized_severity = "medium"
                oversized_message = f"Người dùng mới giao dịch vị thế quá lớn ({trade_value:.2f} vượt 50% quy mô tài khoản {account_size:.2f})."

            if oversized_triggered:
                violations.append({
                    "rule_type": "prevent_oversized_trade",
                    "message": oversized_message,
                    "severity": oversized_severity,
                    "penalty": 15,
                    "group": "oversized",
                    "should_cooldown": oversized_cooldown
                })

        # 7. Other emotion penalties:
        # revenge_score >= 8: -25, critical
        # panic_score >= 8: -20, critical
        # overconfidence_score >= 8: -15, medium
        # confidence_level >= 9 và overconfidence_score >= 7: -10, medium
        # Thiếu take_profit: -5, low
        # Không có reason/exit_reason rõ ràng (length < 10): -15, low
        # Keyword nguy hiểm: -25, critical

        revenge_score = emotion_scores.get("revenge_score", 0)
        if revenge_score >= 8:
            violations.append({
                "rule_type": "revenge_high",
                "message": f"Phát hiện tâm lý phục thù rất cao ({revenge_score}).",
                "severity": "critical",
                "penalty": 25,
                "group": "revenge"
            })

        panic_score = emotion_scores.get("panic_score", 0)
        if panic_score >= 8:
            violations.append({
                "rule_type": "panic_high",
                "message": f"Phát hiện tâm lý hoảng loạn rất cao ({panic_score}).",
                "severity": "critical",
                "penalty": 20,
                "group": "panic"
            })

        overconfidence_score = emotion_scores.get("overconfidence_score", 0)
        if overconfidence_score >= 8:
            violations.append({
                "rule_type": "overconfidence_high",
                "message": f"Phát hiện tâm lý quá tự tin ({overconfidence_score}).",
                "severity": "medium",
                "penalty": 15,
                "group": "overconfidence"
            })
        elif confidence_level >= 9 and overconfidence_score >= 7:
            violations.append({
                "rule_type": "overconfidence_confidence_high",
                "message": "Độ tự tin cực cao kết hợp điểm quá tự tin từ AI cảnh báo rủi ro ảo tưởng.",
                "severity": "medium",
                "penalty": 10,
                "group": "overconfidence"
            })

        if action == "BUY" and not take_profit:
            violations.append({
                "rule_type": "take_profit_missing",
                "message": "Lệnh BUY chưa cấu hình mục tiêu Take-Profit.",
                "severity": "low",
                "penalty": 5,
                "group": "take_profit_missing"
            })

        if not reason or len(reason.strip()) < 10:
            violations.append({
                "rule_type": "reason_unclear",
                "message": "Lý do giao dịch quá ngắn hoặc không rõ ràng (tối thiểu 10 ký tự).",
                "severity": "low",
                "penalty": 15,
                "group": "reason"
            })

        # Dangerous keywords check
        dangerous_keywords = ["all-in", "gỡ lỗ", "mua bằng mọi giá", "không thể giảm nữa"]
        found_keywords = [kw for kw in dangerous_keywords if kw in reason.lower() or kw in emotion_text.lower()]
        if found_keywords:
            violations.append({
                "rule_type": "dangerous_keywords",
                "message": f"Phát hiện từ khóa giao dịch nguy hiểm: {', '.join(found_keywords)}.",
                "severity": "critical",
                "penalty": 25,
                "group": "dangerous_keywords"
            })

        # Calculate Grouped Penalties (Only max penalty per group)
        grouped_penalties = {}
        for v in violations:
            group = v["group"]
            penalty = v["penalty"]
            if group not in grouped_penalties or penalty > grouped_penalties[group]:
                grouped_penalties[group] = penalty

        total_penalty = sum(grouped_penalties.values())
        discipline_score = max(0, 100 - total_penalty)

        if discipline_score >= 80:
            discipline_risk = "Low"
        elif discipline_score >= 60:
            discipline_risk = "Medium"
        else:
            discipline_risk = "High"

        # Determine if should cooldown
        should_cooldown = False
        if fomo_score >= 8 or revenge_score >= 8 or panic_score >= 8:
            should_cooldown = True
        if any(v["severity"] == "critical" for v in violations):
            should_cooldown = True
        if any(v["rule_type"] == "dangerous_keywords" for v in violations):
            should_cooldown = True
        if any(v.get("should_cooldown", False) for v in violations):
            should_cooldown = True

        return {
            "violations": violations,
            "discipline_score": discipline_score,
            "discipline_risk": discipline_risk,
            "should_cooldown": should_cooldown
        }
