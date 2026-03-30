from pathlib import Path


class SimConfig:
    # I store the backend addresses here so every simulator file can import one shared config.
    backend_http = "http://127.0.0.1:8000/transaction/predict"
    backend_ws = "ws://127.0.0.1:8000/ws/transactions"

    # I build paths from this file location so the simulator still works when the project is moved.
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"
    card_csv = data_dir / "raw" / "transactions" / "card_transdata.csv"

    # I keep the delay in config so I can slow down or speed up the demo without editing logic files.
    delay_seconds = 0.5


cfg = SimConfig()
