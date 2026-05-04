import logging
import os

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# I keep the split paths at the top because this file is the stage that turns
# one prepared dataset into train/test files for the modeling part of the project.
INPUT_PATH = "data/processed/transactions/encoded_main.csv"
OUTPUT_PATH = "data/processed/transactions/"

SPLIT_RATIO = 0.8
RANDOM_SEED = 42

def load_data():
    logging.info("I am loading the dataset.")

    # I use low_memory=False because mixed CSV types can confuse pandas when it
    # guesses types in chunks, and I want one consistent read of the dataset.
    dataframe = pd.read_csv(INPUT_PATH, low_memory=False)

    if dataframe.empty:
        raise ValueError("Dataset is empty.")

    logging.info("I loaded the dataset with shape: %s", dataframe.shape)
    return dataframe


def check_required_columns(dataframe):
    # I validate these columns because a time-based split and supervised training
    # both depend on having a timestamp and a fraud target label.
    required_columns = ["timestamp", "is_fraud"]

    for column_name in required_columns:
        if column_name not in dataframe.columns:
            raise ValueError(f"Missing required column: {column_name}")


def prepare_timestamp(dataframe):
    # I convert the timestamp safely so I can sort the rows by time.
    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], errors="coerce")

    invalid_timestamp_count = dataframe["timestamp"].isnull().sum()
    if invalid_timestamp_count > 0:
        logging.warning("I found %s invalid timestamps, so I dropped those rows.", invalid_timestamp_count)
        dataframe = dataframe.dropna(subset=["timestamp"])

    return dataframe


def remove_duplicates(dataframe):
    rows_before = len(dataframe)
    dataframe = dataframe.drop_duplicates()
    rows_after = len(dataframe)
    duplicate_count = rows_before - rows_after
    logging.info("I removed %s duplicate rows.", duplicate_count)
    return dataframe


def split_dataset(dataframe):
    # I sort by time because I do not want the training data to learn from the future.
    dataframe = dataframe.sort_values(by="timestamp").copy()

    split_index = int(len(dataframe) * SPLIT_RATIO)
    train_dataframe = dataframe.iloc[:split_index].copy()
    test_dataframe = dataframe.iloc[split_index:].copy()

    logging.info("Train shape: %s", train_dataframe.shape)
    logging.info("Test shape: %s", test_dataframe.shape)
    return train_dataframe, test_dataframe


def save_split_files(train_dataframe, test_dataframe):
    # I separate features from the target because supervised models need X and y
    # as different inputs during training and evaluation.
    y_train = train_dataframe["is_fraud"]
    y_test = test_dataframe["is_fraud"]

    # I remove the label and timestamp here so training features do not leak the
    # answer or future-order information into the model.
    X_train = train_dataframe.drop(columns=["is_fraud", "timestamp"])
    X_test = test_dataframe.drop(columns=["is_fraud", "timestamp"])

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    X_train.to_csv(os.path.join(OUTPUT_PATH, "X_train.csv"), index=False)
    X_test.to_csv(os.path.join(OUTPUT_PATH, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(OUTPUT_PATH, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(OUTPUT_PATH, "y_test.csv"), index=False)

    logging.info("I finished the time-based split and saved the files successfully.")


def main():
    dataframe = load_data()
    check_required_columns(dataframe)
    dataframe = prepare_timestamp(dataframe)
    dataframe = remove_duplicates(dataframe)
    train_dataframe, test_dataframe = split_dataset(dataframe)
    save_split_files(train_dataframe, test_dataframe)


if __name__ == "__main__":
    main()
