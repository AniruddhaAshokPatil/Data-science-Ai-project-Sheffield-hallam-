from pathlib import Path
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/cv", tags=["cv"])


class CVPredictIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # I ask for an image path because this route passes document images into
    # the CV fraud service, and the service needs to know which file to read.
    image_path: str
    # I keep metadata optional because some CV checks can use extra context,
    # but I still want the route to work when only an image is provided.
    metadata: Optional[Dict[str, float | int | str | bool]] = None


@router.post("/predict")
def predict_document(payload: CVPredictIn):
    # I keep this route thin on purpose. The router should expose the API,
    # while the actual scoring logic lives in the shared CV service layer.
    from src.scoring.cv_fraud_service import predict_cv_fraud

    image_path = Path(payload.image_path)
    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"I could not find the image at {image_path}.",
        )

    try:
        return predict_cv_fraud(str(image_path), metadata=payload.metadata)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
