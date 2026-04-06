import json
from pathlib import Path
import pickle

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.train.model_paths import ANOMALY_METADATA, ANOMALY_MODEL
from src.train.train_anomaly_model import train_anomaly_model


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "transactions" / "clean_validation.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "anomaly_evaluation.json"
MAX_EVAL_ROWS = 100000


def evaluate_anomaly_model(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    max_rows: int = MAX_EVAL_ROWS,
):
    # I compare anomaly detection against a supervised baseline here because
    # the issue asks whether the anomaly path catches fraud the classifier misses.
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at: {input_path}")

    dataframe = pd.read_csv(input_path)
    if "is_fraud" not in dataframe.columns:
        raise ValueError("Evaluation dataset must contain 'is_fraud'.")
    if max_rows and len(dataframe) > max_rows:
        # I sample here so the evaluation stays practical to rerun locally
        # while still preserving the class balance for comparison work.
        sampled_frames = []
        per_class_target = max(1, max_rows // max(1, dataframe["is_fraud"].nunique()))
        for _, frame in dataframe.groupby("is_fraud"):
            sampled_frames.append(
                frame.sample(n=min(len(frame), per_class_target), random_state=42)
            )
        dataframe = pd.concat(sampled_frames, ignore_index=True)
        dataframe = dataframe.sample(frac=1.0, random_state=42).reset_index(drop=True)

    features = dataframe.drop(columns=["is_fraud"])
    labels = dataframe["is_fraud"].astype(int)

    train_features, test_features, train_labels, test_labels = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    # I train the supervised baseline inside evaluation so I can measure
    # which fraud cases the anomaly model catches on top of it.
    supervised_model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )
    supervised_model.fit(train_features, train_labels)
    supervised_flags = supervised_model.predict(test_features).astype(int)

    if not Path(ANOMALY_MODEL).exists() or not Path(ANOMALY_METADATA).exists():
        train_anomaly_model(input_path=input_path, max_rows=max_rows)

    model = joblib.load(ANOMALY_MODEL)
    with Path(ANOMALY_METADATA).open("rb") as metadata_file:
        metadata = pickle.load(metadata_file)

    raw_scores = model.decision_function(test_features)
    scaled_scores = 1 - (
        (raw_scores - metadata["score_min"])
        / ((metadata["score_max"] - metadata["score_min"]) + 1e-6)
    )
    predicted_flags = np.where(scaled_scores > metadata["threshold"], 1, 0)

    tn, fp, fn, tp = confusion_matrix(test_labels, predicted_flags, labels=[0, 1]).ravel()
    anomaly_only_catches = int(
        ((predicted_flags == 1) & (supervised_flags == 0) & (test_labels.to_numpy() == 1)).sum()
    )
    anomaly_false_positive_additions = int(
        ((predicted_flags == 1) & (supervised_flags == 0) & (test_labels.to_numpy() == 0)).sum()
    )
    summary = {
        "rows": int(len(dataframe)),
        "rows_evaluated": int(len(test_features)),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "precision": float(precision_score(test_labels, predicted_flags, zero_division=0)),
        "recall": float(recall_score(test_labels, predicted_flags, zero_division=0)),
        "threshold": float(metadata["threshold"]),
        "anomaly_only_fraud_catches": anomaly_only_catches,
        "anomaly_only_false_positive_additions": anomaly_false_positive_additions,
    }

    output_path.write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    print(json.dumps(evaluate_anomaly_model(), indent=2))
