"""I keep the reusable computer-vision fraud model loader here for the API."""

import logging

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from src.models.simple_cnn import SimpleCNN
from src.train.model_paths import CV_CNN_MODEL


logger = logging.getLogger(__name__)


class CVModel:
    """I manage loading, preprocessing, and scoring for image fraud checks."""

    def __init__(self, model_path=CV_CNN_MODEL):
        # I save the model path and device here so I can explain clearly where
        # the weights come from and whether I am using CPU or GPU.
        self.model_path = model_path
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    def load(self):
        # I rebuild the same SimpleCNN architecture from training before I load
        # the saved state dictionary into it.
        try:
            self.model = SimpleCNN()
            state_dict = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            logger.info("I loaded the CV model from %s.", self.model_path)
        except Exception as exc:
            raise RuntimeError(f"I could not load the CV model: {exc}") from exc

    def predict(self, image_path):
        # I stop early if the model is missing because that produces a clearer
        # teaching-friendly error message than a low-level PyTorch failure.
        if self.model is None:
            raise RuntimeError("I need to load the CV model before I can predict.")

        try:
            image = Image.open(image_path).convert("RGB")
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                logits = self.model(image_tensor)
                probability = torch.sigmoid(logits).item()

            return np.array([probability], dtype=float)
        except Exception as exc:
            logger.error("I could not score the image %s. Reason: %s", image_path, exc)
            raise
