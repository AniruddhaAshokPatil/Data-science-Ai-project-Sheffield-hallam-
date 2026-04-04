import time

import pandas as pd
import requests

from src.simulator.simulator_config import cfg


def stream_over_http(df: pd.DataFrame):
    # I keep this function focused on HTTP only so the simulator stays easy to reason about.
    print("Starting HTTP transaction streaming...")
    url = cfg.backend_http

    for _, row in df.iterrows():
        features = row.to_dict()
        payload = {"features": features}

        try:
            response = requests.post(url, json=payload)
            print("Sent:", payload)
            print("Received:", response.json())
        except Exception as e:
            print("Error:", e)

        time.sleep(cfg.delay_seconds)

    print("HTTP streaming complete!")
