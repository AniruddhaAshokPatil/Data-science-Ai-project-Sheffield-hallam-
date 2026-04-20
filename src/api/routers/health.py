from fastapi import APIRouter

from src.api.config import settings
from src.api.db import database_ready

router = APIRouter(tags=["health"])


@router.get("/health/live")
def health_live() -> dict:
    # I keep the liveness endpoint minimal so deployment and smoke checks stay stable.
    return {"status": "ok"}


@router.get("/health/ready")
def health_ready() -> dict:
    # I verify the runtime dependencies here so deployments can fail fast if storage or data paths are missing.
    checks = {
        "database_ready": database_ready(),
        "claims_dataset_present": settings.CLAIMS_DATA_PATH.exists(),
        "uploads_directory_ready": settings.EVIDENCE_UPLOADS_DIR.exists(),
    }
    status = "ok" if all(checks.values()) else "degraded"
    return {"status": status, "checks": checks}
