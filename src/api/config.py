import os
from pathlib import Path


class Settings:
    # I resolve the repository root once so every API module can reuse the same paths.
    REPO_ROOT = Path(__file__).resolve().parents[2]
    CLAIMS_DATA_PATH = REPO_ROOT / "data" / "raw" / "insurance_claims" / "claim_history_detailed.csv"
    EVIDENCE_UPLOADS_DIR = Path(
        os.getenv("SHIELDWISE_EVIDENCE_UPLOADS_DIR", REPO_ROOT / "data" / "raw" / "insurance_claims" / "uploads")
    )
    DATABASE_PATH = Path(
        os.getenv("SHIELDWISE_DATABASE_PATH", REPO_ROOT / "data" / "processed" / "shieldwise_runtime.db")
    )
    API_ENV = os.getenv("SHIELDWISE_API_ENV", "development")
    DEBUG = os.getenv("SHIELDWISE_DEBUG", "false").lower() == "true"

    # I keep the allowed origins explicit so the React frontend can talk to the API in development.
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]


settings = Settings()
