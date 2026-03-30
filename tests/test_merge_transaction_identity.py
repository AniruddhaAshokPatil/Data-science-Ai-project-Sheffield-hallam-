import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.merge_transaction_identity import merge_transaction_identity


class MergeTransactionIdentityTests(unittest.TestCase):
    def test_merges_transaction_and_identity_tables(self):
        # I build tiny CSV fixtures here because I want to prove the merge
        # logic works even though the checked-in IEEE files are empty locally.
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            transaction_csv = tmp / "train_transaction.csv"
            identity_csv = tmp / "train_identity.csv"
            merged_csv = tmp / "merged.csv"
            summary_json = tmp / "summary.json"

            pd.DataFrame(
                [
                    {"TransactionID": 1, "amount": 100.0, "isFraud": 0},
                    {"TransactionID": 2, "amount": 900.0, "isFraud": 1},
                ]
            ).to_csv(transaction_csv, index=False)

            pd.DataFrame(
                [
                    {"TransactionID": 1, "DeviceType": "mobile"},
                    {"TransactionID": 2, "DeviceType": "desktop"},
                ]
            ).to_csv(identity_csv, index=False)

            summary = merge_transaction_identity(
                transaction_input=transaction_csv,
                identity_input=identity_csv,
                output_path=merged_csv,
                summary_path=summary_json,
            )

            merged = pd.read_csv(merged_csv)
            written_summary = json.loads(summary_json.read_text())

            self.assertEqual(len(merged), 2)
            self.assertIn("DeviceType", merged.columns)
            self.assertEqual(summary["merged_rows"], 2)
            self.assertEqual(written_summary["identity_match_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
