from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/predict", tags=["prediction"])


class TransactionFeatures(BaseModel):
    ratio_to_median_purchase_price: float = Field(..., ge=0)
    distance_from_home: float = Field(..., ge=0)
    price_threshold: float = Field(3.0, ge=0)
    distance_threshold: float = Field(100.0, ge=0)


@router.post("/transaction")
def predict_transaction(payload: TransactionFeatures):
    """Simple baseline scoring endpoint until a trained model is wired in."""
    risk_score = 0
    if payload.ratio_to_median_purchase_price > payload.price_threshold:
        risk_score += 1
    if payload.distance_from_home > payload.distance_threshold:
        risk_score += 1

    risk_level = "low"
    if risk_score == 1:
        risk_level = "medium"
    elif risk_score == 2:
        risk_level = "high"

    return {"risk_score": risk_score, "risk_level": risk_level}
