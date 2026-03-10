import joblib
from ml.model_paths import TABULAR_MODEL, ANOMALY_MODEL, PREPROCESSOR
from ml.preprocess import apply_preprocessing, load_preprocessor


def load_tabular_model():
    return joblib.load(TABULAR_MODEL)


def load_anomaly_model():
    return joblib.load(ANOMALY_MODEL)
