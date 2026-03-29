import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.train.preprocess import apply_preprocessing, build_preprocessor
from src.train.model_paths import TABULAR_MODEL


def train_tabular_fraud_model(csv_path: str):
    # I keep the tabular training flow in one function so other parts of the
    # project can train the model without rewriting the same steps.
    dataframe = pd.read_csv(csv_path)
    dataframe = dataframe.dropna()

    # I check for the label column because supervised fraud training needs a
    # known target to learn what is fraudulent versus legitimate.
    if "is_fraud" not in dataframe.columns:
        raise ValueError("Dataset must contain an 'is_fraud' column.")

    feature_dataframe = dataframe.drop(columns=["is_fraud"])
    target_series = dataframe["is_fraud"]

    # I build the preprocessor first so inference later can transform features
    # in the same way as training.
    build_preprocessor(feature_dataframe)

    # I apply the saved preprocessing right away so the model sees scaled data.
    processed_features = apply_preprocessing(feature_dataframe)

    # I use a Random Forest here because it is a strong beginner-friendly model
    # for structured tabular fraud features.
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
    )
    model.fit(processed_features, target_series)

    # I save the trained model so the API can load it later without retraining.
    joblib.dump(model, TABULAR_MODEL)
    print(f"Saved tabular model to: {TABULAR_MODEL}")
    
