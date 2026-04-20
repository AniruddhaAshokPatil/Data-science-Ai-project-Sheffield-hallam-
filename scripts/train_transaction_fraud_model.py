import json
import os
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score


# I keep the main project paths here so I can see everything in one place.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_TRANSACTION_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "transactions")
MODEL_DIR = os.path.join(PROJECT_ROOT, "backend", "saved_models")

MAIN_DATASET_PATH = os.path.join(PROCESSED_TRANSACTION_DIR, "clean_main.csv")
CARD_DATASET_PATH = os.path.join(PROCESSED_TRANSACTION_DIR, "clean_validation.csv")

MAX_MAIN_ROWS = 50000


def load_main_transaction_data():
    # I keep a row limit here because the main transaction file is very large.
    return pd.read_csv(MAIN_DATASET_PATH, nrows=MAX_MAIN_ROWS, low_memory=False)


def load_card_transaction_data():
    return pd.read_csv(CARD_DATASET_PATH, low_memory=False)


def prepare_target(dataframe):
    # I make the target easy to work with before I do anything else.
    target_values = dataframe["is_fraud"].astype(str).str.strip().str.lower()
    target_values = target_values.replace({"true": 1, "false": 0, "yes": 1, "no": 0})
    dataframe["is_fraud"] = pd.to_numeric(target_values, errors="coerce")
    dataframe = dataframe.dropna(subset=["is_fraud"]).copy()
    dataframe["is_fraud"] = dataframe["is_fraud"].astype(int)
    return dataframe


def prepare_main_dataset(dataframe):
    # I use this path for the richer transaction behaviour dataset.
    dataframe = prepare_target(dataframe)
    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], errors="coerce")
    dataframe = dataframe.dropna(subset=["timestamp"]).copy()
    dataframe = dataframe.sort_values("timestamp").reset_index(drop=True)

    selected_columns = [
        "timestamp",
        "amount",
        "transaction_type",
        "merchant_category",
        "location",
        "device_used",
        "time_since_last_transaction",
        "spending_deviation_score",
        "velocity_score",
        "geo_anomaly_score",
        "payment_channel",
        "is_fraud",
    ]

    dataframe = dataframe[selected_columns].copy()

    numeric_columns = [
        "amount",
        "time_since_last_transaction",
        "spending_deviation_score",
        "velocity_score",
        "geo_anomaly_score",
    ]
    text_columns = [
        "transaction_type",
        "merchant_category",
        "location",
        "device_used",
        "payment_channel",
    ]

    for column_name in numeric_columns:
        dataframe[column_name] = pd.to_numeric(dataframe[column_name], errors="coerce")
        dataframe[column_name] = dataframe[column_name].fillna(dataframe[column_name].median())

    for column_name in text_columns:
        dataframe[column_name] = dataframe[column_name].fillna("missing").astype(str)

    dataframe["hour"] = dataframe["timestamp"].dt.hour
    dataframe["day_of_week"] = dataframe["timestamp"].dt.dayofweek
    dataframe["month"] = dataframe["timestamp"].dt.month

    return dataframe


def prepare_card_dataset(dataframe):
    # I use this path for the card purchase dataset.
    dataframe = prepare_target(dataframe)

    selected_columns = [
        "distance_from_home",
        "distance_from_last_transaction",
        "ratio_to_median_purchase_price",
        "repeat_retailer",
        "used_chip",
        "used_pin_number",
        "online_order",
        "is_fraud",
    ]

    dataframe = dataframe[selected_columns].copy()

    for column_name in selected_columns:
        if column_name == "is_fraud":
            continue
        dataframe[column_name] = pd.to_numeric(dataframe[column_name], errors="coerce")
        dataframe[column_name] = dataframe[column_name].fillna(dataframe[column_name].median())

    return dataframe


def split_main_dataset(dataframe):
    split_index = int(len(dataframe) * 0.8)
    train_dataframe = dataframe.iloc[:split_index].copy()
    test_dataframe = dataframe.iloc[split_index:].copy()
    return train_dataframe, test_dataframe


def split_card_dataset(dataframe):
    # I use a simple split here because this dataset does not have a timestamp column.
    split_index = int(len(dataframe) * 0.8)
    train_dataframe = dataframe.iloc[:split_index].copy()
    test_dataframe = dataframe.iloc[split_index:].copy()
    return train_dataframe, test_dataframe


def encode_main_features(train_dataframe, test_dataframe):
    y_train = train_dataframe["is_fraud"].copy()
    y_test = test_dataframe["is_fraud"].copy()

    x_train = train_dataframe.drop(columns=["is_fraud", "timestamp"])
    x_test = test_dataframe.drop(columns=["is_fraud", "timestamp"])

    combined = pd.concat([x_train, x_test], keys=["train", "test"], sort=False)
    combined = pd.get_dummies(combined, dtype=int)

    encoded_train = combined.xs("train").copy()
    encoded_test = combined.xs("test").copy()

    return encoded_train, encoded_test, y_train, y_test


def encode_card_features(train_dataframe, test_dataframe):
    y_train = train_dataframe["is_fraud"].copy()
    y_test = test_dataframe["is_fraud"].copy()

    x_train = train_dataframe.drop(columns=["is_fraud"]).copy()
    x_test = test_dataframe.drop(columns=["is_fraud"]).copy()

    return x_train, x_test, y_train, y_test


def train_model(x_train, y_train):
    # I keep the model settings simple on purpose.
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    return model


def calculate_metrics(model, x_test, y_test, sample_size):
    predicted_labels = model.predict(x_test)
    predicted_probabilities = model.predict_proba(x_test)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predicted_labels)), 4),
        "precision": round(float(precision_score(y_test, predicted_labels, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predicted_labels, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, predicted_labels, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, predicted_probabilities)), 4),
        "threshold": 0.5,
        "sample_size": int(sample_size),
    }
    return metrics


def build_main_config(original_dataframe, feature_columns):
    category_fields = [
        "transaction_type",
        "merchant_category",
        "location",
        "device_used",
        "payment_channel",
    ]

    numeric_fields = [
        "amount",
        "time_since_last_transaction",
        "spending_deviation_score",
        "velocity_score",
        "geo_anomaly_score",
        "hour",
        "day_of_week",
        "month",
    ]

    category_options = {}
    for field_name in category_fields:
        category_options[field_name] = sorted(
            original_dataframe[field_name].dropna().astype(str).unique().tolist()
        )

    numeric_defaults = {}
    for field_name in [
        "amount",
        "time_since_last_transaction",
        "spending_deviation_score",
        "velocity_score",
        "geo_anomaly_score",
    ]:
        median_value = pd.to_numeric(original_dataframe[field_name], errors="coerce").median()
        if not pd.notna(median_value):
            median_value = 0.0
        numeric_defaults[field_name] = round(float(median_value), 4)

    return {
        "dataset_name": "financial_fraud_detection_dataset.csv",
        "dataset_label": "Main Transaction Dataset",
        "model_name": "Random Forest",
        "description": "I use this model to check the richer transaction behaviour dataset.",
        "feature_columns": feature_columns,
        "category_fields": category_fields,
        "numeric_fields": numeric_fields,
        "category_options": category_options,
        "numeric_defaults": numeric_defaults,
        "time_defaults": {
            "hour": 12,
            "day_of_week": 2,
            "month": 6,
        },
        "risk_thresholds": {
            "high": 0.75,
            "medium": 0.45,
            "low": 0.0,
        },
        "input_style": "main",
    }


def build_card_config(original_dataframe, feature_columns):
    numeric_fields = [
        "distance_from_home",
        "distance_from_last_transaction",
        "ratio_to_median_purchase_price",
        "repeat_retailer",
        "used_chip",
        "used_pin_number",
        "online_order",
    ]

    numeric_defaults = {}
    for field_name in numeric_fields:
        median_value = pd.to_numeric(original_dataframe[field_name], errors="coerce").median()
        if not pd.notna(median_value):
            median_value = 0.0
        numeric_defaults[field_name] = round(float(median_value), 4)

    return {
        "dataset_name": "card_transdata.csv",
        "dataset_label": "Card Transaction Dataset",
        "model_name": "Random Forest",
        "description": "I use this model to check the card purchase dataset.",
        "feature_columns": feature_columns,
        "category_fields": [],
        "numeric_fields": numeric_fields,
        "category_options": {},
        "numeric_defaults": numeric_defaults,
        "time_defaults": {},
        "risk_thresholds": {
            "high": 0.75,
            "medium": 0.45,
            "low": 0.0,
        },
        "input_style": "card",
    }


def save_outputs(model, metrics, config, name_prefix):
    os.makedirs(MODEL_DIR, exist_ok=True)

    model_path = os.path.join(MODEL_DIR, f"{name_prefix}_fraud_model.pkl")
    metrics_path = os.path.join(MODEL_DIR, f"{name_prefix}_metrics.json")
    config_path = os.path.join(MODEL_DIR, f"{name_prefix}_model_config.json")

    with open(model_path, "wb") as file:
        pickle.dump(model, file)

    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2)

    return model_path, metrics_path, config_path


def train_main_transaction_model():
    dataframe = load_main_transaction_data()
    dataframe = prepare_main_dataset(dataframe)

    train_dataframe, test_dataframe = split_main_dataset(dataframe)
    x_train, x_test, y_train, y_test = encode_main_features(train_dataframe, test_dataframe)

    print("I loaded the main financial transaction dataset.")
    print("Training rows:", len(x_train))
    print("Test rows:", len(x_test))
    print("Feature count:", len(x_train.columns))

    model = train_model(x_train, y_train)
    metrics = calculate_metrics(model, x_test, y_test, len(x_train) + len(x_test))
    config = build_main_config(dataframe, x_train.columns.tolist())
    paths = save_outputs(model, metrics, config, "transaction")

    print("I trained the main transaction fraud model and saved the results.")
    print("Model file:", paths[0])
    print("Metrics file:", paths[1])
    print("Config file:", paths[2])
    print("Metrics:", metrics)


def train_card_transaction_model():
    dataframe = load_card_transaction_data()
    dataframe = prepare_card_dataset(dataframe)

    train_dataframe, test_dataframe = split_card_dataset(dataframe)
    x_train, x_test, y_train, y_test = encode_card_features(train_dataframe, test_dataframe)

    print("I loaded the card transaction dataset.")
    print("Training rows:", len(x_train))
    print("Test rows:", len(x_test))
    print("Feature count:", len(x_train.columns))

    model = train_model(x_train, y_train)
    metrics = calculate_metrics(model, x_test, y_test, len(x_train) + len(x_test))
    config = build_card_config(dataframe, x_train.columns.tolist())
    paths = save_outputs(model, metrics, config, "card_transaction")

    print("I trained the card transaction fraud model and saved the results.")
    print("Model file:", paths[0])
    print("Metrics file:", paths[1])
    print("Config file:", paths[2])
    print("Metrics:", metrics)


def main():
    train_main_transaction_model()
    print("")
    train_card_transaction_model()


if __name__ == "__main__":
    main()
