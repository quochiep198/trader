import os
import requests
from dotenv import load_dotenv

# Load env variables
os.environ["PYTHONPATH"] = "d:/Traider/backend"
load_dotenv("d:/Traider/backend/.env")

from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User

def test_api():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No users found in database.")
            return
            
        print(f"Generating access token for user: {user.email} (ID: {user.id})")
        token = create_access_token(subject=str(user.id))
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = "http://127.0.0.1:8000/api/v1/trade-check/market/snapshot"
        print(f"Calling GET {url} for HPG...")
        resp = requests.get(url, params={"symbol": "HPG"}, headers=headers)
        
        print(f"Status Code: {resp.status_code}")
        print("Response headers:")
        print(resp.headers)
        print("Response JSON:")
        print(resp.json())
        
    except Exception as e:
        print("Error testing API:", e)
    finally:
        db.close()

if __name__ == "__main__":
    test_api()
