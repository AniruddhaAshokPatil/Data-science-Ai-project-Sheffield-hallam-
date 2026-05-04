from fastapi import APIRouter

from src.api.config import settings
from src.api.db import database_ready

router = APIRouter(tags=["health"])


@router.get("/health/live")
def health_live() -> dict:
    # Liveness only confirms that the API process can respond.
    return {"status": "ok"}


@router.get("/health/ready")
def health_ready() -> dict:
    # Readiness checks the local resources needed by the app before it handles real traffic.
    checks = {
        "database_ready": database_ready(),
        "claims_dataset_present": settings.CLAIMS_DATA_PATH.exists(),
        "uploads_directory_ready": settings.EVIDENCE_UPLOADS_DIR.exists(),
    }
    status = "ok" if all(checks.values()) else "degraded"
    return {"status": status, "checks": checks}
