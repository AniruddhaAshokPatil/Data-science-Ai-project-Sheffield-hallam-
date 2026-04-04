from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.api.config import cfg
from src.api.logger import logger
from src.api.risk_scoring import combined_risk

router = APIRouter(prefix="/transaction", tags=["transactions"])


class TransactionIn(BaseModel):
    # I use a Pydantic model here because I want FastAPI to validate
    # the incoming request shape for me before my scoring logic runs.
    model_config = ConfigDict(extra="forbid")

    features: Dict[str, float] = Field(..., min_length=1)
    text: Optional[str] = None  # optional text linked to transaction
    doc_id: Optional[str] = None  # optional document link/id

    @field_validator("features")
    @classmethod
    def validate_features(cls, features: Dict[str, float]) -> Dict[str, float]:
        # I reject empty and non-finite numbers here because production APIs
        # should fail fast on bad inputs instead of scoring nonsense payloads.
        cleaned_features: Dict[str, float] = {}
        for feature_name, feature_value in features.items():
            numeric_value = float(feature_value)
            if not (-1e308 < numeric_value < 1e308):
                raise ValueError(f"Feature '{feature_name}' must be finite.")
            cleaned_features[feature_name] = numeric_value

        if not cleaned_features:
            raise ValueError("I need at least one numeric feature to score.")

        return cleaned_features


class TransactionOut(BaseModel):
    # I use another Pydantic model for the response so my API always
    # returns a predictable structure to the frontend or any client.
    risk: float
    details: Dict[str, float]
    timestamp: str
    profile: str


# I keep these feature-name groups in sets because I only need to check
# whether certain keys exist in the payload. This helps me decide which
# scoring path matches the dataset shape I received.
CARD_FEATURE_KEYS = {
    "ratio_to_median_purchase_price",
    "distance_from_home",
}

FINANCIAL_FEATURE_KEYS = {
    "amount",
    "spending_deviation_score",
    "velocity_score",
    "geo_anomaly_score",
}


def _clamp01(value: float) -> float:
    # I clamp scores into the 0 to 1 range because risk-like values are
    # easier to combine when they all share the same scale.
    number = float(value)

    if number < 0.0:
        return 0.0
    if number > 1.0:
        return 1.0

    return number


def _score_card_features(features: Dict[str, float]) -> Dict[str, float]:
    # I keep the card scoring in its own function so this file stays easier
    # to read and so I can improve card logic later without affecting the
    # financial scoring branch.
    ratio_value = features.get("ratio_to_median_purchase_price", 0.0)
    distance_value = features.get("distance_from_home", 0.0)

    ratio = float(ratio_value)
    dist = float(distance_value)

    # I normalize raw values first because ratio and distance live on very
    # different scales. Converting them into 0 to 1 makes the combined score
    # easier for me to reason about as a beginner.
    ratio_norm = _clamp01(ratio / 5.0)
    dist_norm = _clamp01(dist / 1000.0)
    ratio_weight = 0.6
    distance_weight = 0.4
    tabular_prob = (ratio_weight * ratio_norm) + (distance_weight * dist_norm)

    details = {}
    details["tabular_prob"] = float(tabular_prob)
    details["ratio_norm"] = float(ratio_norm)
    details["dist_norm"] = float(dist_norm)
    details["feature_profile"] = 1.0
    details["recognized_features"] = float(len(feature_keys := CARD_FEATURE_KEYS & set(features)))
    return details


def _score_financial_features(features: Dict[str, float]) -> Dict[str, float]:
    # I separate financial scoring from card scoring because the processed
    # financial dataset has a different meaning and different fraud signals.
    amount_value = features.get("amount", 0.0)
    spending_value = features.get("spending_deviation_score", 0.0)
    velocity_value = features.get("velocity_score", 0.0)
    geo_value = features.get("geo_anomaly_score", 0.0)

    amount = float(amount_value)
    spending_dev = abs(float(spending_value))
    velocity = float(velocity_value)
    geo_anomaly = float(geo_value)
     # I use rough normalizations based on the financial dataset profile so the
    # values can contribute on a similar scale before I blend them together.
    amount_norm = _clamp01(amount / 1500.0)
    spending_dev_norm = _clamp01(spending_dev / 3.0)
    velocity_norm = _clamp01(velocity / 20.0)
    geo_norm = _clamp01(geo_anomaly)

    # I use explicit weights because each feature describes a different kind
    # of suspicious behavior, and I do not want one raw feature to dominate
    # the score just because its numeric range is larger.
    amount_weight = 0.30
    spending_weight = 0.25
    velocity_weight = 0.25
    geo_weight = 0.20

    tabular_prob = 0.0
    tabular_prob += amount_weight * amount_norm
    tabular_prob += spending_weight * spending_dev_norm
    tabular_prob += velocity_weight * velocity_norm
    tabular_prob += geo_weight * geo_norm

    details = {}
    details["tabular_prob"] = float(tabular_prob)
    details["amount_norm"] = float(amount_norm)
    details["spending_dev_norm"] = float(spending_dev_norm)
    details["velocity_norm"] = float(velocity_norm)
    details["geo_norm"] = float(geo_norm)
    details["feature_profile"] = 2.0
    details["recognized_features"] = float(
        len(FINANCIAL_FEATURE_KEYS & set(features))
    )
    return details


def score_transaction_features(features: Dict[str, float]) -> TransactionOut:
    """
    I use this shared scoring function so both HTTP requests and WebSocket
    transaction events can go through the same fraud logic in one place.
    """
    feature_keys = set(features)
    profile_name = "unknown"

    if feature_keys & CARD_FEATURE_KEYS:
        # I choose the card branch when I see the classic card-fraud features.
        details = _score_card_features(features)
        profile_name = "card"
    elif feature_keys & FINANCIAL_FEATURE_KEYS:
        # I choose the financial branch when the payload looks like the
        # processed financial dataset instead of the validation card dataset.
        details = _score_financial_features(features)
        profile_name = "financial"
    else:
        logger.warning(
            "I received an unsupported transaction feature payload: %s",
            sorted(feature_keys),
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "I could not match this payload to a supported transaction "
                "feature profile."
            ),
        )

    # I call the shared risk combiner here because this project is designed
    # to eventually merge tabular, anomaly, NLP, and CV signals together.
    risk = combined_risk(
        xgb_prob=details["tabular_prob"],
        anomaly_score=None,
        text_score=None,
        doc_score=None
    )

    details["threshold"] = float(cfg.heuristic_threshold)

    return TransactionOut(
        risk=float(risk),
        details=details,
        timestamp=datetime.now(timezone.utc).isoformat(),
        profile=profile_name,
    )


@router.post("/predict", response_model=TransactionOut)
def predict_transaction(payload: TransactionIn):
    """
    I expose this route so the rest of the project can ask for a transaction
    fraud score through the API instead of calling scoring functions directly.
    """
    return score_transaction_features(payload.features)
