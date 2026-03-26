import joblib
import torch

from src.models.simple_cnn import SimpleCNN
from src.train.model_paths import ANOMALY_MODEL, CV_CNN_MODEL, PREPROCESSOR, TABULAR_MODEL
from src.train.preprocess import apply_preprocessing, load_preprocessor


def load_tabular_model():
    return joblib.load(TABULAR_MODEL)


def load_anomaly_model():
    return joblib.load(ANOMALY_MODEL)


def load_cv_model(model_path=CV_CNN_MODEL, device=None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    model = SimpleCNN()
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model
