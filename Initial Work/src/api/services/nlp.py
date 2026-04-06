"""I keep the reusable NLP model loader here for the API service layer."""

import joblib

from src.train.model_paths import NLP_MODEL, NLP_VECTORIZER


class NLPModel:
    """I wrap the spam model and vectorizer so the API can load them once."""

    def __init__(self):
        # I start with empty attributes because loading should happen only when
        # the application is actually ready to use the saved artifacts.
        self.model = None
        self.vectorizer = None

    def load(self):
        # I load both saved artifacts here because text prediction needs the
        # same vectorizer and the same trained classifier from training time.
        self.model = joblib.load(NLP_MODEL)
        self.vectorizer = joblib.load(NLP_VECTORIZER)

    def predict(self, texts):
        # I refuse to predict before loading because silent failures would be
        # confusing to explain during a demo or to a professor.
        if self.model is None or self.vectorizer is None:
            raise RuntimeError("I need to load the NLP model before I can predict.")

        # I transform the raw messages into the same bag-of-words features that
        # the saved classifier learned from during training.
        transformed_texts = self.vectorizer.transform(texts)
        probabilities = self.model.predict_proba(transformed_texts)
        return probabilities[:, 1]
