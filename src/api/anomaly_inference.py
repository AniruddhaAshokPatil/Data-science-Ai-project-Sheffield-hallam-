import pickle
import logging

import numpy as np
import pandas as pd

from src.train.model_paths import ANOMALY_METADATA, ANOMALY_MODEL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class AnomalyModel:
    # I wrap the anomaly workflow in a class so the wider fraud project can load once and predict many times.

    def __init__(self, model_path=ANOMALY_MODEL, metadata_path=ANOMALY_METADATA):
        # I keep these values on the object because loading happens once, but prediction may happen many times.
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.pipeline = None
        self.metadata = None
        self.feature_names = None

    def load(self):
        # I load the artifacts here instead of at import time so this module stays safer to reuse in the API.
        try:
            with open(self.model_path, "rb") as pipeline_file:
                self.pipeline = pickle.load(pipeline_file)

            with open(self.metadata_path, "rb") as metadata_file:
                self.metadata = pickle.load(metadata_file)

            # I save these calibration values because the raw anomaly output is not very readable on its own.
            self.score_min = self.metadata["score_min"]
            self.score_max = self.metadata["score_max"]
            self.threshold = self.metadata["threshold"]

            # I keep the feature list when it exists so prediction can match the training column order.
            self.feature_names = self.metadata.get("features", None)

            logging.info("Anomaly model loaded successfully.")

        except Exception as e:
            raise RuntimeError(f"Failed to load anomaly model: {e}")

    def _validate_input(self, X):
        # I validate before prediction because anomaly models are sensitive to missing or misaligned inputs.
        if X is None or len(X) == 0:
            raise ValueError("Input data is empty.")

        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X)

        missing_value_count = X.isnull().sum().sum()
        if missing_value_count > 0:
            raise ValueError("Input contains missing values.")

        if self.feature_names is not None:
            missing_cols = set(self.feature_names) - set(X.columns)
            if missing_cols:
                raise ValueError(f"Missing required features: {missing_cols}")

            # I reorder columns because the model expects the same feature order used during training.
            X = X[self.feature_names]

        return X

    def _compute_score(self, raw_score):
        # I convert the raw anomaly output into a 0 to 1 style score because that is easier for the rest of the project.
        score_range = self.score_max - self.score_min + 1e-6
        scaled = (raw_score - self.score_min) / score_range
        score = 1 - scaled
        return score

    def predict(self, X):
        if self.pipeline is None:
            raise RuntimeError("Model not loaded. Call .load() first.")

        X = self._validate_input(X)

        try:
            raw_score = self.pipeline.decision_function(X)
            score = self._compute_score(raw_score)
            prediction = (score > self.threshold).astype(int)

            # I return both forms because some project flows want the score and others want a yes/no decision.
            return score, prediction

        except Exception as e:
            logging.error(f"Prediction failed: {e}")
            raise
