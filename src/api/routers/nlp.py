from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path

from src.api.logger import logger
from src.api.config import cfg

router = APIRouter(prefix="/nlp", tags=["nlp"])

# Try to import sklearn and prepare a tiny model at startup
_nlp_ready = False
_vec = None
_model = None

try:
    import pandas as pd
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB

    sms_path = Path(cfg.sms_corpus)
    if sms_path.exists():
        df = pd.read_csv(sms_path, sep="\t", names=["label", "message"])
        df["y"] = df["label"].map({"ham": 0, "spam": 1})
        _vec = CountVectorizer()
        X = _vec.fit_transform(df["message"])
        y = df["y"].astype(int)
        _model = MultinomialNB().fit(X, y)
        _nlp_ready = True
        logger.info("NLP model (Naive Bayes) trained on SMSSpamCollection.")
    else:
        logger.warning(f"SMSSpamCollection not found: {sms_path}")
except Exception as e:
    logger.warning(f"Skipped NLP setup (install scikit-learn to enable). Reason: {e}")


class TextIn(BaseModel):
    message: str


@router.post("/predict")
def predict_text(input: TextIn):
    if not _nlp_ready:
        return {
            "ready": False,
            "message": "NLP model not available. Install scikit-learn and place SMSSpamCollection in /data.",
        }
    Xq = _vec.transform([input.message])
    pred = int(_model.predict(Xq)[0])
    verdict = "SPAM" if pred == 1 else "SAFE"
    return {"ready": True, "prediction": pred, "verdict": verdict}
