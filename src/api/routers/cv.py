from typing import Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from src.scoring.cv_fraud_service import predict_cv_fraud

router = APIRouter(prefix="/cv", tags=["cv"])


class CVPredictIn(BaseModel):
    image_path: str
    metadata: Optional[Dict[str, float | int | str | bool]] = None


@router.post("/predict")
def predict_document(payload: CVPredictIn):
    return predict_cv_fraud(payload.image_path, metadata=payload.metadata)
