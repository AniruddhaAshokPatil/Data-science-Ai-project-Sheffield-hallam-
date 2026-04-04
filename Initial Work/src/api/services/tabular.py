# src/api/services/tabular.py

import pickle

class TabularModel:

    def __init__(self):
        self.pipeline = None

    def load(self):
        # I load trained pipeline
        with open("models/fraud_pipeline_tuned.pkl", "rb") as f:
            self.pipeline = pickle.load(f)

    def predict(self, X):
        # I return fraud probability
        return self.pipeline.predict_proba(X)[:, 1]