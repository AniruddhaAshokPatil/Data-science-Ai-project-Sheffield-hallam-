from pathlib import Path

import cv2
import numpy as np
import torch

from src.scoring.fraud_score import compute_fraud_score
from src.train.load_models import load_cv_model
from src.train.model_paths import CV_CNN_MODEL

_cv_model = None
_cv_model_error = None


def _load_cv_model_once():
    global _cv_model, _cv_model_error
    if _cv_model is not None or _cv_model_error is not None:
        return _cv_model

    try:
        if not Path(CV_CNN_MODEL).exists():
            _cv_model_error = f"CV model not found at {CV_CNN_MODEL}"
            return None
        _cv_model = load_cv_model()
    except Exception as exc:
        _cv_model_error = str(exc)
        return None

    return _cv_model


def _prepare_image(image_path, image_size=224):
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not read image at: {image_path}")

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (image_size, image_size))
    tensor = torch.tensor(resized).permute(2, 0, 1).float().unsqueeze(0) / 255.0
    return image, tensor


def _compute_blur_score(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(max(0.0, min(1.0, 1.0 - min(lap_var / 400.0, 1.0))))


def _compute_ocr_score(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    black_ratio = 1.0 - (float(np.count_nonzero(thresh)) / float(thresh.size))
    return float(max(0.0, min(1.0, 1.0 - min(abs(black_ratio - 0.18) / 0.18, 1.0))))


def _compute_metadata_score(image_path, metadata):
    path = Path(image_path)
    file_size_mb = path.stat().st_size / (1024 * 1024)
    size_score = 0.0 if 0.02 <= file_size_mb <= 8.0 else 0.6

    metadata_score = size_score
    if metadata:
        suspicious_flag = metadata.get("suspicious", False)
        was_edited = metadata.get("was_edited", False)
        source = str(metadata.get("source", "")).lower()

        if suspicious_flag:
            metadata_score += 0.3
        if was_edited:
            metadata_score += 0.3
        if source in {"unknown", "external", "untrusted"}:
            metadata_score += 0.2

    return float(max(0.0, min(1.0, metadata_score)))


def predict_cv_fraud(image_path, metadata=None):
    model = _load_cv_model_once()
    if model is None:
        raise RuntimeError(_cv_model_error or "CV model could not be loaded.")

    raw_image, image_tensor = _prepare_image(image_path)
    device = next(model.parameters()).device
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        logits = model(image_tensor)
        model_score = float(torch.sigmoid(logits).item())

    blur_score = _compute_blur_score(raw_image)
    ocr_score = _compute_ocr_score(raw_image)
    metadata_score = _compute_metadata_score(image_path, metadata)

    fraud_score = compute_fraud_score(
        model_score=model_score,
        blur_score=blur_score,
        ocr_score=ocr_score,
        metadata_score=metadata_score,
    )

    verdict = "fraud_suspected" if fraud_score >= 0.5 else "likely_genuine"

    return {
        "fraud_score": fraud_score,
        "verdict": verdict,
        "details": {
            "model_score": model_score,
            "blur_score": blur_score,
            "ocr_score": ocr_score,
            "metadata_score": metadata_score,
        },
        "model_path": str(CV_CNN_MODEL),
    }
