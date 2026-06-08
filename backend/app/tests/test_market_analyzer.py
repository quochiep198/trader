import unittest
from app.services.market_context_analyzer import MarketContextAnalyzer

class TestMarketContextAnalyzer(unittest.TestCase):
    def setUp(self):
        # A list of 25 sorted mock sessions (oldest to newest)
        # We start price at 100 and increase it day by day
        self.sessions = []
        price = 100.0
        for i in range(25):
            open_p = price - 2.0
            close_p = price
            high_p = price + 1.0
            low_p = price - 3.0
            # Set volume to 1000000 generally
            self.sessions.append({
                "session_date": f"2026-05-{10+i}",
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "close": close_p,
                "volume": 1000000
            })
            price += 2.0 # daily uptrend

    def test_compute_metrics_basic(self):
        # Current price: 150.0, volume: 1500000
        # Average volume of 25 sessions is 1000000. Volume vs 20d avg = 1.5
        # sessions[-2] is close at index 23: close_1d_ago is 146.0
        # sessions[-4] is close at index 21: close_3d_ago is 142.0
        # sessions[-6] is close at index 19: close_5d_ago is 138.0
        # sessions[-21] is close at index 4: close_20d_ago is 108.0
        
        metrics = MarketContextAnalyzer.compute_metrics(
            current_price=150.0,
            volume=1500000,
            sessions=self.sessions,
            action="BUY",
            entry_price=145.0,
            stop_loss=140.0,
            take_profit=160.0
        )

        self.assertEqual(metrics["price_change_1d"], round((150.0 - 146.0) / 146.0 * 100, 2))
        self.assertEqual(metrics["price_change_3d"], round((150.0 - 142.0) / 142.0 * 100, 2))
        self.assertEqual(metrics["price_change_5d"], round((150.0 - 138.0) / 138.0 * 100, 2))
        self.assertEqual(metrics["price_change_20d"], round((150.0 - 108.0) / 108.0 * 100, 2))
        self.assertEqual(metrics["consecutive_up_sessions"], 24)  # Closes increase every day
        self.assertEqual(metrics["consecutive_down_sessions"], 0)
        self.assertEqual(metrics["volume_vs_20d_avg"], 1.5)
        self.assertEqual(metrics["current_vs_entry_percent"], round((150.0 - 145.0) / 145.0 * 100, 2))
        self.assertEqual(metrics["distance_to_stop_loss_percent"], round((150.0 - 140.0) / 150.0 * 100, 2))
        self.assertEqual(metrics["distance_to_take_profit_percent"], round((160.0 - 150.0) / 150.0 * 100, 2))

    def test_compute_metrics_sell_to_close(self):
        metrics = MarketContextAnalyzer.compute_metrics(
            current_price=150.0,
            volume=1000000,
            sessions=self.sessions,
            action="SELL_TO_CLOSE",
            average_entry_price=120.0
        )

        self.assertEqual(metrics["current_vs_entry_percent"], round((150.0 - 120.0) / 120.0 * 100, 2))
        self.assertIsNone(metrics["distance_to_stop_loss_percent"])
        self.assertIsNone(metrics["distance_to_take_profit_percent"])

    def test_warnings_market_fomo_context(self):
        # FOMO Warning triggers when (price_change_3d >= 7 or up_sessions >= 3) AND fomo_score >= 6
        metrics = {
            "price_change_3d": 8.0,
            "consecutive_up_sessions": 3,
            "consecutive_down_sessions": 0,
            "volume_vs_20d_avg": 1.0,
            "current_vs_entry_percent": 0.0,
            "distance_to_stop_loss_percent": 5.0,
            "distance_to_take_profit_percent": 5.0
        }
        
        # Scenario 1: High FOMO score -> Triggers warning
        result = MarketContextAnalyzer.generate_warnings_and_risk(
            metrics=metrics,
            emotion_scores={"fomo_score": 8, "panic_score": 0},
            data_status="fresh",
            action="BUY"
        )
        self.assertIn("market_fomo_context", result["market_warnings"])
        self.assertEqual(result["market_context_risk"], "high")

        # Scenario 2: Low FOMO score -> No warning
        result = MarketContextAnalyzer.generate_warnings_and_risk(
            metrics=metrics,
            emotion_scores={"fomo_score": 4, "panic_score": 0},
            data_status="fresh",
            action="BUY"
        )
        self.assertNotIn("market_fomo_context", result["market_warnings"])
        self.assertEqual(result["market_context_risk"], "low")

    def test_warnings_buying_chase_risk(self):
        # buying_chase_risk triggers when current_vs_entry_percent >= 3 and action = BUY
        metrics = {
            "price_change_3d": 1.0,
            "consecutive_up_sessions": 0,
            "consecutive_down_sessions": 0,
            "volume_vs_20d_avg": 1.0,
            "current_vs_entry_percent": 4.5,
            "distance_to_stop_loss_percent": 5.0,
            "distance_to_take_profit_percent": 5.0
        }

        # Scenario 1: Action BUY -> Triggers
        result = MarketContextAnalyzer.generate_warnings_and_risk(
            metrics=metrics,
            emotion_scores={"fomo_score": 0, "panic_score": 0},
            data_status="fresh",
            action="BUY"
        )
        self.assertIn("buying_chase_risk", result["market_warnings"])
        self.assertEqual(result["market_context_risk"], "medium")

        # Scenario 2: Action SELL_TO_CLOSE -> Does not trigger buying chase warning
        result = MarketContextAnalyzer.generate_warnings_and_risk(
            metrics=metrics,
            emotion_scores={"fomo_score": 0, "panic_score": 0},
            data_status="fresh",
            action="SELL_TO_CLOSE"
        )
        self.assertNotIn("buying_chase_risk", result["market_warnings"])

    def test_warnings_near_stop_loss_and_take_profit(self):
        # near_stop_loss triggers when 0 < dist_sl <= 2
        # near_take_profit triggers when 0 < dist_tp <= 2
        metrics = {
            "price_change_3d": 0.0,
            "consecutive_up_sessions": 0,
            "consecutive_down_sessions": 0,
            "volume_vs_20d_avg": 1.0,
            "current_vs_entry_percent": 0.0,
            "distance_to_stop_loss_percent": 1.5,
            "distance_to_take_profit_percent": 1.8
        }

        result = MarketContextAnalyzer.generate_warnings_and_risk(
            metrics=metrics,
            emotion_scores={"fomo_score": 0, "panic_score": 0},
            data_status="fresh",
            action="BUY"
        )
        self.assertIn("near_stop_loss", result["market_warnings"])
        self.assertIn("near_take_profit", result["market_warnings"])
        self.assertEqual(result["market_context_risk"], "medium")

    def test_warnings_data_fallbacks(self):
        # Stale data -> Warning but no high risk by default
        metrics = {
            "price_change_3d": 0.0,
            "consecutive_up_sessions": 0,
            "consecutive_down_sessions": 0,
            "volume_vs_20d_avg": 1.0,
            "current_vs_entry_percent": 0.0,
            "distance_to_stop_loss_percent": 5.0,
            "distance_to_take_profit_percent": 5.0
        }

        result_stale = MarketContextAnalyzer.generate_warnings_and_risk(
            metrics=metrics,
            emotion_scores={"fomo_score": 0, "panic_score": 0},
            data_status="stale",
            action="BUY"
        )
        self.assertIn("stale_market_data", result_stale["market_warnings"])
        self.assertEqual(result_stale["market_context_risk"], "low")

        # Unavailable data -> Skips warnings, returns unavailable warning and low risk
        result_unavail = MarketContextAnalyzer.generate_warnings_and_risk(
            metrics=metrics,
            emotion_scores={"fomo_score": 0, "panic_score": 0},
            data_status="unavailable",
            action="BUY"
        )
        self.assertIn("unavailable_market_data", result_unavail["market_warnings"])
        self.assertEqual(len(result_unavail["market_warnings"]), 1)
        self.assertEqual(result_unavail["market_context_risk"], "low")

if __name__ == "__main__":
    unittest.main()
