import os
import logging
import pickle

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

np.random.seed(42)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# I keep the NLP training paths near the top because this file is the text
# classification training stage in the wider fraud project.
INPUT_PATH = "data/processed/nlp/processed_spam.csv"
MODEL_PATH = "models/"

# I load the processed spam dataset here because earlier NLP prep should have
# turned raw SMS text into a cleaner training table.
dataframe = pd.read_csv(INPUT_PATH)

if "text" not in dataframe.columns or "label" not in dataframe.columns:
    raise ValueError("Dataset must contain 'text' and 'label' columns")

# I drop missing rows because text models need both message text and labels
# to train correctly.
dataframe = dataframe.dropna()

dataset_size = len(dataframe)
fraud_rate = dataframe["label"].mean()
logging.info(f"Dataset size: {dataset_size}")
logging.info(f"Fraud rate: {fraud_rate:.4f}")

X_train, X_test, y_train, y_test = train_test_split(
    dataframe["text"],
    dataframe["label"],
    test_size=0.2,
    random_state=42,
    stratify=dataframe["label"],
)

# I use a pipeline so text vectorization and the classifier always stay paired
# together as one reusable training-and-inference workflow.
vectorizer = TfidfVectorizer(
    max_features=3000,
    stop_words="english",
)
classifier = LogisticRegression(
    class_weight="balanced",
    max_iter=200,
    random_state=42,
)
pipeline_steps = [
    ("tfidf", vectorizer),
    ("model", classifier),
]
pipeline = Pipeline(pipeline_steps)

logging.info("Training NLP model...")

pipeline.fit(X_train, y_train)

# I use predicted probabilities first so I can tune the decision threshold
# instead of accepting the default classifier cutoff blindly.
predicted_probabilities = pipeline.predict_proba(X_test)
y_proba = predicted_probabilities[:, 1]

roc = roc_auc_score(y_test, y_proba)
pr_auc = average_precision_score(y_test, y_proba)

logging.info(f"ROC-AUC: {roc:.4f}")
logging.info(f"PR-AUC: {pr_auc:.4f}")

precision, recall, thresholds = precision_recall_curve(y_test, y_proba)

# I use an F1-style threshold search here because spam detection, like fraud,
# needs a balance between catching positives and avoiding false alarms.
f1_numerator = 2 * precision * recall
f1_denominator = precision + recall + 1e-6
f1_scores = f1_numerator / f1_denominator
best_idx = np.argmax(f1_scores)
best_threshold = thresholds[best_idx]

logging.info(f"Best threshold: {best_threshold:.4f}")

os.makedirs(MODEL_PATH, exist_ok=True)

# I save the full pipeline so the API can later load the same vectorizer and
# classifier together instead of rebuilding them from scratch.
pipeline_output_path = MODEL_PATH + "nlp_pipeline.pkl"
with open(pipeline_output_path, "wb") as pipeline_file:
    pickle.dump(pipeline, pipeline_file)

metadata = {
    "roc_auc": roc,
    "pr_auc": pr_auc,
    "threshold": float(best_threshold),
}

# I save metadata too because the wider project may need the threshold and
# evaluation metrics when serving or comparing models.
metadata_output_path = MODEL_PATH + "nlp_metadata.pkl"
with open(metadata_output_path, "wb") as metadata_file:
    pickle.dump(metadata, metadata_file)

logging.info("NLP model saved successfully.")
