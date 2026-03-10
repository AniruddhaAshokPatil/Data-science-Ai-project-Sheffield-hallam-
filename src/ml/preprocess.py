import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib
from ml.model_paths import PREPROCESSOR


def build_preprocessor(df: pd.DataFrame):
    """Build a numeric-only scaler."""
    numeric_df = df.select_dtypes(include="number")
    scaler = StandardScaler()
    scaler.fit(numeric_df)
    joblib.dump({"columns": numeric_df.columns.tolist(), "scaler": scaler}, PREPROCESSOR)
    return numeric_df.columns.tolist(), scaler


def load_preprocessor():
    data = joblib.load(PREPROCESSOR)
    return data["columns"], data["scaler"]


def apply_preprocessing(df: pd.DataFrame):
    """Applies the saved scaler to new transaction data."""
    columns, scaler = load_preprocessor()
    df_num = df.reindex(columns=columns, fill_value=0)
    return scaler.transform(df_num)