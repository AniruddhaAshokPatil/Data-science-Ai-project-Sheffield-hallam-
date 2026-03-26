from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    # Resolve paths based on this file location (src/api)
    backend_dir: Path = Path(__file__).resolve().parent
    src_dir: Path = backend_dir.parent
    project_root: Path = src_dir.parent

    # Data files (based on your paths)
    data_dir: Path = project_root / "data"
    processed_transactions_dir: Path = data_dir / "processed" / "transactions"
    card_csv: Path = processed_transactions_dir / "clean_validation.csv"
    financial_csv: Path = processed_transactions_dir / "clean_main.csv"
    sms_corpus: Path = data_dir / "SMSSpamCollection"

    # Outputs
    outputs_dir: Path = backend_dir / "outputs"
    risk_chart: Path = outputs_dir / "risk_visualization.png"

    # Thresholds for simple heuristics (beginner friendly)
    heuristic_threshold: float = 0.65


cfg = Config()
cfg.outputs_dir.mkdir(parents=True, exist_ok=True)
