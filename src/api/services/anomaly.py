import pickle
import numpy as np
import pandas as pd
import logging

from src.train.model_paths import ANOMALY_METADATA, ANOMALY_MODEL

# -------------------------------
# STEP 1: Logging
# -------------------------------

logging.basicConfig(level=logging.INFO)

# -------------------------------
# STEP 2: Anomaly Model Wrapper
# -------------------------------

class AnomalyModel:
    """
    I manage:
    - loading anomaly model
    - scaling anomaly scores
    - applying threshold
    """

    def __init__(self, model_path=ANOMALY_MODEL, metadata_path=ANOMALY_METADATA):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.pipeline = None
        self.metadata = None

    # -------------------------------
    # STEP 3: Load Model + Metadata
    # -------------------------------

    def load(self):
        try:
            # I load the saved anomaly pipeline here because the API should use
            # the same fitted scaler and IsolationForest from training.
            with open(self.model_path, "rb") as model_file:
                self.pipeline = pickle.load(model_file)

            # I load calibration values from the shared metadata path so the
            # risk score scaling stays consistent across the whole project.
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)

            self.score_min = self.metadata["score_min"]
            self.score_max = self.metadata["score_max"]
            self.threshold = self.metadata["threshold"]

            # Optional: feature names for alignment
            self.feature_names = self.metadata.get("features", None)

            logging.info("Anomaly model loaded successfully.")

        except Exception as e:
            raise RuntimeError(f"Failed to load anomaly model: {e}")

    # -------------------------------
    # STEP 4: Input Validation
    # -------------------------------

    def _validate_input(self, X):
        """
        I ensure input is correct before prediction
        """

        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X)

        if X is None or len(X) == 0:
            raise ValueError("Input data is empty")

        if X.isnull().sum().sum() > 0:
            raise ValueError("Input contains missing values")

        # I align columns to training schema
        if self.feature_names is not None:
            missing = set(self.feature_names) - set(X.columns)
            if missing:
                raise ValueError(f"Missing features: {missing}")

            X = X[self.feature_names]

        return X

    # -------------------------------
    # STEP 5: Score Calibration
    # -------------------------------

    def _compute_score(self, raw_score):
        """
        I convert raw IsolationForest output into [0,1]
        """

        scaled = (raw_score - self.score_min) / (
            self.score_max - self.score_min + 1e-6
        )

        return 1 - scaled  # higher = more anomalous

    # -------------------------------
    # STEP 6: Predict
    # -------------------------------

    def predict(self, X):
        """
        I return:
        - anomaly score [0,1]
        - binary fraud flag
        """

        if self.pipeline is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        # I validate input
        X = self._validate_input(X)

        try:
            # I compute raw anomaly score
            raw_score = self.pipeline.decision_function(X)

            # I convert to calibrated fraud score
            score = self._compute_score(raw_score)

            # I apply threshold
            prediction = (score > self.threshold).astype(int)

            return score, prediction

        except Exception as e:
            logging.error(f"Anomaly prediction failed: {e}")
            raise
