# src/api/anomaly_inference.py

import os
import pickle
import numpy as np
import pandas as pd
import logging

# -------------------------------
# STEP 0: Logging Setup
# -------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------
# STEP 1: Model Loader (Controlled)
# -------------------------------

class AnomalyModel:
    """
    I am wrapping everything inside a class so I can:
    - control loading
    - validate inputs
    - reuse safely in APIs
    """

    def __init__(self, model_path="models/"):
        self.model_path = model_path
        self.pipeline = None
        self.metadata = None
        self.feature_names = None

    def load(self):
        """
        I explicitly load model artifacts (NOT at import time)
        """
        try:
            with open(os.path.join(self.model_path, "anomaly_pipeline.pkl"), "rb") as f:
                self.pipeline = pickle.load(f)

            with open(os.path.join(self.model_path, "anomaly_metadata.pkl"), "rb") as f:
                self.metadata = pickle.load(f)

            # I store calibration parameters
            self.score_min = self.metadata["score_min"]
            self.score_max = self.metadata["score_max"]
            self.threshold = self.metadata["threshold"]

            # Optional: load feature names if saved
            self.feature_names = self.metadata.get("features", None)

            logging.info("Anomaly model loaded successfully.")

        except Exception as e:
            raise RuntimeError(f"Failed to load anomaly model: {e}")

    # -------------------------------
    # STEP 2: Validation
    # -------------------------------

    def _validate_input(self, X):
        """
        I validate input before prediction to prevent silent failures
        """

        if X is None or len(X) == 0:
            raise ValueError("Input data is empty.")

        # Convert to DataFrame if needed
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X)

        # Check NaNs
        if X.isnull().sum().sum() > 0:
            raise ValueError("Input contains missing values.")

        # Align columns if feature names exist
        if self.feature_names is not None:
            missing_cols = set(self.feature_names) - set(X.columns)
            if missing_cols:
                raise ValueError(f"Missing required features: {missing_cols}")

            # I reorder columns to match training
            X = X[self.feature_names]

        return X

    # -------------------------------
    # STEP 3: Score Calibration
    # -------------------------------

    def _compute_score(self, raw_score):
        """
        I convert raw IsolationForest output into [0,1]
        """
        scaled = (raw_score - self.score_min) / (
            self.score_max - self.score_min + 1e-6
        )
        return 1 - scaled

    # -------------------------------
    # STEP 4: Prediction
    # -------------------------------

    def predict(self, X):
        """
        I return:
        - anomaly score
        - binary fraud prediction
        """

        if self.pipeline is None:
            raise RuntimeError("Model not loaded. Call .load() first.")

        # I validate and align input
        X = self._validate_input(X)

        try:
            # I compute raw anomaly score
            raw_score = self.pipeline.decision_function(X)

            # I calibrate score to [0,1]
            score = self._compute_score(raw_score)

            # I apply threshold
            prediction = (score > self.threshold).astype(int)

            return score, prediction

        except Exception as e:
            logging.error(f"Prediction failed: {e}")
            raise