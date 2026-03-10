from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    # Resolve paths based on this file location (src/backend)
    backend_dir: Path = Path(__file__).resolve().parent
    src_dir: Path = backend_dir.parent
    project_root: Path = src_dir.parent

    # Data files (based on your paths)
    data_dir: Path = project_root / "data"
    card_csv: Path = data_dir / "card_transdata.csv"
    financial_csv: Path = data_dir / "financial_fraud_detection_dataset 2.csv"
    sms_corpus: Path = data_dir / "SMSSpamCollection"

    # Outputs
    outputs_dir: Path = backend_dir / "outputs"
    risk_chart: Path = outputs_dir / "risk_visualization.png"

    # Thresholds for simple heuristics (beginner friendly)
    heuristic_threshold: float = 0.65


cfg = Config()
cfg.outputs_dir.mkdir(parents=True, exist_ok=True)