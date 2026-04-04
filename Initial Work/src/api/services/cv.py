# src/api/services/cv.py

import os
import torch
import numpy as np
import logging
import pickle
from PIL import Image
from torchvision import transforms, models
from torch import nn

# -------------------------------
# STEP 1: Logging
# -------------------------------

logging.basicConfig(level=logging.INFO)

# -------------------------------
# STEP 2: CV Model Wrapper
# -------------------------------

class CVModel:
    """
    I manage:
    - loading model
    - preprocessing images
    - predicting fraud score
    """

    def __init__(self, model_path="models/"):
        self.model_path = model_path
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # -------------------------------
    # STEP 3: Load Model
    # -------------------------------

    def load(self):
        try:
            # I rebuild SAME architecture as training
            self.model = models.resnet18(weights=None)
            self.model.fc = nn.Linear(self.model.fc.in_features, 1)

            # I load trained weights
            self.model.load_state_dict(
                torch.load(os.path.join(self.model_path, "cv_model.pth"), map_location=self.device)
            )

            self.model.to(self.device)
            self.model.eval()

            logging.info("CV model loaded successfully.")

        except Exception as e:
            raise RuntimeError(f"Failed to load CV model: {e}")

        # -------------------------------
        # STEP 4: Define Transform (MATCH TRAINING)
        # -------------------------------

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    # -------------------------------
    # STEP 5: Predict Function
    # -------------------------------

    def predict(self, image_path):
        """
        I take an image path and return:
        - fraud score [0,1]
        """

        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        try:
            # I load image
            image = Image.open(image_path).convert("RGB")

            # I apply same transform as training
            image = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                logits = self.model(image)

                # I convert logits → probability
                prob = torch.sigmoid(logits).cpu().numpy()[0][0]

            return np.array([prob])

        except Exception as e:
            logging.error(f"CV prediction failed: {e}")
            raise