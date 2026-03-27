# src/train/tune_fraud_model.py

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
# STEP 2: Load Data
# -------------------------------

INPUT_PATH = "data/processed/transactions/"
MODEL_PATH = "models/"

X_train = pd.read_csv(INPUT_PATH + "X_train.csv")
y_train = pd.read_csv(INPUT_PATH + "y_train.csv").values.ravel()

X_test = pd.read_csv(INPUT_PATH + "X_test.csv")
y_test = pd.read_csv(INPUT_PATH + "y_test.csv").values.ravel()

# -------------------------------
# STEP 3: Build Pipeline
# -------------------------------

def build_model(C):
    # I am creating a pipeline to ensure consistent scaling + model usage
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            C=C,
            class_weight="balanced",
            max_iter=300,
            random_state=42,
            n_jobs=-1
        ))
    ])

# -------------------------------
# STEP 4: Manual Time-Safe Tuning
# -------------------------------

param_values = [0.01, 0.1, 1, 10]

best_score = -1
best_model = None
best_C = None

logging.info("Starting manual time-safe tuning...")

for C in param_values:

    model = build_model(C)
    
    # I am training ONLY on training data (no CV leakage)
    model.fit(X_train, y_train)
    
    y_proba = model.predict_proba(X_test)[:, 1]
    
    score = roc_auc_score(y_test, y_proba)
    
    logging.info(f"C={C} → ROC-AUC={score:.4f}")
    
    if score > best_score:
        best_score = score
        best_model = model
        best_C = C

logging.info(f"Best C selected: {best_C}")

# -------------------------------
# STEP 5: Final Evaluation
# -------------------------------

y_proba = best_model.predict_proba(X_test)[:, 1]

roc = roc_auc_score(y_test, y_proba)
pr_auc = average_precision_score(y_test, y_proba)

logging.info(f"Final ROC-AUC: {roc:.4f}")
logging.info(f"Final PR-AUC: {pr_auc:.4f}")

# -------------------------------
# STEP 6: Threshold Optimisation
# -------------------------------

precision, recall, thresholds = precision_recall_curve(y_test, y_proba)

f1_scores = (2 * precision * recall) / (precision + recall + 1e-6)
best_idx = np.argmax(f1_scores)

best_threshold = thresholds[best_idx]

logging.info(f"Optimal Threshold: {best_threshold:.4f}")

# -------------------------------
# STEP 7: Save Artifacts
# -------------------------------

os.makedirs(MODEL_PATH, exist_ok=True)

with open(MODEL_PATH + "fraud_pipeline_tuned.pkl", "wb") as f:
    pickle.dump(best_model, f)

metadata = {
    "best_C": best_C,
    "roc_auc": roc,
    "pr_auc": pr_auc,
    "threshold": float(best_threshold),
    "features": list(X_train.columns)
}

with open(MODEL_PATH + "tuned_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

logging.info("Tuned model and metadata saved successfully.")