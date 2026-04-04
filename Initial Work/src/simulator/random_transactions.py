import random
import time

import requests

from src.simulator.simulator_config import cfg


def generate_random_transaction():
    # I build this fake transaction field by field so the generated data is easier to understand.
    ratio_to_median_purchase_price = round(random.uniform(0.5, 8.0), 3)
    distance_from_home = round(random.uniform(1, 3000), 2)
    transaction_amount = round(random.uniform(5, 1200), 2)

    transaction = {
        "ratio_to_median_purchase_price": ratio_to_median_purchase_price,
        "distance_from_home": distance_from_home,
        "transaction_amount": transaction_amount,
    }
    return transaction


def stream_random_transactions(n=20):
    # I use random transactions here so I can exercise the API even when I do not want to stream a CSV file.
    print("Starting random transaction generator...")
    url = cfg.backend_http

    for _ in range(n):
        random_features = generate_random_transaction()
        tx = {"features": random_features}

        try:
            res = requests.post(url, json=tx)
            print("Sent:", tx)
            print("Received:", res.json())
        except Exception as e:
            print("Error:", e)

        time.sleep(cfg.delay_seconds)

    print("Random simulation complete!")
