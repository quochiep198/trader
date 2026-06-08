import os
from dotenv import load_dotenv

# Load env variables before importing app
os.environ["PYTHONPATH"] = "d:/Traider/backend"
load_dotenv("d:/Traider/backend/.env")

from app.core.database import SessionLocal
from app.models.market_snapshot import MarketSnapshot
from app.models.market_context_log import MarketContextLog

def inspect_recent_entries():
    db = SessionLocal()
    try:
        print("Recent 10 Market Snapshots:")
        snaps = db.query(MarketSnapshot).order_by(MarketSnapshot.created_at.desc()).limit(10).all()
        for s in snaps:
            print(f"ID: {s.id} | Symbol: {s.symbol} | Price: {s.current_price} | Date: {s.session_date} | Created At: {s.created_at}")
            
        print("\nRecent 10 Market Context Logs:")
        logs = db.query(MarketContextLog).order_by(MarketContextLog.created_at.desc()).limit(10).all()
        for l in logs:
            print(f"ID: {l.id} | Symbol: {l.symbol} | Action: {l.action} | Price Change 1D: {l.price_change_1d} | Risk: {l.market_context_risk} | Warnings: {l.market_warnings} | Created At: {l.created_at}")
            
    except Exception as e:
        print("Error querying database:", e)
    finally:
        db.close()

if __name__ == "__main__":
    inspect_recent_entries()
