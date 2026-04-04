from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional

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
    context: Optional[Dict[str, str | float | int | bool]] = None

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
    details: Dict[str, Any]
    timestamp: str
    profile: str
    verdict: str
    scenario: str
    explanations: list[str]
    feature_importance: list[Dict[str, Any]]


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

_receiver_history = defaultdict(int)
_device_history = defaultdict(int)
_ip_history = defaultdict(int)


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


def _safe_lower(value: Any) -> str:
    # I convert optional context values into lowercase strings here so the
    # explanation rules can compare values safely.
    if value is None:
        return ""
    return str(value).strip().lower()


def _parse_transaction_timestamp(raw_value: Any) -> datetime:
    # I parse the transaction timestamp here because the dashboard may send a
    # custom time, but I still want a safe fallback for older clients.
    if raw_value is None:
        return datetime.now(timezone.utc)

    try:
        parsed = datetime.fromisoformat(str(raw_value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _build_financial_context_details(
    features: Dict[str, float],
    context: Optional[Dict[str, str | float | int | bool]],
) -> Dict[str, float]:
    # I derive time and repetition signals here because those clues help me
    # explain how a risky transaction fits into a wider fraud pattern.
    context = context or {}
    transaction_time = _parse_transaction_timestamp(context.get("timestamp"))
    hour_value = float(transaction_time.hour)
    is_night = 1.0 if transaction_time.hour < 6 or transaction_time.hour >= 23 else 0.0

    receiver_account = str(context.get("receiver_account", "")).strip()
    device_hash = str(context.get("device_hash", "")).strip()
    ip_address = str(context.get("ip_address", "")).strip()

    repeated_receiver_count = float(_receiver_history[receiver_account]) if receiver_account else 0.0
    repeated_device_count = float(_device_history[device_hash]) if device_hash else 0.0
    repeated_ip_count = float(_ip_history[ip_address]) if ip_address else 0.0

    max_repeat = max(repeated_receiver_count, repeated_device_count, repeated_ip_count, 0.0)
    repeat_entity_score = _clamp01(max_repeat / 5.0)

    transaction_type = _safe_lower(context.get("transaction_type"))
    merchant_category = _safe_lower(context.get("merchant_category"))
    location = _safe_lower(context.get("location"))
    device_used = _safe_lower(context.get("device_used"))
    payment_channel = _safe_lower(context.get("payment_channel"))

    online_context_score = 1.0 if merchant_category == "online" and device_used == "web" else 0.0
    transfer_context_score = 1.0 if transaction_type == "transfer" else 0.0
    remote_channel_score = 1.0 if payment_channel in {"wire_transfer", "upi"} else 0.0
    cross_border_score = 1.0 if location in {"tokyo", "dubai", "singapore", "sydney"} else 0.0

    details = {
        "transaction_hour": hour_value,
        "night_activity_score": float(is_night),
        "repeat_entity_score": float(repeat_entity_score),
        "repeated_receiver_count": float(repeated_receiver_count),
        "repeated_device_count": float(repeated_device_count),
        "repeated_ip_count": float(repeated_ip_count),
        "online_context_score": float(online_context_score),
        "transfer_context_score": float(transfer_context_score),
        "remote_channel_score": float(remote_channel_score),
        "cross_border_score": float(cross_border_score),
    }

    if receiver_account:
        _receiver_history[receiver_account] += 1
    if device_hash:
        _device_history[device_hash] += 1
    if ip_address:
        _ip_history[ip_address] += 1

    return details


def _build_verdict(risk: float) -> str:
    # I keep verdict mapping in one helper so the API returns a clearer label
    # than a bare number when people review the result.
    if risk >= 0.65:
        return "HIGH_RISK"
    if risk >= 0.35:
        return "REVIEW"
    return "SAFE"


def _build_scenario(
    profile_name: str,
    details: Dict[str, Any],
    context: Optional[Dict[str, str | float | int | bool]],
) -> str:
    # I choose one simple fraud story here so the result is easier to explain
    # than a long list of disconnected clues.
    context = context or {}
    merchant_category = _safe_lower(context.get("merchant_category"))
    device_used = _safe_lower(context.get("device_used"))

    if profile_name == "financial":
        if details["velocity_norm"] >= 0.7 and details["geo_norm"] >= 0.7:
            return "Account Takeover"
        if merchant_category == "online" and device_used == "web" and details["spending_dev_norm"] >= 0.5:
            return "Card Not Present Fraud"
        if details["amount_norm"] <= 0.08 and details["velocity_norm"] >= 0.7:
            return "Card Testing"
        if details["transfer_context_score"] >= 1.0 and details["amount_norm"] >= 0.7:
            return "Rapid Fund Movement"
        return "Normal Behaviour"

    if profile_name == "card" and details["ratio_norm"] >= 0.6 and details["dist_norm"] >= 0.5:
        return "Card Not Present Fraud"
    return "Normal Behaviour"


def _build_feature_importance(
    profile_name: str,
    features: Dict[str, float],
    details: Dict[str, Any],
    context: Optional[Dict[str, str | float | int | bool]],
) -> list[Dict[str, Any]]:
    # I translate the internal scores into an ordered explanation list here so
    # the frontend can render a clear feature-attribution table.
    feature_rows = []

    if profile_name == "financial":
        mapping = [
            ("amount", features.get("amount", 0.0), details.get("amount_norm", 0.0)),
            ("spending_deviation_score", features.get("spending_deviation_score", 0.0), details.get("spending_dev_norm", 0.0)),
            ("velocity_score", features.get("velocity_score", 0.0), details.get("velocity_norm", 0.0)),
            ("geo_anomaly_score", features.get("geo_anomaly_score", 0.0), details.get("geo_norm", 0.0)),
            ("night_activity", details.get("transaction_hour", 0.0), details.get("night_activity_score", 0.0)),
            ("repeat_entity", max(details.get("repeated_receiver_count", 0.0), details.get("repeated_device_count", 0.0), details.get("repeated_ip_count", 0.0)), details.get("repeat_entity_score", 0.0)),
            ("online_context", _safe_lower((context or {}).get("merchant_category", "")) or "none", details.get("online_context_score", 0.0)),
        ]
    else:
        mapping = [
            ("ratio_to_median_purchase_price", features.get("ratio_to_median_purchase_price", 0.0), details.get("ratio_norm", 0.0)),
            ("distance_from_home", features.get("distance_from_home", 0.0), details.get("dist_norm", 0.0)),
        ]

    for feature_name, raw_value, contribution_value in mapping:
        numeric_value = float(contribution_value)
        feature_rows.append(
            {
                "feature": feature_name,
                "value": raw_value,
                "contribution": round(numeric_value, 3),
                "effect": "Risk increasing" if numeric_value >= 0.45 else "Risk reducing",
            }
        )

    feature_rows.sort(key=lambda item: item["contribution"], reverse=True)
    return feature_rows


def _build_explanations(
    profile_name: str,
    details: Dict[str, Any],
    scenario: str,
    verdict: str,
    context: Optional[Dict[str, str | float | int | bool]],
) -> list[str]:
    # I assemble short explanations here so the API can explain the decision
    # with plain statements that fit the frontend and the project demo.
    context = context or {}
    explanations = [f"I classified this case as {scenario} with a {verdict.lower()} verdict."]

    if profile_name == "financial":
        if details["velocity_norm"] >= 0.6:
            explanations.append("I increased the risk because the transaction velocity looks unusually high.")
        if details["geo_norm"] >= 0.6:
            explanations.append("I increased the risk because the geographic anomaly score suggests an unusual location pattern.")
        if details["spending_dev_norm"] >= 0.5:
            explanations.append("I increased the risk because the spending pattern differs from the expected customer behaviour.")
        if details.get("night_activity_score", 0.0) >= 1.0:
            explanations.append("I added extra concern because the transaction happened during a higher-risk night-time window.")
        if details.get("repeat_entity_score", 0.0) >= 0.4:
            explanations.append("I added repeated-entity risk because this receiver, device, or IP has appeared before.")
        if details.get("online_context_score", 0.0) >= 1.0:
            explanations.append("I recognised an online web context that matches common card-not-present fraud patterns.")
        if _safe_lower(context.get("payment_channel")) in {"wire_transfer", "upi"}:
            explanations.append("I treated the payment channel as more sensitive because fast remote channels can be abused for fraud.")
    else:
        if details["ratio_norm"] >= 0.6:
            explanations.append("I increased the risk because the purchase ratio is high compared with the normal baseline.")
        if details["dist_norm"] >= 0.5:
            explanations.append("I increased the risk because the transaction is far from the usual home area.")

    return explanations


def score_transaction_features(
    features: Dict[str, float],
    context: Optional[Dict[str, str | float | int | bool]] = None,
) -> TransactionOut:
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
        details.update(_build_financial_context_details(features, context))
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
    verdict = _build_verdict(float(risk))
    scenario = _build_scenario(profile_name, details, context)
    feature_importance = _build_feature_importance(profile_name, features, details, context)
    explanations = _build_explanations(profile_name, details, scenario, verdict, context)
    details["verdict_score_band"] = verdict.lower()

    return TransactionOut(
        risk=float(risk),
        details=details,
        timestamp=datetime.now(timezone.utc).isoformat(),
        profile=profile_name,
        verdict=verdict,
        scenario=scenario,
        explanations=explanations,
        feature_importance=feature_importance,
    )


@router.post("/predict", response_model=TransactionOut)
def predict_transaction(payload: TransactionIn):
    """
    I expose this route so the rest of the project can ask for a transaction
    fraud score through the API instead of calling scoring functions directly.
    """
    return score_transaction_features(payload.features, context=payload.context)
