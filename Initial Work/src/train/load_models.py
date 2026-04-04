import joblib
import torch

from src.models.simple_cnn import SimpleCNN
from src.train.model_paths import ANOMALY_MODEL, CV_CNN_MODEL, PREPROCESSOR, TABULAR_MODEL
from src.train.preprocess import apply_preprocessing, load_preprocessor


def load_tabular_model():
    # I keep model loading in one helper so the rest of the project does not
    # need to remember the exact artifact path every time it needs the model.
    model = joblib.load(TABULAR_MODEL)
    return model


def load_anomaly_model():
    # I use a separate loader for the anomaly model because each fraud modality
    # can have its own saved artifact and inference path.
    model = joblib.load(ANOMALY_MODEL)
    return model


def load_cv_model(model_path=CV_CNN_MODEL, device=None):
    # I make device optional here because I want the same function to work on
    # either CPU-only machines or machines that have CUDA available.
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # I rebuild the model architecture before loading weights because PyTorch
    # state dictionaries store parameters, not the full class definition.
    model = SimpleCNN()
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)

    # I switch to eval mode because this loader is meant for inference, not training.
    model.eval()
    return model
