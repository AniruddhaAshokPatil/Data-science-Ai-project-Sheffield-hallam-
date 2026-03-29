# src/scoring/fraud_score.py

# I keep the default weights in one dictionary so the CV fraud service can
# combine several clues into one score without scattering numbers everywhere.
DEFAULT_WEIGHTS = {
    "model_score": 0.5,
    "blur_score": 0.2,
    "ocr_score": 0.2,
    "metadata_score": 0.1,
}


def _normalize_score(name, value):
    # I normalize each score input here because the final fraud score should
    # work with clean numeric values inside the 0 to 1 range.
    try:
        numeric_score = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric value.") from exc

    if numeric_score < 0:
        return 0.0
    if numeric_score > 1:
        return 1.0
    return numeric_score


def compute_fraud_score(
    model_score,
    blur_score,
    ocr_score,
    metadata_score,
    weights=None,
):
    # I build a score dictionary first because it is easier to validate each
    # component before I blend them into one final fraud score.
    scores = {
        "model_score": _normalize_score("model_score", model_score),
        "blur_score": _normalize_score("blur_score", blur_score),
        "ocr_score": _normalize_score("ocr_score", ocr_score),
        "metadata_score": _normalize_score("metadata_score", metadata_score),
    }

    # I copy the defaults so callers can override weights for experiments
    # without permanently changing the shared project defaults.
    active_weights = DEFAULT_WEIGHTS.copy()
    if weights is not None:
        active_weights.update(weights)

    total_weight = sum(active_weights.values())
    if total_weight <= 0:
        raise ValueError("Fraud score weights must sum to a positive value.")

    # I compute a weighted average so stronger fraud clues can contribute more
    # to the final score than weaker supporting signals.
    weighted_sum = 0.0
    for name, score_value in scores.items():
        weight_value = active_weights[name]
        weighted_sum += score_value * weight_value

    final_score = weighted_sum / total_weight
    return final_score
