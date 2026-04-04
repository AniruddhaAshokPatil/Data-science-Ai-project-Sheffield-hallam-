"""I expose the SMS spam prediction route in this file."""

import joblib
from pathlib import Path
from threading import Lock

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from src.api.config import cfg
from src.api.logger import logger
from src.data.preprocess_nlp import load_sms_dataset
from src.train.model_paths import NLP_MODEL, NLP_VECTORIZER

router = APIRouter(prefix="/nlp", tags=["nlp"])

_nlp_lock = Lock()
_nlp_status = {"ready": False, "reason": "NLP model not initialized yet."}
_vec = None
_model = None

URGENCY_TERMS = {"urgent", "suspended", "locked", "immediately", "warning"}
ACTION_TERMS = {"click", "verify", "confirm", "claim", "login"}
IMPERSONATION_TERMS = {"bank", "account", "security", "payment", "wallet"}


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
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.naive_bayes import MultinomialNB

            # I prefer the saved artifacts first because loading them is faster
            # and more stable than retraining on every new API process.
            if NLP_MODEL.exists() and NLP_VECTORIZER.exists():
                _model = joblib.load(NLP_MODEL)
                _vec = joblib.load(NLP_VECTORIZER)
                _nlp_status = {"ready": True, "reason": "ready"}
                logger.info("I loaded the saved NLP model artifacts.")
                return True, "ready"

            sms_path = Path(cfg.sms_corpus)
            if not sms_path.exists():
                _nlp_status = {
                    "ready": False,
                    "reason": f"I could not find the SMS corpus at {sms_path}.",
                }
                return False, _nlp_status["reason"]

            # I use the shared dataset loader here because the raw SMS file can
            # contain wrapped lines and awkward formatting.
            dataframe = load_sms_dataset(sms_path)
            dataframe["message"] = dataframe["message"].fillna("").astype(str)
            dataframe["y"] = dataframe["label"].map({"ham": 0, "spam": 1})
            dataframe = dataframe.dropna(subset=["y"])

            _vec = CountVectorizer()
            features = _vec.fit_transform(dataframe["message"])
            labels = dataframe["y"].astype(int)
            _model = MultinomialNB().fit(features, labels)
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


def _build_prediction_response(message: str):
    # I keep the final prediction formatting in one helper because that makes
    # the route itself shorter and easier to explain.
    transformed_message = _vec.transform([message])
    prediction = int(_model.predict(transformed_message)[0])
    verdict = "SPAM" if prediction == 1 else "SAFE"
    probability_values = _model.predict_proba(transformed_message)[0]
    spam_probability = float(probability_values[1])

    lowered_message = message.lower()
    urgency_hits = [term for term in URGENCY_TERMS if term in lowered_message]
    action_hits = [term for term in ACTION_TERMS if term in lowered_message]
    impersonation_hits = [term for term in IMPERSONATION_TERMS if term in lowered_message]

    detected_intent = "phishing" if prediction == 1 or action_hits or impersonation_hits else "normal"
    explanations = []

    if urgency_hits:
        explanations.append("I found urgency language that tries to pressure the user into acting quickly.")
    if action_hits:
        explanations.append("I found call-to-action wording that pushes the user to click, verify, or confirm something.")
    if impersonation_hits:
        explanations.append("I found account or institution language that can support phishing-style impersonation.")
    if not explanations:
        explanations.append("I did not find strong suspicious language signals in the message.")

    return {
        "ready": True,
        "prediction": prediction,
        "verdict": verdict,
        "spam_probability": spam_probability,
        "detected_intent": detected_intent,
        "signal_breakdown": {
            "urgency_terms": urgency_hits,
            "action_terms": action_hits,
            "impersonation_terms": impersonation_hits,
        },
        "explanations": explanations,
    }


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
    return _build_prediction_response(input.message)
