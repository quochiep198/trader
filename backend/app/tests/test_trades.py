import unittest
import os
import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set database URL to a test SQLite database before importing database setup
os.environ["DATABASE_URL"] = "sqlite:///./test_trades.db"

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.rule import Rule
from app.models.emotion_log import EmotionLog

# Setup SQLite test engine and SessionLocal
TEST_DATABASE_URL = "sqlite:///./test_trades.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestTradesCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_trades.db"):
            try:
                os.remove("./test_trades.db")
            except OSError:
                pass

    def setUp(self):
        # Clear database records between tests
        db = TestingSessionLocal()
        db.query(EmotionLog).delete()
        db.query(Rule).delete()
        db.query(User).delete()
        db.commit()
        db.close()

        # Register and login a default user
        reg_payload = {
            "email": "trader@example.com",
            "password": "Password123",
            "name": "Discipline Trader"
        }
        self.client.post("/api/v1/auth/register", json=reg_payload)

        # Login
        login_payload = {
            "email": "trader@example.com",
            "password": "Password123"
        }
        res_login = self.client.post("/api/v1/auth/login", json=login_payload)
        self.token = res_login.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Update account_size of default user to 100000.00 to prevent oversized trade rules on normal testing
        db = TestingSessionLocal()
        user = db.query(User).filter(User.email == "trader@example.com").first()
        user.account_size = 100000.00
        db.commit()
        db.close()

    @patch('app.services.ai_service.AIService.analyze_emotion')
    def test_buy_order_rr_calculation(self, mock_analyze):
        mock_analyze.return_value = {
            "emotion_tags": ["Calm"],
            "fomo_score": 2,
            "panic_score": 1,
            "revenge_score": 0,
            "overconfidence_score": 2,
            "greed_score": 1,
            "hesitation_score": 2,
            "discipline_risk": "low",
            "should_cooldown": False,
            "reason": "Clear breakout setup on HPG",
            "coach_message": "Lệnh giao dịch tuân thủ tốt kỷ luật.",
            "reflection_question": None
        }

        # Valid BUY request
        payload = {
            "symbol": "HPG",
            "action": "BUY",
            "entry_price": 28000,
            "quantity": 100,
            "stop_loss": 27000,
            "take_profit": 31000,
            "reason": "Breakout HPG daily chart with high volume",
            "emotion_text": "I feel calm and focused, not chasing the price.",
            "confidence_level": 8
        }

        res = self.client.post("/api/v1/trade-check", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        # Verify Risk Calculator output
        risk = data["risk_calculation"]
        self.assertEqual(float(risk["risk_per_share"]), 1000)
        self.assertEqual(float(risk["total_risk"]), 100000)
        # account_size is 100000.00, total_risk is 100000, risk_percent is 100%
        self.assertEqual(risk["risk_percent"], 100.0)

        # Invalid BUY (stop_loss >= entry_price) -> returns 422 from Pydantic validator
        invalid_payload = payload.copy()
        invalid_payload["stop_loss"] = 29000
        res_invalid = self.client.post("/api/v1/trade-check", json=invalid_payload, headers=self.headers)
        self.assertEqual(res_invalid.status_code, 422)

    @patch('app.services.ai_service.AIService.analyze_emotion')
    def test_sell_order_no_sl_tp(self, mock_analyze):
        mock_analyze.return_value = {
            "emotion_tags": ["Calm"],
            "fomo_score": 1,
            "panic_score": 1,
            "revenge_score": 0,
            "overconfidence_score": 1,
            "greed_score": 1,
            "hesitation_score": 1,
            "discipline_risk": "low",
            "should_cooldown": False,
            "reason": "Hit target on HPG",
            "coach_message": "Chốt lời đúng kỷ luật.",
            "reflection_question": None
        }

        # Valid SELL_TO_CLOSE request without SL/TP
        payload = {
            "symbol": "HPG",
            "action": "SELL_TO_CLOSE",
            "sell_price": 31000,
            "quantity": 100,
            "average_entry_price": 28000,
            "reason": "Target hit, selling to realize profits.",
            "emotion_text": "I feel happy and satisfied.",
            "confidence_level": 9
        }

        res = self.client.post("/api/v1/trade-check", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        # Verify estimated P/L in risk calculation
        risk = data["risk_calculation"]
        self.assertEqual(float(risk["estimated_pnl_amount"]), 300000) # (31000 - 28000) * 100
        self.assertAlmostEqual(risk["estimated_pnl_percent"], 10.7142857) # (3000 / 28000) * 100

    @patch('app.services.ai_service.AIService.analyze_emotion')
    def test_ai_timeout_fallback(self, mock_analyze):
        # Simulate AI timeout/failure by returning None
        mock_analyze.return_value = None

        # Small BUY to avoid triggering rule engine cooldowns (like oversized trade condition)
        payload = {
            "symbol": "HPG",
            "action": "BUY",
            "entry_price": 100,
            "quantity": 1,
            "stop_loss": 99,
            "take_profit": 110,
            "reason": "Simple valid setup",
            "emotion_text": "I am calm and happy.",
            "confidence_level": 7
        }

        res = self.client.post("/api/v1/trade-check", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        # Verify fallback values
        self.assertEqual(data["emotion_scores"]["fomo_score"], 0)
        self.assertEqual(data["emotion_scores"]["revenge_score"], 0)
        self.assertEqual(data["emotion_tags"], ["Neutral"])
        self.assertIn("Hệ thống không thể phân tích cảm xúc", data["coach_message"])
        self.assertFalse(data["should_cooldown"])
        # Risk calculator math is still processed normally
        self.assertEqual(float(data["risk_calculation"]["risk_per_share"]), 1)

    @patch('app.services.ai_service.AIService.analyze_emotion')
    def test_cooldown_locking_and_acknowledgement(self, mock_analyze):
        # Mock AI to trigger cooldown (e.g. revenge trading score = 9)
        mock_analyze.return_value = {
            "emotion_tags": ["Revenge"],
            "fomo_score": 1,
            "panic_score": 1,
            "revenge_score": 9,
            "overconfidence_score": 1,
            "greed_score": 3,
            "hesitation_score": 2,
            "discipline_risk": "high",
            "should_cooldown": True,
            "reason": "Aggressive revenge entry",
            "coach_message": "Cảnh báo phục thù giao dịch!",
            "reflection_question": "Tại sao bạn lại nôn nóng gỡ lỗ?"
        }

        payload = {
            "symbol": "HPG",
            "action": "BUY",
            "entry_price": 28000,
            "quantity": 100,
            "stop_loss": 27000,
            "take_profit": 31000,
            "reason": "Vừa lỗ lệnh trước nên mua ngay để gỡ",
            "emotion_text": "Muốn mua gỡ lỗ ngay lập tức.",
            "confidence_level": 6
        }

        res = self.client.post("/api/v1/trade-check", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        log_id = data["log_id"]
        self.assertTrue(data["should_cooldown"])
        self.assertEqual(data["intervention"]["reflection_question"], "Tại sao bạn lại nôn nóng gỡ lỗ?")

        # Try to acknowledge with < 10 characters -> returns 422
        ack_payload_short = {"reflective_answer": "Short"}
        res_ack_short = self.client.post(
            f"/api/v1/trade-check/{log_id}/acknowledge",
            json=ack_payload_short,
            headers=self.headers
        )
        self.assertEqual(res_ack_short.status_code, 422)

        # Acknowledge with >= 10 characters -> returns 200
        ack_payload_valid = {"reflective_answer": "Tôi sẽ đợi tín hiệu thị trường rõ ràng hơn."}
        res_ack = self.client.post(
            f"/api/v1/trade-check/{log_id}/acknowledge",
            json=ack_payload_valid,
            headers=self.headers
        )
        self.assertEqual(res_ack.status_code, 200)
        self.assertTrue(res_ack.json()["success"])

        # Check DB that log was updated
        db = TestingSessionLocal()
        log = db.query(EmotionLog).filter(EmotionLog.id == uuid.UUID(log_id)).first()
        self.assertTrue(log.cooldown_acknowledged)
        self.assertEqual(log.reflective_answer, "Tôi sẽ đợi tín hiệu thị trường rõ ràng hơn.")
        db.close()
