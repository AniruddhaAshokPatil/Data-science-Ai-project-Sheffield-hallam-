"""I keep the reusable tabular fraud model loader here for API predictions."""

import joblib

from src.train.model_paths import TABULAR_MODEL


class TabularModel:
    """I wrap the saved tabular model so the API can reuse it cleanly."""

    def __init__(self):
        # I start with no pipeline loaded because model loading is a separate
        # step from object creation in this project.
        self.pipeline = None

    def load(self):
        # I load the saved tabular model here so every prediction call uses the
        # exact artifact produced during training.
        self.pipeline = joblib.load(TABULAR_MODEL)

    def predict(self, X):
        # I check for the loaded pipeline first because predict_proba would
        # fail with a less helpful error if I skipped this guard.
        if self.pipeline is None:
            raise RuntimeError("I need to load the tabular model before I can predict.")

        probabilities = self.pipeline.predict_proba(X)
        return probabilities[:, 1]
