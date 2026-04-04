import argparse
import json
from pathlib import Path
import pickle

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.train.model_paths import ANOMALY_METADATA, ANOMALY_MODEL


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "transactions" / "clean_validation.csv"
TARGET_COLUMN = "is_fraud"
MAX_TRAINING_ROWS = 200000


def compute_anomaly_score(raw_score, min_val, max_val):
    # I convert the raw IsolationForest output into a 0 to 1 style risk score
    # because the rest of the project reasons about fraud on that scale.
    score_range = max_val - min_val + 1e-6
    scaled = (raw_score - min_val) / score_range
    return 1 - scaled


def _load_training_frame(input_path: Path) -> pd.DataFrame:
    # I keep input loading in one helper so I can fail clearly when the issue's
    # training dataset is missing or shaped differently than expected.
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Training dataset not found at: {input_path}")

    dataframe = pd.read_csv(input_path)
    if TARGET_COLUMN not in dataframe.columns:
        raise ValueError(f"Training dataset must contain '{TARGET_COLUMN}'.")
    if dataframe.isnull().sum().sum() > 0:
        raise ValueError("I found missing values in the anomaly training dataset.")

    return dataframe


def train_anomaly_model(
    input_path: Path = DEFAULT_INPUT,
    model_output: Path = ANOMALY_MODEL,
    metadata_output: Path = ANOMALY_METADATA,
    max_rows: int = MAX_TRAINING_ROWS,
) -> dict:
    # I train on the labeled validation-style dataset here because it already
    # contains the structured fraud features this project serves at runtime.
    dataframe = _load_training_frame(input_path)
    if max_rows and len(dataframe) > max_rows:
        # I cap training rows here so the project can still retrain locally on
        # a laptop without turning this issue into an hours-long batch job.
        dataframe = dataframe.sample(n=max_rows, random_state=42)
    labels = dataframe[TARGET_COLUMN].astype(int)
    features = dataframe.drop(columns=[TARGET_COLUMN])

    # I learn the anomaly boundary only from legitimate rows because the model
    # is supposed to treat unusual behavior as suspicious drift from normal.
    normal_features = features[labels == 0]
    if normal_features.empty:
        raise ValueError("I need at least one legitimate transaction to train the anomaly model.")

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                IsolationForest(
                    n_estimators=200,
                    contamination="auto",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    pipeline.fit(normal_features)

    train_scores = pipeline.decision_function(normal_features)
    score_min = float(train_scores.min())
    score_max = float(train_scores.max())
    calibrated_train_scores = compute_anomaly_score(train_scores, score_min, score_max)
    threshold = float(np.percentile(calibrated_train_scores, 95))

    model_output = Path(model_output)
    metadata_output = Path(metadata_output)
    model_output.parent.mkdir(parents=True, exist_ok=True)
    metadata_output.parent.mkdir(parents=True, exist_ok=True)

    # I save the whole scaler-plus-model pipeline so inference uses the same
    # numeric preparation that training used.
    joblib.dump(pipeline, model_output)

    metadata = {
        "input_path": str(input_path),
        "features": list(features.columns),
        "score_min": score_min,
        "score_max": score_max,
        "threshold": threshold,
        "normal_rows": int(len(normal_features)),
        "total_rows": int(len(dataframe)),
    }
    with metadata_output.open("wb") as metadata_file:
        pickle.dump(metadata, metadata_file)

    return {
        "model_path": str(model_output),
        "metadata_path": str(metadata_output),
        "normal_rows": int(len(normal_features)),
        "total_rows": int(len(dataframe)),
        "threshold": threshold,
    }


def parse_args():
    # I expose the paths here so I can retrain against a different prepared
    # transaction dataset without editing this script each time.
    parser = argparse.ArgumentParser(description="Train the anomaly detection model.")
    parser.add_argument("--input-path", default=str(DEFAULT_INPUT))
    parser.add_argument("--model-output", default=str(ANOMALY_MODEL))
    parser.add_argument("--metadata-output", default=str(ANOMALY_METADATA))
    parser.add_argument("--max-rows", type=int, default=MAX_TRAINING_ROWS)
    return parser.parse_args()


def main():
    args = parse_args()
    summary = train_anomaly_model(
        input_path=Path(args.input_path),
        model_output=Path(args.model_output),
        metadata_output=Path(args.metadata_output),
        max_rows=args.max_rows,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
