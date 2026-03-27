import pandas as pd

from src.simulator.simulator_config import cfg


def load_transactions_from_csv(nrows=100):
    df = pd.read_csv(cfg.card_csv, nrows=nrows)
    # Remove label column if present
    if "is_fraud" in df.columns:
        df = df.drop(columns=["is_fraud"])
    return df
