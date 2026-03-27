# src/train/train_nlp_model.py

import os
import pandas as pd
import numpy as np
import logging
import pickle

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve

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

INPUT_PATH = "data/processed/nlp/processed_spam.csv"
MODEL_PATH = "models/"

df = pd.read_csv(INPUT_PATH)

# -------------------------------
# STEP 3: Validation
# -------------------------------

if "text" not in df.columns or "label" not in df.columns:
    raise ValueError("Dataset must contain 'text' and 'label' columns")

df = df.dropna()

logging.info(f"Dataset size: {len(df)}")
logging.info(f"Fraud rate: {df['label'].mean():.4f}")

# -------------------------------
# STEP 4: Train/Test Split
# -------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    df["text"],
    df["label"],
    test_size=0.2,
    random_state=42,
    stratify=df["label"]
)

# -------------------------------
# STEP 5: Pipeline
# -------------------------------

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=3000,
        stop_words="english"
    )),
    ("model", LogisticRegression(
        class_weight="balanced",
        max_iter=200,
        random_state=42
    ))
])

# -------------------------------
# STEP 6: Train
# -------------------------------

logging.info("Training NLP model...")

pipeline.fit(X_train, y_train)

# -------------------------------
# STEP 7: Evaluate
# -------------------------------

y_proba = pipeline.predict_proba(X_test)[:, 1]

roc = roc_auc_score(y_test, y_proba)
pr_auc = average_precision_score(y_test, y_proba)

logging.info(f"ROC-AUC: {roc:.4f}")
logging.info(f"PR-AUC: {pr_auc:.4f}")

# -------------------------------
# STEP 8: Threshold Optimisation
# -------------------------------

precision, recall, thresholds = precision_recall_curve(y_test, y_proba)

f1 = (2 * precision * recall) / (precision + recall + 1e-6)
best_idx = np.argmax(f1)
best_threshold = thresholds[best_idx]

logging.info(f"Best threshold: {best_threshold:.4f}")

# -------------------------------
# STEP 9: Save
# -------------------------------

os.makedirs(MODEL_PATH, exist_ok=True)

with open(MODEL_PATH + "nlp_pipeline.pkl", "wb") as f:
    pickle.dump(pipeline, f)

metadata = {
    "roc_auc": roc,
    "pr_auc": pr_auc,
    "threshold": float(best_threshold)
}

with open(MODEL_PATH + "nlp_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

logging.info("NLP model saved successfully.")