import logging
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)

# I keep baseline statistics from training here because drift only means
# something when I compare live traffic against the project’s original norms.
baseline_stats = {
    "score_mean": 0.2,
    "score_std": 0.1,
    "feature_means": {},
}

# I store recent observations in memory because this lightweight service is
# meant to give the dashboard a quick health signal without extra setup.
recent_scores: List[float] = []
recent_features: List[Dict[str, float]] = []

# -------------------------------
# CONFIG
# -------------------------------

WINDOW_SIZE = 100
DRIFT_THRESHOLD = 0.15

def update_monitoring(score: float, features: Dict[str, float]) -> None:
    """
    I store the latest model output and feature snapshot so the project can
    compare current behaviour against the training baseline over time.
    """
    recent_scores.append(float(score))
    recent_features.append({key: float(value) for key, value in features.items()})

    # I keep the monitoring window fixed so old behaviour does not outweigh
    # what the system is doing right now in production-like traffic.
    if len(recent_scores) > WINDOW_SIZE:
        recent_scores.pop(0)
        recent_features.pop(0)


def _calculate_feature_drift() -> float:
    # I compare each live feature mean against its own training mean because
    # that tells me far more than averaging raw feature values together.
    if not recent_features:
        return 0.0

    baseline_feature_means = baseline_stats.get("feature_means") or {}
    if not baseline_feature_means:
        return 0.0

    common_features = [
        feature_name
        for feature_name in baseline_feature_means
        if all(feature_name in feature_row for feature_row in recent_features)
    ]

    if not common_features:
        return 0.0

    live_feature_means = {
        feature_name: float(
            np.mean([feature_row[feature_name] for feature_row in recent_features])
        )
        for feature_name in common_features
    }

    normalized_drifts = []
    for feature_name in common_features:
        baseline_mean = float(baseline_feature_means[feature_name])
        live_mean = live_feature_means[feature_name]
        scale = max(abs(baseline_mean), 1e-6)
        normalized_drifts.append(abs(live_mean - baseline_mean) / scale)

    return float(np.mean(normalized_drifts))


def detect_drift() -> Dict[str, float | bool | str | int]:
    """
    I compare recent predictions against the stored baseline so the project can
    catch model drift before a dashboard user trusts stale behaviour.
    """

    if len(recent_scores) < WINDOW_SIZE:
        return {
            "status": "insufficient_data",
            "samples_seen": len(recent_scores),
            "samples_required": WINDOW_SIZE,
        }

    current_mean = np.mean(recent_scores)
    baseline_mean = baseline_stats["score_mean"]
    score_drift = abs(current_mean - baseline_mean)
    feature_drift = _calculate_feature_drift()
    drift_flag = (score_drift > DRIFT_THRESHOLD) or (feature_drift > DRIFT_THRESHOLD)

    if drift_flag:
        logger.warning(
            "Drift detected: score_drift=%.4f feature_drift=%.4f",
            score_drift,
            feature_drift,
        )

    return {
        "status": "ok",
        "drift": drift_flag,
        "score_drift": float(score_drift),
        "feature_drift": float(feature_drift),
        "samples_seen": len(recent_scores),
    }
