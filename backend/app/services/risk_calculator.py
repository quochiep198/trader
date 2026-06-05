from decimal import Decimal
from typing import Optional, Dict, Any

class RiskCalculator:
    @staticmethod
    def calculate_buy_risk(
        entry_price: Decimal,
        quantity: int,
        stop_loss: Optional[Decimal],
        account_size: Decimal
    ) -> Dict[str, Any]:
        trade_value = entry_price * quantity
        if not stop_loss:
            return {
                "risk_per_share": None,
                "total_risk": None,
                "risk_percent": None,
                "trade_value": trade_value,
                "estimated_pnl_amount": None,
                "estimated_pnl_percent": None
            }
        
        risk_per_share = entry_price - stop_loss
        total_risk = risk_per_share * quantity
        risk_percent = None
        if account_size > 0:
            risk_percent = float((total_risk / account_size) * 100)

        return {
            "risk_per_share": risk_per_share,
            "total_risk": total_risk,
            "risk_percent": risk_percent,
            "trade_value": trade_value,
            "estimated_pnl_amount": None,
            "estimated_pnl_percent": None
        }

    @staticmethod
    def calculate_sell_risk(
        sell_price: Decimal,
        quantity: int,
        average_entry_price: Optional[Decimal]
    ) -> Dict[str, Any]:
        trade_value = sell_price * quantity
        if not average_entry_price or average_entry_price <= 0:
            return {
                "risk_per_share": None,
                "total_risk": None,
                "risk_percent": None,
                "trade_value": trade_value,
                "estimated_pnl_amount": None,
                "estimated_pnl_percent": None
            }

        estimated_pnl_amount = (sell_price - average_entry_price) * quantity
        estimated_pnl_percent = float(((sell_price - average_entry_price) / average_entry_price) * 100)

        return {
            "risk_per_share": None,
            "total_risk": None,
            "risk_percent": None,
            "trade_value": trade_value,
            "estimated_pnl_amount": estimated_pnl_amount,
            "estimated_pnl_percent": estimated_pnl_percent
        }
