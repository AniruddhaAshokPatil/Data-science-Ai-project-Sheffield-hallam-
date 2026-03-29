import os
from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    # I resolve paths from this file location so the project can find data
    # and outputs without depending on hardcoded paths for one machine only.
    backend_dir: Path = Path(__file__).resolve().parent
    src_dir: Path = backend_dir.parent
    project_root: Path = src_dir.parent

    # I keep shared dataset paths here because multiple API files need them,
    # and this gives me one central place to update if the layout changes.
    data_dir: Path = project_root / "data"
    processed_transactions_dir: Path = data_dir / "processed" / "transactions"
    card_csv: Path = processed_transactions_dir / "clean_validation.csv"
    financial_csv: Path = processed_transactions_dir / "clean_main.csv"
    sms_corpus: Path = data_dir / "SMSSpamCollection"

    # I keep output locations here for the same reason: analytics and visual
    # files should be saved consistently across the backend.
    outputs_dir: Path = backend_dir / "outputs"
    risk_chart: Path = outputs_dir / "risk_visualization.png"

    # I store a shared threshold here because several scoring paths may need
    # the same idea of what counts as suspicious.
    heuristic_threshold: float = 0.65
    app_env: str = "development"
    log_level: str = "INFO"
    app_version: str = "1.0.0"
    allowed_origins: list[str] = ["*"]

    @classmethod
    def from_env(cls) -> "Config":
        # I read deployment settings from environment variables here so the
        # same code can run locally, in staging, or in production cleanly.
        heuristic_threshold = float(
            os.getenv("FRAUD_HEURISTIC_THRESHOLD", "0.65")
        )
        app_env = os.getenv("FRAUD_APP_ENV", "development")
        log_level = os.getenv("FRAUD_LOG_LEVEL", "INFO").upper()
        app_version = os.getenv("FRAUD_APP_VERSION", "1.0.0")

        origins_raw = os.getenv("FRAUD_ALLOWED_ORIGINS", "*")
        allowed_origins = [
            origin.strip() for origin in origins_raw.split(",") if origin.strip()
        ] or ["*"]

        return cls(
            heuristic_threshold=heuristic_threshold,
            app_env=app_env,
            log_level=log_level,
            app_version=app_version,
            allowed_origins=allowed_origins,
        )


# I create one shared config object so other files can import `cfg`
# instead of rebuilding the same paths and settings each time.
cfg = Config.from_env()
cfg.outputs_dir.mkdir(parents=True, exist_ok=True)
