import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

from src.api.logger import logger
from src.scoring.fraud_score import compute_fraud_score
from src.train.model_paths import CV_CNN_MODEL

cv2.setNumThreads(1)
_cv_runtime_probe = None


def _prepare_image(image_path, image_size=224):
    # I keep image preparation in one helper so every CV check starts from the
    # same resized version of the input image.
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not read image at: {image_path}")

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized_image = cv2.resize(rgb_image, (image_size, image_size))
    return image, resized_image


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
    # suspicious source information can support the visual score.
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


def _compute_heuristic_model_score(image):
    # I use a simple image-statistics proxy here so the CV route can keep
    # working even when the heavier Torch runtime is unavailable.
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    contrast = float(grayscale.std()) / 64.0
    brightness = abs((float(grayscale.mean()) / 255.0) - 0.5) / 0.5

    contrast = max(0.0, min(1.0, contrast))
    brightness = max(0.0, min(1.0, brightness))
    heuristic_score = (0.7 * (1.0 - contrast)) + (0.3 * brightness)
    return float(max(0.0, min(1.0, heuristic_score)))


def _probe_cv_runtime():
    # I check the deep-learning runtime in a separate Python process because a
    # broken Torch import can terminate the child process without crashing the
    # main API process.
    global _cv_runtime_probe
    if _cv_runtime_probe is not None:
        return _cv_runtime_probe

    image_path = Path(CV_CNN_MODEL)
    if not image_path.exists():
        _cv_runtime_probe = {
            "mode": "heuristic_fallback",
            "reason": "I could not find the saved CV model artifact.",
        }
        return _cv_runtime_probe

    command = [
        sys.executable,
        "-m",
        "src.scoring.cv_deep_learning_runner",
        "--image-path",
        "data/processed/cv/test/original/img_00185_orig.jpg",
    ]

    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout.strip())
        _cv_runtime_probe = {
            "mode": payload["cv_mode"],
            "reason": "I can run the full Torch CV path.",
        }
    except Exception as exc:
        _cv_runtime_probe = {
            "mode": "heuristic_fallback",
            "reason": f"I could not run the Torch CV path. Reason: {exc}",
        }

    return _cv_runtime_probe


def get_cv_runtime_status():
    # I expose the runtime mode here so readiness checks and the API can report
    # clearly whether I am using deep learning or the safer fallback mode.
    runtime = _probe_cv_runtime()
    status = "ready" if runtime["mode"] == "deep_learning" else "fallback"
    return {
        "name": "CV inference runtime",
        "mode": runtime["mode"],
        "required": False,
        "available": True,
        "status": status,
        "reason": runtime["reason"],
    }


def _run_deep_learning_model_score(image_path: str) -> float:
    # I run the heavier Torch inference path in a subprocess so the main API
    # can stay alive even if the local Torch runtime is unstable.
    command = [
        sys.executable,
        "-m",
        "src.scoring.cv_deep_learning_runner",
        "--image-path",
        image_path,
    ]
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout.strip())
    return float(payload["model_score"])


def predict_cv_fraud(image_path, metadata=None):
    # I keep the full CV prediction flow in one function so the API router can
    # call one service entry point instead of managing CV details itself.
    raw_image, _ = _prepare_image(image_path)
    runtime = _probe_cv_runtime()

    # I use deep learning when the Torch runtime works, and I fall back to the
    # safer heuristic mode only when the deep-learning path is unavailable.
    if runtime["mode"] == "deep_learning":
        logger.info("I am using the deep-learning CV scoring path for %s.", image_path)
        model_score = _run_deep_learning_model_score(image_path)
        cv_mode = "deep_learning"
    else:
        logger.info(
            "I am using the heuristic CV scoring path for %s because the deep-learning runtime is unavailable.",
            image_path,
        )
        model_score = _compute_heuristic_model_score(raw_image)
        cv_mode = "heuristic_fallback"

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
    detected_anomalies = []
    explanations = []

    if model_score >= 0.6:
        detected_anomalies.append("visual_pattern_mismatch")
        explanations.append("I found a strong visual anomaly score from the main CV model path.")
    if blur_score >= 0.55:
        detected_anomalies.append("blur_or_quality_issue")
        explanations.append("I found blur or image-quality issues that make the document look less trustworthy.")
    if ocr_score <= 0.35:
        detected_anomalies.append("text_region_irregularity")
        explanations.append("I found text-region behaviour that does not match the expected document balance.")
    if metadata_score >= 0.4:
        detected_anomalies.append("metadata_context_risk")
        explanations.append("I found metadata clues that increase document risk, such as suspicious source or edit history.")

    if not explanations:
        explanations.append("I did not find strong suspicious visual evidence in this document image.")

    confidence = 1.0 - (max(model_score, blur_score, ocr_score, metadata_score) - min(model_score, blur_score, ocr_score, metadata_score))
    confidence = float(max(0.2, min(0.98, confidence)))

    details = {}
    details["model_score"] = model_score
    details["blur_score"] = blur_score
    details["ocr_score"] = ocr_score
    details["metadata_score"] = metadata_score
    details["cv_mode"] = cv_mode

    result = {}
    result["fraud_score"] = fraud_score
    result["verdict"] = verdict
    result["confidence"] = confidence
    result["detected_anomalies"] = detected_anomalies
    result["explanations"] = explanations
    result["evidence_summary"] = (
        "I combined the main visual score, blur score, text-region score, "
        "and metadata score to explain this document result."
    )
    result["details"] = details
    result["model_path"] = str(CV_CNN_MODEL)
    return result
