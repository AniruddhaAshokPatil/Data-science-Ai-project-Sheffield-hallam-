"""I keep the reusable anomaly model service here for transaction scoring."""

import logging

import joblib
import numpy as np
import pandas as pd

from src.train.model_paths import ANOMALY_METADATA, ANOMALY_MODEL


logger = logging.getLogger(__name__)


class AnomalyModel:
    """I manage loading, validating, and scoring anomaly-detection inputs."""

    def __init__(self, model_path=ANOMALY_MODEL, metadata_path=ANOMALY_METADATA):
        # I store the artifact paths here because the same object may load once
        # and then serve many prediction requests afterward.
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.pipeline = None
        self.metadata = None
        self.feature_names = None
        self.score_min = None
        self.score_max = None
        self.threshold = None

    def load(self):
        # I load the saved model and the calibration metadata together because
        # the raw anomaly output is not meaningful without the saved scaling
        # values from training.
        try:
            self.pipeline = joblib.load(self.model_path)
            self.metadata = joblib.load(self.metadata_path)
            self.feature_names = self.metadata.get("features")
            self.score_min = float(self.metadata["score_min"])
            self.score_max = float(self.metadata["score_max"])
            self.threshold = float(self.metadata["threshold"])
            logger.info("I loaded the anomaly model from %s.", self.model_path)
        except Exception as exc:
            raise RuntimeError(f"I could not load the anomaly model: {exc}") from exc

    def _validate_input(self, X):
        # I validate the incoming data first because anomaly models are very
        # sensitive to missing values and mismatched column order.
        if X is None or len(X) == 0:
            raise ValueError("I need at least one row of input data.")

        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X)

        if not isinstance(X, pd.DataFrame):
            raise TypeError("I expect anomaly inputs as a pandas DataFrame or numpy array.")

        if X.isnull().sum().sum() > 0:
            raise ValueError("I found missing values in the anomaly input data.")

        if self.feature_names is not None:
            missing_features = sorted(set(self.feature_names) - set(X.columns))
            if missing_features:
                raise ValueError(f"I am missing required features: {missing_features}")

            # I reorder the columns here so prediction uses the same feature
            # order that the model saw during training.
            X = X[self.feature_names]

        return X

    def _compute_score(self, raw_score):
        # I convert the raw Isolation Forest output into a friendlier 0 to 1
        # score so the wider project can treat higher values as higher risk.
        score_range = self.score_max - self.score_min + 1e-6
        scaled_score = (raw_score - self.score_min) / score_range
        return 1 - scaled_score

    def predict(self, X):
        # I guard against unloaded artifacts because I want any misuse of this
        # class to fail with a clear explanation.
        if self.pipeline is None:
            raise RuntimeError("I need to load the anomaly model before I can predict.")

        validated_input = self._validate_input(X)

        try:
            raw_score = self.pipeline.decision_function(validated_input)
            calibrated_score = self._compute_score(raw_score)
            prediction = (calibrated_score > self.threshold).astype(int)
            return calibrated_score, prediction
        except Exception as exc:
            logger.error("I could not compute anomaly predictions. Reason: %s", exc)
            raise
