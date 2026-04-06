import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.train.model_paths import PREPROCESSOR


# I list the most useful financial fraud columns here because they appear in the
# raw financial dataset and also match the features that my API scores at runtime.
PRIMARY_FINANCIAL_FEATURES = [
    "amount",
    "time_since_last_transaction",
    "spending_deviation_score",
    "velocity_score",
    "geo_anomaly_score",
]


def load_transaction_training_dataframe(csv_path: str) -> pd.DataFrame:
    """
    I load one transaction CSV and convert it into a clean training table that
    works for both the raw financial dataset and the processed datasets.
    """
    dataframe = pd.read_csv(csv_path)

    if "is_fraud" not in dataframe.columns:
        raise ValueError("Dataset must contain an 'is_fraud' column.")

    # I prefer the financial fraud feature set first because it is the dataset
    # the user asked to use, and those columns line up well with the live API.
    selected_feature_columns = []
    for column_name in PRIMARY_FINANCIAL_FEATURES:
        if column_name in dataframe.columns:
            selected_feature_columns.append(column_name)

    # I fall back to every numeric feature when a dataset uses a different
    # schema, because I still want older prepared files to keep working.
    if not selected_feature_columns:
        numeric_columns = dataframe.select_dtypes(include=["number", "bool"]).columns.tolist()
        selected_feature_columns = [
            column_name for column_name in numeric_columns if column_name != "is_fraud"
        ]

    if not selected_feature_columns:
        raise ValueError("I could not find any numeric transaction features to train on.")

    cleaned_dataframe = dataframe[selected_feature_columns + ["is_fraud"]].copy()

    # I fill missing numeric values with the median of each column so the raw
    # financial dataset can train cleanly even when some rows are incomplete.
    for column_name in selected_feature_columns:
        median_value = cleaned_dataframe[column_name].median()
        if pd.isna(median_value):
            median_value = 0.0
        cleaned_dataframe[column_name] = cleaned_dataframe[column_name].fillna(median_value)

    # I convert the target into 0 and 1 integers because some CSV files store
    # fraud labels as True and False instead of plain numbers.
    cleaned_dataframe["is_fraud"] = cleaned_dataframe["is_fraud"].astype(int)
    return cleaned_dataframe


def build_preprocessor(df: pd.DataFrame):
    """I build and save a numeric-only scaler so later inference can match training."""
    # I keep only numeric columns because StandardScaler works on numeric data,
    # and many model pipelines should not receive raw text columns directly.
    numeric_df = df.select_dtypes(include="number")
    numeric_columns = numeric_df.columns.tolist()

    scaler = StandardScaler()
    scaler.fit(numeric_df)

    # I save both the fitted scaler and the column order because inference must
    # transform new data in the same feature layout used during training.
    preprocessor_package = {"columns": numeric_columns, "scaler": scaler}
    joblib.dump(preprocessor_package, PREPROCESSOR)
    return numeric_columns, scaler


def load_preprocessor():
    # I load the saved scaler package here so training and inference code can
    # reuse the same preprocessing rules.
    data = joblib.load(PREPROCESSOR)
    return data["columns"], data["scaler"]


def apply_preprocessing(df: pd.DataFrame):
    """I apply the saved scaler to new transaction data in the same way as training."""
    columns, scaler = load_preprocessor()

    # I reindex columns here because new data may arrive with a different
    # order or with some missing columns, and I want a stable model input shape.
    df_num = df.reindex(columns=columns, fill_value=0)
    transformed_values = scaler.transform(df_num)
    return transformed_values
