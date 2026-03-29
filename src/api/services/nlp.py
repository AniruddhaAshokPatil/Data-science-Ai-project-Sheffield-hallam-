# src/api/services/nlp.py

import pickle

class NLPModel:

    def __init__(self):
        self.pipeline = None

    def load(self):
        with open("models/nlp_pipeline.pkl", "rb") as f:
            self.pipeline = pickle.load(f)

    def predict(self, texts):
        return self.pipeline.predict_proba(texts)[:, 1]