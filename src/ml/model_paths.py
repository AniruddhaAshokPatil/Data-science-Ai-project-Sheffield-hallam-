from pathlib import Path

# This file centralizes model save locations
ml_dir = Path(__file__).resolve().parent
artifacts_dir = ml_dir / "artifacts"
artifacts_dir.mkdir(exist_ok=True)

TABULAR_MODEL = artifacts_dir / "tabular_fraud_model.joblib"
ANOMALY_MODEL = artifacts_dir / "isolation_forest.joblib"
PREPROCESSOR = artifacts_dir / "preprocessor.joblib"
