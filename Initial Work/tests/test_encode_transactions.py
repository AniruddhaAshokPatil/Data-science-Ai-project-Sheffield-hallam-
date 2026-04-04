import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

# I add the project root to sys.path so this test file can import project code
# when I run it directly from the repository without extra environment setup.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.encode_transactions import encode_transactions


class EncodeTransactionsTests(unittest.TestCase):
    def test_encodes_main_and_validation_with_shared_schema_and_metadata(self):
        # I use a temporary directory here so the test can create input and
        # output files safely without touching the real project datasets.
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            main_input = tmp / "clean_main.csv"
            validation_input = tmp / "clean_validation.csv"
            main_output = tmp / "encoded_main.csv"
            validation_output = tmp / "encoded_validation.csv"
            metadata_output = tmp / "encoded_schema.json"

            # I build a small mock "main" dataset here because I want to test
            # the same column types the real project may contain.
            pd.DataFrame(
                [
                    {
                        "transaction_id": "tx-1",
                        "timestamp": "2024-01-01 12:00:00",
                        "sender_account": "alice",
                        "receiver_account": "merchant",
                        "transaction_type": "card",
                        "merchant_category": "grocery",
                        "device_used": "mobile",
                        "ip_address": "1.1.1.1",
                        "device_hash": "abc",
                        "amount": 50.5,
                        "is_fraud": 1,
                    },
                    {
                        "transaction_id": "tx-2",
                        "timestamp": "2024-01-02 12:00:00",
                        "sender_account": "bob",
                        "receiver_account": "merchant",
                        "transaction_type": "bank",
                        "merchant_category": "travel",
                        "device_used": "web",
                        "ip_address": "2.2.2.2",
                        "device_hash": "def",
                        "amount": 70.0,
                        "is_fraud": 0,
                    },
                ]
            ).to_csv(main_input, index=False)

            # I build a second mock validation dataset here because the whole
            # purpose of the encoder is to align both datasets to one schema.
            pd.DataFrame(
                [
                    {
                        "distance_from_home": 10.0,
                        "online_order": 1,
                        "timestamp": "2024-01-03 08:30:00",
                        "used_chip": 0,
                        "fraud": 1,
                    },
                    {
                        "distance_from_home": 20.0,
                        "online_order": 0,
                        "timestamp": "2024-01-04 08:30:00",
                        "used_chip": 1,
                        "fraud": 0,
                    },
                ]
            ).to_csv(validation_input, index=False)

            # I call the real encoder here because this is an integration-style
            # test for the transaction feature encoding stage.
            result = encode_transactions(
                main_input=main_input,
                validation_input=validation_input,
                main_output=main_output,
                validation_output=validation_output,
                metadata_output=metadata_output,
            )

            encoded_main = pd.read_csv(main_output)
            encoded_validation = pd.read_csv(validation_output)
            metadata = json.loads(metadata_output.read_text())

            # I check schema alignment first because both datasets must end up
            # with identical feature columns before model training can work.
            self.assertEqual(list(encoded_main.columns), list(encoded_validation.columns))
            self.assertEqual(result["feature_columns"], metadata["feature_columns"])
            self.assertEqual(encoded_main.columns[-1], "is_fraud")
            self.assertEqual(encoded_validation.columns[-1], "is_fraud")
            self.assertNotIn("transaction_id", encoded_main.columns)
            self.assertNotIn("sender_account", encoded_main.columns)
            self.assertNotIn("receiver_account", encoded_main.columns)
            self.assertNotIn("ip_address", encoded_main.columns)
            self.assertNotIn("device_hash", encoded_main.columns)
            self.assertIn("timestamp", encoded_main.columns)
            self.assertTrue(pd.api.types.is_integer_dtype(encoded_main["timestamp"]))
            self.assertTrue(pd.api.types.is_integer_dtype(encoded_validation["timestamp"]))
            self.assertIn("transaction_type_bank", encoded_main.columns)
            self.assertIn("transaction_type_card", encoded_main.columns)
            self.assertEqual(metadata["target_column"], "is_fraud")


if __name__ == "__main__":
    unittest.main()
