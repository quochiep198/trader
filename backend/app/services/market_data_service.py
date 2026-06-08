from abc import ABC, abstractmethod
import random
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, List

class MarketDataProvider(ABC):
    @abstractmethod
    async def get_snapshot(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch near-real-time snapshot of market prices and volumes for a symbol.
        """
        pass

    @abstractmethod
    async def get_ohlcv_sessions(self, symbol: str, sessions: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch historical session prices (OHLCV) for a symbol, sorted chronologically.
        """
        pass


class MockMarketDataProvider(MarketDataProvider):
    async def get_snapshot(self, symbol: str) -> Dict[str, Any]:
        symbol = symbol.strip().upper()
        # Seed deterministic random values based on symbol chars
        seed = sum(ord(c) for c in symbol)
        rng = random.Random(seed)
        
        # Base price (VND: 15,000 to 120,000)
        base_price = rng.randint(15, 120) * 1000
        
        # Simulated price trend depending on symbol
        trend_offset = 0
        if "HPG" in symbol:
            trend_offset = 5000  # Uptrend
        elif "VIC" in symbol:
            trend_offset = -6000 # Downtrend
            
        current_price = base_price + trend_offset + rng.randint(-1000, 1000)
        current_price = max(5000, current_price)  # Keep price positive
        
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vn = datetime.now(vn_tz)
        
        # Determine stale/fresh status based on trading hours (9:00 - 15:00 Mon-Fri)
        is_weekday = now_vn.weekday() < 5
        is_trading_hours = 9 <= now_vn.hour < 15
        
        data_status = "fresh"
        if not (is_weekday and is_trading_hours):
            # Outside active trading, closed session price is considered fresh
            data_status = "fresh"
            
        # Volatility index
        daily_spread = rng.randint(500, 2000)
        
        return {
            "symbol": symbol,
            "provider": "mock_provider",
            "current_price": current_price,
            "open_price": current_price - rng.randint(-500, 500),
            "high_price": current_price + daily_spread // 2,
            "low_price": current_price - daily_spread // 2,
            "close_price": current_price,
            "volume": rng.randint(1, 20) * 1000000,
            "session_date": now_vn.strftime("%Y-%m-%d"),
            "data_status": data_status,
            "fetched_at": now_vn
        }

    async def get_ohlcv_sessions(self, symbol: str, sessions: int = 20) -> List[Dict[str, Any]]:
        symbol = symbol.strip().upper()
        seed = sum(ord(c) for c in symbol)
        rng = random.Random(seed)
        
        # Get starting price from snapshot
        snap = await self.get_snapshot(symbol)
        price = snap["current_price"]
        
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        current_day = datetime.now(vn_tz)
        
        sessions_list = []
        
        # Up or down trend per day based on symbol
        daily_trend = 0
        if "HPG" in symbol:
            daily_trend = rng.randint(200, 500)  # Average daily up
        elif "VIC" in symbol:
            daily_trend = rng.randint(-600, -200) # Average daily down
        else:
            daily_trend = rng.randint(-200, 200)  # Sideways
            
        count = 0
        while count < sessions:
            # Skip weekends for trading days
            if current_day.weekday() >= 5:
                current_day -= timedelta(days=1)
                continue
                
            day_change = rng.randint(-500, 800) + daily_trend
            open_p = price - day_change
            close_p = price
            high_p = max(open_p, close_p) + rng.randint(0, 400)
            low_p = min(open_p, close_p) - rng.randint(0, 400)
            vol = rng.randint(800000, 12000000)
            
            sessions_list.append({
                "session_date": current_day.strftime("%Y-%m-%d"),
                "open": float(open_p),
                "high": float(high_p),
                "low": float(low_p),
                "close": float(close_p),
                "volume": int(vol)
            })
            
            price = open_p
            current_day -= timedelta(days=1)
            count += 1
            
        # Sort oldest to newest
        sessions_list.reverse()
        return sessions_list
