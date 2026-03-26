import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
from src.train.preprocess import apply_preprocessing, build_preprocessor
from src.train.model_paths import ANOMALY_MODEL


def train_anomaly_detector(csv_path: str):
    df = pd.read_csv(csv_path)
    df = df.dropna()

    # Use only NON-FRAUD rows to learn normal patterns
    if "is_fraud" in df.columns:
        df = df[df["is_fraud"] == 0]

    X = df.select_dtypes(include="number")

    # Preprocessing (shared with classifier)
    build_preprocessor(X)
    X_processed = apply_preprocessing(X)

    model = IsolationForest(
        contamination=0.01,
        random_state=42
    )
    model.fit(X_processed)

    joblib.dump(model, ANOMALY_MODEL)
    print(f"Saved anomaly model to: {ANOMALY_MODEL}")
