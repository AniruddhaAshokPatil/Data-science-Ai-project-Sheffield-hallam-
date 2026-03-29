import os
import logging
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# I am fixing randomness so results are consistent every time I run
np.random.seed(42)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# I keep training paths together here because this file is the anomaly-model
# stage of the wider fraud training pipeline.
INPUT_PATH = "data/processed/transactions/"
MODEL_PATH = "models/"

os.makedirs(MODEL_PATH, exist_ok=True)

logging.info("I am loading datasets...")

# I load only the training split here because anomaly training should learn
# what normal behavior looks like before I score suspicious behavior.
X_train_path = INPUT_PATH + "X_train.csv"
y_train_path = INPUT_PATH + "y_train.csv"

X_train = pd.read_csv(X_train_path)
y_train_frame = pd.read_csv(y_train_path)
y_train = y_train_frame.values.ravel()

missing_value_count = X_train.isnull().sum().sum()
if missing_value_count > 0:
    raise ValueError("I found missing values in training data")

# I train on legitimate transactions only because anomaly detection is meant
# to learn the normal pattern and then flag deviations from it.
X_train_normal = X_train[y_train == 0]

logging.info(f"I am training on {len(X_train_normal)} normal samples")

# I use a pipeline here so feature scaling and the anomaly model stay linked
# together when I later save and reuse them.
anomaly_model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42,
    n_jobs=-1,
)

pipeline_steps = [
    ("scaler", StandardScaler()),
    ("model", anomaly_model),
]
pipeline = Pipeline(pipeline_steps)

logging.info("I am training anomaly model...")

pipeline.fit(X_train_normal)

# I am using ONLY training data to define score distribution
# I use decision_function on training-normal data because I need a reference
# score distribution before I can calibrate anomaly scores for inference.
train_scores = pipeline.decision_function(X_train_normal)

score_min = train_scores.min()
score_max = train_scores.max()

logging.info(f"Score range (train): {score_min:.4f} → {score_max:.4f}")

# I define the score conversion here so the raw IsolationForest output can be
# turned into a clearer fraud-like score between 0 and 1.
def compute_anomaly_score(raw_score, min_val, max_val):
    """
    I convert raw IsolationForest output into [0,1] fraud score
    """
    score_range = max_val - min_val + 1e-6
    scaled = (raw_score - min_val) / score_range
    anomaly_score = 1 - scaled
    return anomaly_score

# I use a percentile threshold because anomaly detection often depends on the
# tail of the score distribution rather than a fixed class boundary.
calibrated_train_scores = compute_anomaly_score(train_scores, score_min, score_max)
threshold = np.percentile(calibrated_train_scores, 95)

logging.info(f"Anomaly threshold set at: {threshold:.4f}")

# I save the full pipeline because inference needs both scaling and the model.
pipeline_output_path = MODEL_PATH + "anomaly_pipeline.pkl"
with open(pipeline_output_path, "wb") as pipeline_file:
    pickle.dump(pipeline, pipeline_file)

# I save calibration information because inference needs the same score conversion later.
metadata = {
    "score_min": float(score_min),
    "score_max": float(score_max),
    "threshold": float(threshold),
}

metadata_output_path = MODEL_PATH + "anomaly_metadata.pkl"
with open(metadata_output_path, "wb") as metadata_file:
    pickle.dump(metadata, metadata_file)

logging.info("I have saved anomaly pipeline and metadata successfully.")
