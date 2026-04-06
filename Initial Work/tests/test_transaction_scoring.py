import sys
import unittest
from pathlib import Path


# I add the project root to sys.path here so I can run this test file directly
# and still import the transaction scoring logic from the project package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api.routers.transactions import score_transaction_features


class TransactionScoringTests(unittest.TestCase):
    def test_card_feature_payload_uses_card_signals(self):
        # I test the card-style payload separately because the transaction
        # scorer now supports more than one feature profile.
        result = score_transaction_features(
            {
                "ratio_to_median_purchase_price": 3.0,
                "distance_from_home": 250.0,
                "online_order": 1.0,
            }
        )

        self.assertGreater(result.risk, 0.0)
        self.assertIn("ratio_norm", result.details)
        self.assertIn("dist_norm", result.details)
        self.assertEqual(result.details["feature_profile"], 1.0)

    def test_financial_feature_payload_uses_financial_signals(self):
        # I test the financial-style payload too because I want to prove the
        # newer scoring branch does not fall back to zero anymore.
        result = score_transaction_features(
            {
                "amount": 900.0,
                "spending_deviation_score": 1.8,
                "velocity_score": 16.0,
                "geo_anomaly_score": 0.9,
            }
        )

        self.assertGreater(result.risk, 0.0)
        self.assertIn("amount_norm", result.details)
        self.assertIn("spending_dev_norm", result.details)
        self.assertIn("velocity_norm", result.details)
        self.assertIn("geo_norm", result.details)
        self.assertEqual(result.details["feature_profile"], 2.0)
        self.assertGreater(result.details["tabular_prob"], 0.0)
        self.assertEqual(result.profile, "financial")

    def test_card_payload_reports_profile_name_and_threshold(self):
        # I verify the response metadata here because production clients often
        # need a little context alongside the final risk value.
        result = score_transaction_features(
            {
                "ratio_to_median_purchase_price": 2.5,
                "distance_from_home": 100.0,
            }
        )

        self.assertEqual(result.profile, "card")
        self.assertIn("threshold", result.details)


if __name__ == "__main__":
    unittest.main()
