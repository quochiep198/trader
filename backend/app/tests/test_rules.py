import unittest
import os
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set database URL to a test SQLite database before importing database setup
os.environ["DATABASE_URL"] = "sqlite:///./test_sql_app.db"

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.rule import Rule

# Setup SQLite test engine and SessionLocal
TEST_DATABASE_URL = "sqlite:///./test_sql_app.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestTradingRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create all tables in the test database
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Drop all tables and clean up test file
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_sql_app.db"):
            try:
                os.remove("./test_sql_app.db")
            except OSError:
                pass

    def setUp(self):
        # Clear database records between tests
        db = TestingSessionLocal()
        db.query(Rule).delete()
        db.query(User).delete()
        db.commit()
        db.close()

    def test_rule_seeding_on_registration(self):
        # Register a new user
        reg_payload = {
            "email": "test_seeding@example.com",
            "password": "Password123",
            "name": "Test Seeding User"
        }
        res_reg = self.client.post("/api/v1/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 200)

        # Login to get JWT token
        login_payload = {
            "email": "test_seeding@example.com",
            "password": "Password123"
        }
        res_login = self.client.post("/api/v1/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check default rules in DB
        res_rules = self.client.get("/api/v1/rules/", headers=headers)
        self.assertEqual(res_rules.status_code, 200)
        rules = res_rules.json()

        # Should seed exactly 7 default rules
        self.assertEqual(len(rules), 7)

        # Map type to active status & value
        rules_map = {r["rule_type"]: r for r in rules}
        
        self.assertTrue(rules_map["require_stop_loss"]["is_active"])
        self.assertEqual(rules_map["require_stop_loss"]["rule_value"], "yes")

        self.assertTrue(rules_map["max_risk_per_trade"]["is_active"])
        self.assertEqual(rules_map["max_risk_per_trade"]["rule_value"], "2%")

        self.assertTrue(rules_map["max_consecutive_losses"]["is_active"])
        self.assertEqual(rules_map["max_consecutive_losses"]["rule_value"], "3")

        self.assertTrue(rules_map["max_fomo_score"]["is_active"])
        self.assertEqual(rules_map["max_fomo_score"]["rule_value"], "7")

        self.assertFalse(rules_map["max_trades_per_day"]["is_active"])
        self.assertEqual(rules_map["max_trades_per_day"]["rule_value"], "5")

        self.assertFalse(rules_map["cooldown_after_loss"]["is_active"])
        self.assertEqual(rules_map["cooldown_after_loss"]["rule_value"], "24")

        self.assertTrue(rules_map["prevent_oversized_trade"]["is_active"])
        self.assertEqual(rules_map["prevent_oversized_trade"]["rule_value"], "-15")

    def test_rule_value_validation_limits(self):
        # Register and login
        self.client.post("/api/v1/auth/register", json={
            "email": "test_limits@example.com",
            "password": "Password123",
            "name": "Test Limits User"
        })
        res_login = self.client.post("/api/v1/auth/login", json={
            "email": "test_limits@example.com",
            "password": "Password123"
        })
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get the seeded rules
        res_rules = self.client.get("/api/v1/rules/", headers=headers)
        rules = res_rules.json()
        rules_map = {r["rule_type"]: r for r in rules}

        # 1. Test max_risk_per_trade bounds (0 < risk < 100)
        risk_rule_id = rules_map["max_risk_per_trade"]["id"]
        
        # Test negative value -> Fail
        res = self.client.put(f"/api/v1/rules/{risk_rule_id}/value", json={"rule_value": "-1"}, headers=headers)
        self.assertEqual(res.status_code, 400)
        
        # Test zero value -> Fail
        res = self.client.put(f"/api/v1/rules/{risk_rule_id}/value", json={"rule_value": "0"}, headers=headers)
        self.assertEqual(res.status_code, 400)

        # Test exceeding 100 -> Fail
        res = self.client.put(f"/api/v1/rules/{risk_rule_id}/value", json={"rule_value": "100"}, headers=headers)
        self.assertEqual(res.status_code, 400)

        # Test valid value -> Success
        res = self.client.put(f"/api/v1/rules/{risk_rule_id}/value", json={"rule_value": "1.5"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["rule"]["rule_value"], "1.5%")

        # 2. Test max_consecutive_losses bounds (integer > 0)
        loss_rule_id = rules_map["max_consecutive_losses"]["id"]
        
        # Test zero -> Fail
        res = self.client.put(f"/api/v1/rules/{loss_rule_id}/value", json={"rule_value": "0"}, headers=headers)
        self.assertEqual(res.status_code, 400)

        # Test float -> Fail
        res = self.client.put(f"/api/v1/rules/{loss_rule_id}/value", json={"rule_value": "2.5"}, headers=headers)
        self.assertEqual(res.status_code, 400)

        # Test valid -> Success
        res = self.client.put(f"/api/v1/rules/{loss_rule_id}/value", json={"rule_value": "5"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["rule"]["rule_value"], "5")

        # 3. Test max_fomo_score bounds (1 <= fomo <= 10)
        fomo_rule_id = rules_map["max_fomo_score"]["id"]

        # Test zero -> Fail
        res = self.client.put(f"/api/v1/rules/{fomo_rule_id}/value", json={"rule_value": "0"}, headers=headers)
        self.assertEqual(res.status_code, 400)

        # Test 11 -> Fail
        res = self.client.put(f"/api/v1/rules/{fomo_rule_id}/value", json={"rule_value": "11"}, headers=headers)
        self.assertEqual(res.status_code, 400)

        # Test valid -> Success
        res = self.client.put(f"/api/v1/rules/{fomo_rule_id}/value", json={"rule_value": "8"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["rule"]["rule_value"], "8")

    def test_rule_toggle_behavior(self):
        # Register and login
        self.client.post("/api/v1/auth/register", json={
            "email": "test_toggle@example.com",
            "password": "Password123",
            "name": "Test Toggle User"
        })
        res_login = self.client.post("/api/v1/auth/login", json={
            "email": "test_toggle@example.com",
            "password": "Password123"
        })
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get seeded rules
        res_rules = self.client.get("/api/v1/rules/", headers=headers)
        rules = res_rules.json()
        rule = rules[0]
        rule_id = rule["id"]
        original_status = rule["is_active"]

        # Toggle the rule
        res_toggle = self.client.put(f"/api/v1/rules/{rule_id}/toggle", headers=headers)
        self.assertEqual(res_toggle.status_code, 200)
        self.assertEqual(res_toggle.json()["is_active"], not original_status)

        # Toggle back
        res_toggle_back = self.client.put(f"/api/v1/rules/{rule_id}/toggle", headers=headers)
        self.assertEqual(res_toggle_back.status_code, 200)
        self.assertEqual(res_toggle_back.json()["is_active"], original_status)

    def test_rule_isolation(self):
        # Create User A
        self.client.post("/api/v1/auth/register", json={
            "email": "usera@example.com",
            "password": "Password123",
            "name": "User A"
        })
        res_login_a = self.client.post("/api/v1/auth/login", json={
            "email": "usera@example.com",
            "password": "Password123"
        })
        token_a = res_login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Create User B
        self.client.post("/api/v1/auth/register", json={
            "email": "userb@example.com",
            "password": "Password123",
            "name": "User B"
        })
        res_login_b = self.client.post("/api/v1/auth/login", json={
            "email": "userb@example.com",
            "password": "Password123"
        })
        token_b = res_login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User A gets their rules
        res_rules_a = self.client.get("/api/v1/rules/", headers=headers_a)
        rule_a_id = res_rules_a.json()[0]["id"]

        # User B tries to toggle User A's rule -> Should return 404 (or 403)
        res_toggle_malicious = self.client.put(f"/api/v1/rules/{rule_a_id}/toggle", headers=headers_b)
        self.assertEqual(res_toggle_malicious.status_code, 404)

        # User B tries to update User A's rule value -> Should return 404 (or 403)
        res_value_malicious = self.client.put(
            f"/api/v1/rules/{rule_a_id}/value", 
            json={"rule_value": "1.5"}, 
            headers=headers_b
        )
        self.assertEqual(res_value_malicious.status_code, 404)

    def test_rule_lazy_seeding_for_existing_user(self):
        # 1. Register a new user
        self.client.post("/api/v1/auth/register", json={
            "email": "test_lazy@example.com",
            "password": "Password123",
            "name": "Test Lazy User"
        })
        
        # Login
        res_login = self.client.post("/api/v1/auth/login", json={
            "email": "test_lazy@example.com",
            "password": "Password123"
        })
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Delete their seeded rules to simulate pre-existing user
        db = TestingSessionLocal()
        user_obj = db.query(User).filter(User.email == "test_lazy@example.com").first()
        db.query(Rule).filter(Rule.user_id == user_obj.id).delete()
        db.commit()
        
        # Verify they have 0 rules
        rules_count = db.query(Rule).filter(Rule.user_id == user_obj.id).count()
        self.assertEqual(rules_count, 0)
        db.close()
        
        # 3. Call GET rules -> Trigger lazy seeding
        res_rules = self.client.get("/api/v1/rules/", headers=headers)
        self.assertEqual(res_rules.status_code, 200)
        rules = res_rules.json()
        self.assertEqual(len(rules), 7)
        
        # Verify DB persistence
        db = TestingSessionLocal()
        rules_count_after = db.query(Rule).filter(Rule.user_id == user_obj.id).count()
        self.assertEqual(rules_count_after, 7)
        db.close()

if __name__ == "__main__":
    unittest.main()
