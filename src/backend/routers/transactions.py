from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

from backend.risk_scoring import combined_risk
from backend.config import cfg

router = APIRouter(prefix="/transaction", tags=["transactions"])


class TransactionIn(BaseModel):
    features: Dict[str, float]
    text: Optional[str] = None  # optional text linked to transaction
    doc_id: Optional[str] = None  # optional document link/id


class TransactionOut(BaseModel):
    risk: float
    details: Dict[str, float]
    timestamp: str


@router.post("/predict", response_model=TransactionOut)
def predict_transaction(payload: TransactionIn):
    """
    Beginner-friendly heuristic using two common signals if present:
    - ratio_to_median_purchase_price
    - distance_from_home

    If they're missing, we fall back to a simple average of provided features.
    This is just to keep the API running while your ML models are being built.
    """
    x = payload.features
    # Try to use the two classic fraud signals if available
    ratio = float(x.get("ratio_to_median_purchase_price", 0.0))
    dist = float(x.get("distance_from_home", 0.0))

    # Very simple normalisation (demo only)
    # Scale ratio and distance into [0, 1] using rough constants
    ratio_norm = min(1.0, ratio / 5.0)   # assume 5x median is quite high
    dist_norm = min(1.0, dist / 1000.0)  # assume 1000 units is far

    # Combine them with a naive rule
    tabular_prob = (0.6 * ratio_norm) + (0.4 * dist_norm)

    # For now, we have no anomaly/text/doc scores wired here
    risk = combined_risk(
        xgb_prob=tabular_prob,
        anomaly_score=None,
        text_score=None,
        doc_score=None
    )

    return TransactionOut(
        risk=float(risk),
        details={
            "tabular_prob": float(tabular_prob),
            "ratio_norm": float(ratio_norm),
            "dist_norm": float(dist_norm),
            "threshold": float(cfg.heuristic_threshold),
        },
        timestamp=datetime.utcnow().isoformat(),
    )
