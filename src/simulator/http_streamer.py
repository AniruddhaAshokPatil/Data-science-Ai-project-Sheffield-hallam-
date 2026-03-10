import time
import requests
import pandas as pd
from simulator.simulator_config import cfg


def stream_over_http(df: pd.DataFrame):
    print("🚀 Starting HTTP transaction streaming...")
    url = cfg.backend_http

    for _, row in df.iterrows():
        payload = {"features": row.to_dict()}
        try:
            response = requests.post(url, json=payload)
            print("Sent →", payload)
            print("Received ←", response.json())
        except Exception as e:
            print("Error:", e)

        time.sleep(cfg.delay_seconds)

    print("✅ HTTP streaming complete!")

