import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

from src.train.model_paths import PREPROCESSOR


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
