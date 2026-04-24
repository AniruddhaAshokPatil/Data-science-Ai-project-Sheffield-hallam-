import logging
import os

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)

# I keep the file paths at the top because this script only does one job:
# it reads the cleaned transaction data and adds a few extra columns.
INPUT_PATH = "data/processed/transactions/clean_main.csv"
OUTPUT_PATH = "data/processed/transactions/"

USER_COL = "sender_account"

def load_transaction_data():
    # I load the transaction file here because everything else in this script
    # depends on this cleaned and encoded dataset.
    dataframe = pd.read_csv(INPUT_PATH, low_memory=False)
    logging.info("I loaded the dataset with shape: %s", dataframe.shape)
    return dataframe


def prepare_time_column(dataframe):
    # I turn the timestamp into a real datetime value so I can sort the rows
    # in time order and build time-based behaviour features.
    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], errors="coerce")

    invalid_timestamp_count = dataframe["timestamp"].isnull().sum()
    if invalid_timestamp_count > 0:
        logging.warning("I am dropping %s rows with invalid timestamps", invalid_timestamp_count)
        dataframe = dataframe.dropna(subset=["timestamp"])

    dataframe = dataframe.sort_values(by="timestamp").copy()
    return dataframe


def check_required_columns(dataframe):
    # I check the columns early so the script fails with a clear message instead
    # of crashing later in the middle of the calculations.
    required_columns = ["timestamp", "amount", USER_COL]

    for column_name in required_columns:
        if column_name not in dataframe.columns:
            raise ValueError(f"I could not find the required column: {column_name}")


def add_velocity_feature(dataframe):
    # I create a numeric seconds column because pandas rolling time windows are
    # easier to calculate from one number than from a datetime object.
    dataframe["timestamp_seconds"] = dataframe["timestamp"].astype("int64") // 10**9

    # I count how many transactions the same sender made in the last hour.
    rolling_counts = (
        dataframe.groupby(USER_COL)
        .rolling(window=3600, on="timestamp_seconds")["amount"]
        .count()
        .reset_index(level=0, drop=True)
    )

    dataframe["velocity_1h"] = rolling_counts
    return dataframe


def add_frequency_feature(dataframe):
    # I count how many total transactions each sender has in the dataset.
    dataframe["frequency"] = dataframe.groupby(USER_COL)[USER_COL].transform("count")
    return dataframe


def add_deviation_feature(dataframe):
    # I calculate the running average from earlier transactions only.
    # I do this to avoid leaking future information into the current row.
    running_average = (
        dataframe.groupby(USER_COL)["amount"]
        .expanding()
        .mean()
        .shift(1)
        .reset_index(level=0, drop=True)
    )

    dataframe["user_mean_amount"] = running_average

    # I fill the first missing average with the overall median amount because
    # the first transaction for each sender has no earlier history.
    overall_median = dataframe["amount"].median()
    dataframe["user_mean_amount"] = dataframe["user_mean_amount"].fillna(overall_median)

    difference = dataframe["amount"] - dataframe["user_mean_amount"]
    dataframe["deviation"] = difference.abs()
    return dataframe


def add_log_amount_feature(dataframe):
    # I use log1p to make very large transaction amounts less extreme.
    dataframe["log_amount"] = np.log1p(dataframe["amount"])
    return dataframe


def save_output(dataframe):
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    # I save to a different file so I can still keep the earlier pipeline file.
    output_file = os.path.join(OUTPUT_PATH, "featured_main.csv")
    dataframe.to_csv(output_file, index=False)
    logging.info("I finished feature engineering.")
    logging.info("I saved the new file here: %s", output_file)


def main():
    dataframe = load_transaction_data()
    check_required_columns(dataframe)
    dataframe = prepare_time_column(dataframe)
    dataframe = add_velocity_feature(dataframe)
    dataframe = add_frequency_feature(dataframe)
    dataframe = add_deviation_feature(dataframe)
    dataframe = add_log_amount_feature(dataframe)

    # I remove helper columns that I only needed while calculating the features.
    dataframe = dataframe.drop(columns=["user_mean_amount", "timestamp_seconds"])
    save_output(dataframe)


if __name__ == "__main__":
    main()
