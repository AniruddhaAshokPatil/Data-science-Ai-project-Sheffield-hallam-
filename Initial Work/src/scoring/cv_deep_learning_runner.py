"""I run the full Torch-based CV inference path in a separate process."""

import argparse
import json
from pathlib import Path

import cv2
import torch

from src.train.load_models import load_cv_model


def _prepare_image(image_path: str, image_size: int = 224):
    # I prepare the image here so the deep-learning model sees the same input
    # layout every time I run document scoring.
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image at: {image_path}")

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized_image = cv2.resize(rgb_image, (image_size, image_size))

    tensor = torch.tensor(resized_image)
    tensor = tensor.permute(2, 0, 1)
    tensor = tensor.float()
    tensor = tensor.unsqueeze(0)
    tensor = tensor / 255.0
    return tensor


def run_inference(image_path: str):
    # I keep the actual Torch inference small here because this helper exists
    # only to prove whether the deep-learning CV runtime works.
    model = load_cv_model()
    image_tensor = _prepare_image(image_path)
    device = next(model.parameters()).device
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        logits = model(image_tensor)
        probability = torch.sigmoid(logits)
        model_score = float(probability.item())

    return {
        "cv_mode": "deep_learning",
        "model_score": model_score,
    }


def main():
    # I keep the command-line interface simple so the main API service can ask
    # this helper to score one image and read back JSON.
    parser = argparse.ArgumentParser(description="Run deep-learning CV inference.")
    parser.add_argument("--image-path", required=True)
    args = parser.parse_args()

    payload = run_inference(args.image_path)
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
