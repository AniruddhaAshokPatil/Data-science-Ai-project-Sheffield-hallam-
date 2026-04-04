import pandas as pd

from src.simulator.simulator_config import cfg


def load_transactions_from_csv(nrows=100):
    # I load only part of the CSV by default so my simulator starts quickly during demos.
    dataframe = pd.read_csv(cfg.card_csv, nrows=nrows)

    # I remove the fraud label before streaming because the API should score the data, not read the answer.
    if "is_fraud" in dataframe.columns:
        dataframe = dataframe.drop(columns=["is_fraud"])

    return dataframe
