# src/scoring/fraud_score.py

DEFAULT_WEIGHTS = {
    "model_score": 0.5,
    "blur_score": 0.2,
    "ocr_score": 0.2,
    "metadata_score": 0.1,
}


def _normalize_score(name, value):
    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric value.") from exc

    if score < 0:
        return 0.0
    if score > 1:
        return 1.0
    return score


def compute_fraud_score(
    model_score,
    blur_score,
    ocr_score,
    metadata_score,
    weights=None,
):
    scores = {
        "model_score": _normalize_score("model_score", model_score),
        "blur_score": _normalize_score("blur_score", blur_score),
        "ocr_score": _normalize_score("ocr_score", ocr_score),
        "metadata_score": _normalize_score("metadata_score", metadata_score),
    }

    active_weights = DEFAULT_WEIGHTS.copy()
    if weights is not None:
        active_weights.update(weights)

    total_weight = sum(active_weights.values())
    if total_weight <= 0:
        raise ValueError("Fraud score weights must sum to a positive value.")

    weighted_sum = sum(scores[name] * active_weights[name] for name in scores)
    return weighted_sum / total_weight
