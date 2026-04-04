"""I keep the shared backend settings and project paths in this file."""

import os
from pathlib import Path
from pydantic import BaseModel


def _split_env_list(raw_value: str) -> list[str]:
    # I use one small helper here because more than one environment variable
    # stores comma-separated values, and I want one clear parsing rule.
    cleaned_values = []
    for item in raw_value.split(","):
        stripped_item = item.strip()
        if stripped_item:
            cleaned_values.append(stripped_item)

    if cleaned_values:
        return cleaned_values
    return ["*"]


class Config(BaseModel):
    # I resolve paths from this file location so the project can find data
    # and outputs without depending on hardcoded paths for one machine only.
    backend_dir: Path = Path(__file__).resolve().parent
    src_dir: Path = backend_dir.parent
    project_root: Path = src_dir.parent

    # I keep shared dataset paths here because multiple API files need them,
    # and this gives me one central place to update if the layout changes.
    data_dir: Path = project_root / "data"
    raw_data_dir: Path = data_dir / "raw"
    raw_transactions_dir: Path = raw_data_dir / "transactions"
    processed_transactions_dir: Path = data_dir / "processed" / "transactions"
    card_csv: Path = processed_transactions_dir / "clean_validation.csv"
    financial_csv: Path = processed_transactions_dir / "clean_main.csv"
    financial_raw_csv: Path = raw_transactions_dir / "financial_fraud_detection_dataset.csv"
    sms_corpus: Path = raw_data_dir / "nlp" / "SMSSpamCollection.csv"

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
    trusted_hosts: list[str] = ["*"]
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    @classmethod
    def from_env(cls) -> "Config":
        # I read deployment settings from environment variables here so the
        # same code can run locally, in staging, or in production cleanly.
        heuristic_threshold = float(os.getenv("FRAUD_HEURISTIC_THRESHOLD", "0.65"))
        app_env = os.getenv("FRAUD_APP_ENV", "development")
        log_level = os.getenv("FRAUD_LOG_LEVEL", "INFO").upper()
        app_version = os.getenv("FRAUD_APP_VERSION", "1.0.0")
        rate_limit_requests = int(os.getenv("FRAUD_RATE_LIMIT_REQUESTS", "120"))
        rate_limit_window_seconds = int(os.getenv("FRAUD_RATE_LIMIT_WINDOW_SECONDS", "60"))

        origins_raw = os.getenv("FRAUD_ALLOWED_ORIGINS", "*")
        allowed_origins = _split_env_list(origins_raw)
        trusted_hosts_raw = os.getenv("FRAUD_TRUSTED_HOSTS", "*")
        trusted_hosts = _split_env_list(trusted_hosts_raw)

        return cls(
            heuristic_threshold=heuristic_threshold,
            app_env=app_env,
            log_level=log_level,
            app_version=app_version,
            allowed_origins=allowed_origins,
            trusted_hosts=trusted_hosts,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window_seconds=rate_limit_window_seconds,
        )


# I create one shared config object so other files can import `cfg`
# instead of rebuilding the same paths and settings each time.
cfg = Config.from_env()
cfg.outputs_dir.mkdir(parents=True, exist_ok=True)
