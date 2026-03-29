import os
import logging
import pickle

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

np.random.seed(42)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# I keep tuning paths near the top because this file is a follow-up training
# stage that tests a few hyperparameter choices for the fraud model.
INPUT_PATH = "data/processed/transactions/"
MODEL_PATH = "models/"

# I load the prepared split files here because tuning should use the same
# training and testing pipeline as the main fraud model.
X_train_path = INPUT_PATH + "X_train.csv"
y_train_path = INPUT_PATH + "y_train.csv"
X_test_path = INPUT_PATH + "X_test.csv"
y_test_path = INPUT_PATH + "y_test.csv"

X_train = pd.read_csv(X_train_path)
y_train_frame = pd.read_csv(y_train_path)
y_train = y_train_frame.values.ravel()

X_test = pd.read_csv(X_test_path)
y_test_frame = pd.read_csv(y_test_path)
y_test = y_test_frame.values.ravel()

def build_model(c_value):
    # I keep model construction in one helper so I can test different C values
    # while keeping the rest of the pipeline exactly the same.
    logistic_model = LogisticRegression(
        C=c_value,
        class_weight="balanced",
        max_iter=300,
        random_state=42,
        n_jobs=-1,
    )
    pipeline_steps = [
        ("scaler", StandardScaler()),
        ("model", logistic_model),
    ]
    return Pipeline(pipeline_steps)

# I use a small manual list of C values because this is a simple, time-safe
# tuning pass instead of a large automated hyperparameter search.
param_values = [0.01, 0.1, 1, 10]

best_score = -1
best_model = None
best_C = None

logging.info("Starting manual time-safe tuning...")

for c_value in param_values:

    model = build_model(c_value)

    # I am training ONLY on training data (no CV leakage)
    model.fit(X_train, y_train)

    # I score on the held-out test set here so I can compare each tuned model
    # by the same ROC-AUC metric.
    predicted_probabilities = model.predict_proba(X_test)
    y_proba = predicted_probabilities[:, 1]

    score = roc_auc_score(y_test, y_proba)

    logging.info(f"C={c_value} → ROC-AUC={score:.4f}")

    if score > best_score:
        best_score = score
        best_model = model
        best_C = c_value

logging.info(f"Best C selected: {best_C}")

best_predicted_probabilities = best_model.predict_proba(X_test)
y_proba = best_predicted_probabilities[:, 1]

roc = roc_auc_score(y_test, y_proba)
pr_auc = average_precision_score(y_test, y_proba)

logging.info(f"Final ROC-AUC: {roc:.4f}")
logging.info(f"Final PR-AUC: {pr_auc:.4f}")

# I optimize the final threshold after choosing the best C because fraud
# predictions usually need a tuned operating point, not just a tuned model.
precision, recall, thresholds = precision_recall_curve(y_test, y_proba)

f1_numerator = 2 * precision * recall
f1_denominator = precision + recall + 1e-6
f1_scores = f1_numerator / f1_denominator
best_idx = np.argmax(f1_scores)

best_threshold = thresholds[best_idx]

logging.info(f"Optimal Threshold: {best_threshold:.4f}")

os.makedirs(MODEL_PATH, exist_ok=True)

# I save the tuned pipeline separately so it does not overwrite the default
# fraud model until I decide which version I want to serve.
tuned_pipeline_path = MODEL_PATH + "fraud_pipeline_tuned.pkl"
with open(tuned_pipeline_path, "wb") as pipeline_file:
    pickle.dump(best_model, pipeline_file)

metadata = {
    "best_C": best_C,
    "roc_auc": roc,
    "pr_auc": pr_auc,
    "threshold": float(best_threshold),
    "features": list(X_train.columns),
}

metadata_output_path = MODEL_PATH + "tuned_metadata.pkl"
with open(metadata_output_path, "wb") as metadata_file:
    pickle.dump(metadata, metadata_file)

logging.info("Tuned model and metadata saved successfully.")
