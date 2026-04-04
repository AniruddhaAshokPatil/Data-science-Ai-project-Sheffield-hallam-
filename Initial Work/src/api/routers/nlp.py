from pathlib import Path
from threading import Lock

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from src.api.config import cfg
from src.api.logger import logger

router = APIRouter(prefix="/nlp", tags=["nlp"])

_nlp_lock = Lock()
_nlp_status = {"ready": False, "reason": "NLP model not initialized yet."}
_vec = None
_model = None


def _ensure_nlp_model_ready():
    # I lazy-load the NLP model here so API startup stays fast and one missing
    # text dependency does not make the whole backend feel broken.
    global _vec, _model, _nlp_status
    if _nlp_status["ready"]:
        return True, "ready"

    with _nlp_lock:
        if _nlp_status["ready"]:
            return True, "ready"

        try:
            import pandas as pd
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.naive_bayes import MultinomialNB

            sms_path = Path(cfg.sms_corpus)
            if not sms_path.exists():
                _nlp_status = {
                    "ready": False,
                    "reason": f"I could not find the SMS corpus at {sms_path}.",
                }
                return False, _nlp_status["reason"]

            df = pd.read_csv(sms_path, sep="\t", names=["label", "message"])
            df["y"] = df["label"].map({"ham": 0, "spam": 1})
            _vec = CountVectorizer()
            X = _vec.fit_transform(df["message"])
            y = df["y"].astype(int)
            _model = MultinomialNB().fit(X, y)
            _nlp_status = {"ready": True, "reason": "ready"}
            logger.info("I trained the NLP Naive Bayes model from the SMS corpus.")
            return True, "ready"
        except Exception as exc:
            _nlp_status = {
                "ready": False,
                "reason": (
                    "I could not initialize the NLP model. "
                    f"Reason: {exc}"
                ),
            }
            logger.warning(_nlp_status["reason"])
            return False, _nlp_status["reason"]


class TextIn(BaseModel):
    # I keep the input model very small here because the route only needs one
    # thing from the user: the message text to classify.
    model_config = ConfigDict(extra="forbid")
    message: str = Field(..., min_length=1, max_length=5000)


@router.post("/predict")
def predict_text(input: TextIn):
    # I return a friendly fallback response instead of crashing because I want
    # the API to stay usable even when the NLP dependencies or data are missing.
    is_ready, reason = _ensure_nlp_model_ready()
    if not is_ready:
        return {
            "ready": False,
            "message": reason,
        }
    # I transform the incoming text with the same vectorizer used at training
    # time so the model sees the message in the format it expects.
    Xq = _vec.transform([input.message])
    pred = int(_model.predict(Xq)[0])
    verdict = "SPAM" if pred == 1 else "SAFE"
    return {"ready": True, "prediction": pred, "verdict": verdict}
