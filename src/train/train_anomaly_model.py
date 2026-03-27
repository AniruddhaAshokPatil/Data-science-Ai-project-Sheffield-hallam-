# src/train/train_anomaly_model.py

import os
import pandas as pd
import numpy as np
import logging
import pickle

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# -------------------------------
# STEP 0: Reproducibility
# -------------------------------

# I am fixing randomness so results are consistent every time I run
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

INPUT_PATH = "data/processed/transactions/"
MODEL_PATH = "models/"

os.makedirs(MODEL_PATH, exist_ok=True)

# -------------------------------
# STEP 3: Load Data
# -------------------------------

logging.info("I am loading datasets...")

X_train = pd.read_csv(INPUT_PATH + "X_train.csv")
y_train = pd.read_csv(INPUT_PATH + "y_train.csv").values.ravel()

# -------------------------------
# STEP 4: Validation
# -------------------------------

# I am ensuring there are no missing values
if X_train.isnull().sum().sum() > 0:
    raise ValueError("I found missing values in training data")

# -------------------------------
# STEP 5: Train ONLY on Normal Data
# -------------------------------

# I am selecting only legitimate transactions
X_train_normal = X_train[y_train == 0]

logging.info(f"I am training on {len(X_train_normal)} normal samples")

# -------------------------------
# STEP 6: Build Pipeline
# -------------------------------

# I am combining scaling + model to avoid mismatch in production
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", IsolationForest(
        n_estimators=200,
        contamination="auto",  # I let model infer anomaly proportion
        random_state=42,
        n_jobs=-1
    ))
])

# -------------------------------
# STEP 7: Train Model
# -------------------------------

logging.info("I am training anomaly model...")

pipeline.fit(X_train_normal)

# -------------------------------
# STEP 8: Generate TRAIN Scores (IMPORTANT)
# -------------------------------

# I am using ONLY training data to define score distribution
train_scores = pipeline.decision_function(X_train_normal)

# -------------------------------
# STEP 9: Build Score Calibrator
# -------------------------------

# I am computing min/max from TRAIN (not test!)
score_min = train_scores.min()
score_max = train_scores.max()

logging.info(f"Score range (train): {score_min:.4f} → {score_max:.4f}")

# -------------------------------
# STEP 10: Define Scoring Function
# -------------------------------

# I am defining a reusable function for inference
def compute_anomaly_score(raw_score, min_val, max_val):
    """
    I convert raw IsolationForest output into [0,1] fraud score
    """
    scaled = (raw_score - min_val) / (max_val - min_val + 1e-6)
    return 1 - scaled  # higher = more anomalous

# -------------------------------
# STEP 11: Define Threshold
# -------------------------------

# I am using percentile-based threshold (robust for anomaly detection)
threshold = np.percentile(
    compute_anomaly_score(train_scores, score_min, score_max),
    95  # top 5% most anomalous
)

logging.info(f"Anomaly threshold set at: {threshold:.4f}")

# -------------------------------
# STEP 12: Save Artifacts
# -------------------------------

# I am saving full pipeline (scaler + model)
with open(MODEL_PATH + "anomaly_pipeline.pkl", "wb") as f:
    pickle.dump(pipeline, f)

# I am saving calibration + threshold
metadata = {
    "score_min": float(score_min),
    "score_max": float(score_max),
    "threshold": float(threshold)
}

with open(MODEL_PATH + "anomaly_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

logging.info("I have saved anomaly pipeline and metadata successfully.")