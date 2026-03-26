import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

from src.train.preprocess import apply_preprocessing, build_preprocessor
from src.train.model_paths import TABULAR_MODEL


def train_tabular_fraud_model(csv_path: str):
    df = pd.read_csv(csv_path)
    df = df.dropna()

    # Assume the dataset has a fraud label column
    if "is_fraud" not in df.columns:
        raise ValueError("Dataset must contain an 'is_fraud' column.")

    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    # Build and save preprocessor
    _, _ = build_preprocessor(X)

    # Apply preprocessing
    X_processed = apply_preprocessing(X)

    # Simple Random Forest model
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )
    model.fit(X_processed, y)

    # Save model
    joblib.dump(model, TABULAR_MODEL)
    print(f"Saved tabular model to: {TABULAR_MODEL}")
    
