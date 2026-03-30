from pathlib import Path

# I centralize model save locations in one file so the training, loading, and
# API code all agree on where artifacts belong.
train_dir = Path(__file__).resolve().parent
artifacts_dir = train_dir / "artifacts"
artifacts_dir.mkdir(exist_ok=True)

TABULAR_MODEL = artifacts_dir / "tabular_fraud_model.joblib"
ANOMALY_MODEL = artifacts_dir / "isolation_forest.joblib"
ANOMALY_METADATA = artifacts_dir / "isolation_forest.metadata.pkl"
PREPROCESSOR = artifacts_dir / "preprocessor.joblib"
CV_CNN_MODEL = artifacts_dir / "simple_cnn.pth"
NLP_MODEL = artifacts_dir / "sms_model.joblib"
NLP_VECTORIZER = artifacts_dir / "sms_vectorizer.joblib"
