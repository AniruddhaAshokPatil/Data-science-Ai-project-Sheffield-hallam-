from pathlib import Path

import cv2
import numpy as np
import torch

from src.api.logger import logger
from src.scoring.fraud_score import compute_fraud_score
from src.train.load_models import load_cv_model
from src.train.model_paths import CV_CNN_MODEL

_cv_model = None
_cv_model_error = None


def _load_cv_model_once():
    # I cache the model here because loading CV weights repeatedly would slow
    # the API down every time I score a new document image.
    global _cv_model, _cv_model_error
    if _cv_model is not None or _cv_model_error is not None:
        return _cv_model

    try:
        model_path = Path(CV_CNN_MODEL)

        if not model_path.exists():
            _cv_model_error = f"CV model not found at {CV_CNN_MODEL}"
            logger.warning(_cv_model_error)
            return None

        _cv_model = load_cv_model()
        logger.info("I loaded the CV fraud model from %s.", model_path)
    except Exception as exc:
        _cv_model_error = str(exc)
        logger.warning("I could not load the CV fraud model. Reason: %s", exc)
        return None

    return _cv_model


def _prepare_image(image_path, image_size=224):
    # I keep image preparation in one helper so the model always receives the
    # same resize and tensor conversion steps for every prediction.
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not read image at: {image_path}")

    # I convert BGR to RGB because OpenCV loads images in BGR order, while the
    # model workflow is easier to reason about in standard RGB order.
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized_image = cv2.resize(rgb_image, (image_size, image_size))

    tensor = torch.tensor(resized_image)
    tensor = tensor.permute(2, 0, 1)
    tensor = tensor.float()
    tensor = tensor.unsqueeze(0)
    tensor = tensor / 255.0

    return image, tensor


def _compute_blur_score(image):
    # I use the Laplacian variance here because blur can often be estimated by
    # how much edge detail remains in the image.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur_fraction = laplacian_variance / 400.0

    if blur_fraction > 1.0:
        blur_fraction = 1.0

    blur_score = 1.0 - blur_fraction
    blur_score = max(0.0, min(1.0, blur_score))
    return float(blur_score)


def _compute_ocr_score(image):
    # I create a rough document-text quality score here because document fraud
    # images often look abnormal in how foreground text and background separate.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    non_zero_ratio = float(np.count_nonzero(thresholded)) / float(thresholded.size)
    black_ratio = 1.0 - non_zero_ratio

    distance_from_expected = abs(black_ratio - 0.18) / 0.18
    if distance_from_expected > 1.0:
        distance_from_expected = 1.0

    ocr_score = 1.0 - distance_from_expected
    ocr_score = max(0.0, min(1.0, ocr_score))
    return float(ocr_score)


def _compute_metadata_score(image_path, metadata):
    # I use metadata as an extra fraud clue because suspicious file size or
    # suspicious source information can support the visual model output.
    path = Path(image_path)
    file_size_bytes = path.stat().st_size
    file_size_mb = file_size_bytes / (1024 * 1024)
    size_score = 0.0 if 0.02 <= file_size_mb <= 8.0 else 0.6

    metadata_score = size_score
    if metadata:
        suspicious_flag = bool(metadata.get("suspicious", False))
        was_edited = bool(metadata.get("was_edited", False))
        source_value = metadata.get("source", "")
        source = str(source_value).lower()

        if suspicious_flag:
            metadata_score += 0.3
        if was_edited:
            metadata_score += 0.3
        if source in {"unknown", "external", "untrusted"}:
            metadata_score += 0.2

    metadata_score = max(0.0, min(1.0, metadata_score))
    return float(metadata_score)


def predict_cv_fraud(image_path, metadata=None):
    # I keep the full CV prediction flow in one function so the API router can
    # call one service entry point instead of managing CV details itself.
    model = _load_cv_model_once()
    if model is None:
        raise RuntimeError(_cv_model_error or "CV model could not be loaded.")

    raw_image, image_tensor = _prepare_image(image_path)
    device = next(model.parameters()).device
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        # I use no_grad because this is inference, not training, so I do not
        # need PyTorch to track gradients.
        logits = model(image_tensor)
        probability = torch.sigmoid(logits)
        model_score = float(probability.item())

    blur_score = _compute_blur_score(raw_image)
    ocr_score = _compute_ocr_score(raw_image)
    metadata_score = _compute_metadata_score(image_path, metadata)

    fraud_score = compute_fraud_score(
        model_score=model_score,
        blur_score=blur_score,
        ocr_score=ocr_score,
        metadata_score=metadata_score,
    )

    # I turn the numeric score into a simple verdict because the wider project
    # often needs both a detailed score and a human-friendly summary.
    verdict = "fraud_suspected" if fraud_score >= 0.5 else "likely_genuine"

    details = {}
    details["model_score"] = model_score
    details["blur_score"] = blur_score
    details["ocr_score"] = ocr_score
    details["metadata_score"] = metadata_score

    result = {}
    result["fraud_score"] = fraud_score
    result["verdict"] = verdict
    result["details"] = details
    result["model_path"] = str(CV_CNN_MODEL)
    return result
