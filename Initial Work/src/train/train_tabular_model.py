"""I train and save the beginner-friendly tabular fraud model in this file."""

import joblib
from sklearn.ensemble import RandomForestClassifier

from src.train.model_paths import TABULAR_MODEL
from src.train.preprocess import (
    apply_preprocessing,
    build_preprocessor,
    load_transaction_training_dataframe,
)


def train_tabular_fraud_model(csv_path: str):
    # I keep the full tabular workflow inside one function so I can explain
    # the whole process from CSV to saved model in a straight line.
    dataframe = load_transaction_training_dataframe(csv_path)

    feature_dataframe = dataframe.drop(columns=["is_fraud"])
    target_series = dataframe["is_fraud"]

    # I fit and save the preprocessor first so later inference can transform
    # new rows in the same way as the training data.
    build_preprocessor(feature_dataframe)
    processed_features = apply_preprocessing(feature_dataframe)

    # I use a Random Forest here because it is a strong and explainable model
    # for structured beginner-level fraud features.
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
    )
    model.fit(processed_features, target_series)

    # I save the trained model so the API can reuse it without retraining.
    joblib.dump(model, TABULAR_MODEL)
    print(f"I saved the tabular model to: {TABULAR_MODEL}")
