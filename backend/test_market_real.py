import asyncio
import os
from dotenv import load_dotenv

# Load env variables before importing app
os.environ["PYTHONPATH"] = "d:/Traider/backend"
load_dotenv("d:/Traider/backend/.env")

from app.core.database import SessionLocal, engine
from app.services.market_data_service import MockMarketDataProvider
from app.services.market_context_analyzer import MarketContextAnalyzer
from app.models.market_snapshot import MarketSnapshot
from app.models.user import User

async def run_real_db_test():
    db = SessionLocal()
    market_provider = MockMarketDataProvider()
    symbol = "HPG"
    
    try:
        # Check if user table can be queried
        user = db.query(User).first()
        if user:
            print(f"Connected to DB successfully. Found user: {user.email}")
        else:
            print("Connected to DB successfully. No users found.")
            
        print(f"Fetching mock snapshot for {symbol}...")
        snapshot = await market_provider.get_snapshot(symbol)
        sessions = await market_provider.get_ohlcv_sessions(symbol, sessions=20)
        
        print(f"Calculating metrics for {symbol}...")
        metrics = MarketContextAnalyzer.compute_metrics(
            current_price=snapshot["current_price"],
            volume=snapshot["volume"],
            sessions=sessions,
            action="BUY"
        )
        
        print("Caching snapshot in real database...")
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
        print("Successfully cached snapshot in DB!")
        
        # Verify it is stored
        stored = db.query(MarketSnapshot).filter_by(symbol=symbol).order_by(MarketSnapshot.created_at.desc()).first()
        if stored:
            print(f"Verified stored snapshot! ID: {stored.id}, Price: {stored.current_price}, Fetched At: {stored.fetched_at}")
            
    except Exception as e:
        print("An error occurred during real DB market check:")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_real_db_test())
