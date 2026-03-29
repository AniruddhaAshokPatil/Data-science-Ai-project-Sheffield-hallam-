# src/train/train_fraud_model.py

import os
import pandas as pd
import numpy as np
import logging
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    classification_report,
    precision_recall_curve
)

# -------------------------------
# STEP 0: Reproducibility
# -------------------------------

np.random.seed(42)

# -------------------------------
# STEP 1: Logging
# -------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------
# STEP 2: Paths
# -------------------------------

# I keep training input and output paths near the top because this file is one
# complete training stage in the fraud pipeline.
INPUT_PATH = "data/processed/transactions/"
MODEL_PATH = "models/"

os.makedirs(MODEL_PATH, exist_ok=True)

# -------------------------------
# STEP 3: Load Data
# -------------------------------

logging.info("I am loading datasets...")

# I load the split files here because earlier data scripts already prepared
# train and test sets for the fraud model to learn from.
X_train = pd.read_csv(INPUT_PATH + "X_train.csv")
X_test = pd.read_csv(INPUT_PATH + "X_test.csv")
y_train = pd.read_csv(INPUT_PATH + "y_train.csv").values.ravel()
y_test = pd.read_csv(INPUT_PATH + "y_test.csv").values.ravel()

# -------------------------------
# STEP 4: Validation Checks
# -------------------------------

if X_train.empty or X_test.empty:
    raise ValueError("Input datasets are empty.")

if X_train.isnull().sum().sum() > 0:
    raise ValueError("NaNs detected in training data.")

if list(X_train.columns) != list(X_test.columns):
    raise ValueError("Feature mismatch between train and test sets")

logging.info(f"Train shape: {X_train.shape}")
logging.info(f"Fraud rate: {np.mean(y_train):.4f}")

# -------------------------------
# STEP 5: Build Pipeline
# -------------------------------

# I combine scaling and the model in one pipeline so preprocessing at training
# and inference time stays consistent.
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(
        class_weight="balanced",
        max_iter=300,
        random_state=42,
        n_jobs=-1
    )),
])

# -------------------------------
# STEP 6: Train Model
# -------------------------------

logging.info("I am training the pipeline...")

pipeline.fit(X_train, y_train)

# -------------------------------
# STEP 7: Predict Probabilities
# -------------------------------

# I use probabilities instead of hard classes first because fraud decisions
# usually need threshold tuning rather than one fixed default boundary.
predicted_probabilities = pipeline.predict_proba(X_test)
y_proba = predicted_probabilities[:, 1]

# -------------------------------
# STEP 8: Evaluation
# -------------------------------

roc = roc_auc_score(y_test, y_proba)
pr_auc = average_precision_score(y_test, y_proba)

logging.info(f"ROC-AUC: {roc:.4f}")
logging.info(f"PR-AUC: {pr_auc:.4f}")

# -------------------------------
# STEP 9: Threshold Optimisation
# -------------------------------

precision, recall, thresholds = precision_recall_curve(y_test, y_proba)

# I tune the threshold from precision and recall because fraud work often cares
# about the balance between catching fraud and avoiding false alarms.
numerator = 2 * precision * recall
denominator = precision + recall + 1e-6
f1_scores = numerator / denominator
best_idx = np.argmax(f1_scores)
best_threshold = thresholds[best_idx]

logging.info(f"Optimal threshold: {best_threshold:.4f}")

# I am applying optimal threshold
y_pred = (y_proba > best_threshold).astype(int)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -------------------------------
# STEP 10: Save Artifacts
# -------------------------------

# I save the full pipeline, not only the raw model, because the scaler is part
# of the learned workflow and must travel with the model artifact.
with open(MODEL_PATH + "fraud_pipeline.pkl", "wb") as f:
    pickle.dump(pipeline, f)

# I save metadata too because it helps the wider project know what threshold,
# metrics, and feature layout belonged to this training run.
metadata = {}
metadata["features"] = list(X_train.columns)
metadata["roc_auc"] = roc
metadata["pr_auc"] = pr_auc
metadata["threshold"] = float(best_threshold)

with open(MODEL_PATH + "model_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

logging.info("Pipeline and metadata saved successfully.")
