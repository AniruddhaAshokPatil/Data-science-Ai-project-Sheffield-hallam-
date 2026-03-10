from pathlib import Path

class SimConfig:
    # Connect to your backend
    backend_http = "http://127.0.0.1:8000/transaction/predict"
    backend_ws = "ws://127.0.0.1:8000/ws/transactions"

    # Project & Data paths
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"
    card_csv = data_dir / "card_transdata.csv"

    # Speed of simulation
    delay_seconds = 0.5  # send one transaction every 0.5 sec

cfg = SimConfig()
