import random
import time

import requests

from src.simulator.simulator_config import cfg


def generate_random_transaction():
    return {
        "ratio_to_median_purchase_price": round(random.uniform(0.5, 8.0), 3),
        "distance_from_home": round(random.uniform(1, 3000), 2),
        "transaction_amount": round(random.uniform(5, 1200), 2),
    }


def stream_random_transactions(n=20):
    print("🎲 Starting random transaction generator...")
    url = cfg.backend_http

    for _ in range(n):
        tx = {"features": generate_random_transaction()}
        try:
            res = requests.post(url, json=tx)
            print("Sent:", tx)
            print("Received:", res.json())
        except Exception as e:
            print("Error:", e)

        time.sleep(cfg.delay_seconds)

    print("🎉 Random simulation complete!")
