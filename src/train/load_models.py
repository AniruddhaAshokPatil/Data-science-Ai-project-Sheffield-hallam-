"""I keep shared artifact-loading helpers here for the training and API code."""

import joblib
import torch

from src.models.simple_cnn import SimpleCNN
from src.train.model_paths import ANOMALY_MODEL, CV_CNN_MODEL, TABULAR_MODEL


def load_tabular_model():
    # I use one helper here so other files do not have to remember the exact
    # artifact path for the saved tabular fraud model.
    return joblib.load(TABULAR_MODEL)


def load_anomaly_model():
    # I keep anomaly loading separate because that artifact belongs to a
    # different fraud-detection branch from the tabular classifier.
    return joblib.load(ANOMALY_MODEL)


def load_cv_model(model_path=CV_CNN_MODEL, device=None):
    # I make the device optional so this helper can work on both CPU-only
    # laptops and CUDA-enabled machines.
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # I rebuild the shared SimpleCNN class before loading its saved weights
    # because PyTorch stores parameters separately from the class definition.
    model = SimpleCNN()
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model
