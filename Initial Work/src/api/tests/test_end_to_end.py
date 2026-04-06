import os
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from fastapi import FastAPI

from src.api.main import create_app
from src.api.routers.transactions import router as transactions_router

TIMEOUT_THRESHOLD = 0.5
CV_SAMPLE_IMAGE = "data/processed/cv/test/original/img_00185_orig.jpg"

NORMAL_TRANSACTION = {
    "features": {
        "amount": 50,
        "spending_deviation_score": 0.2,
        "velocity_score": 1,
        "geo_anomaly_score": 0.05,
    },
    "text": "payment for groceries",
}

FRAUD_TRANSACTION = {
    "features": {
        "amount": 5000,
        "spending_deviation_score": 3.8,
        "velocity_score": 18,
        "geo_anomaly_score": 0.95,
    },
    "text": "urgent verify your account now",
}

def _build_test_client() -> TestClient:
    # I create the test app in one place so each test exercises the same API
    # wiring while staying isolated from heavier startup modules.
    os.makedirs("/tmp/matplotlib", exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
    app = FastAPI()
    app.include_router(transactions_router)
    return TestClient(app)


def _exercise_transaction(payload, label):
    """
    I exercise the live transaction route here because this test should prove
    the API shape your frontend and demo flow rely on.
    """
    client = _build_test_client()
    start_time = time.time()
    response = client.post("/transaction/predict", json=payload)
    latency = time.time() - start_time

    assert response.status_code == 200, "API failed"

    data = response.json()
    assert "risk" in data, "Missing risk"
    assert "details" in data, "Missing details"
    assert "timestamp" in data, "Missing timestamp"
    assert "profile" in data, "Missing profile"
    assert 0 <= data["risk"] <= 1, "Risk out of range"
    assert "tabular_prob" in data["details"], "Missing tabular score details"
    assert latency < TIMEOUT_THRESHOLD, "Latency too high"
    return data

def test_end_to_end_transaction_scoring():
    """
    I compare a low-risk and a higher-risk payload because that is the clearest
    project-level proof that the scoring endpoint is behaving sensibly.
    """
    normal = _exercise_transaction(NORMAL_TRANSACTION, "NORMAL")
    fraud = _exercise_transaction(FRAUD_TRANSACTION, "FRAUD")
    assert fraud["risk"] > normal["risk"], "Fraud risk should be higher than normal"


def test_transaction_route_rejects_unknown_feature_profile():
    """
    I expect unsupported payload shapes to fail clearly because production APIs
    should guide clients toward valid contracts instead of scoring junk data.
    """
    client = _build_test_client()
    response = client.post(
        "/transaction/predict",
        json={"features": {"mystery_signal": 42.0}},
    )

    assert response.status_code == 422
    assert "supported transaction feature profile" in response.json()["detail"]


class EndToEndTransactionTests(unittest.TestCase):
    def test_end_to_end_transaction_scoring(self):
        try:
            test_end_to_end_transaction_scoring()
        except (ModuleNotFoundError, RuntimeError) as exc:
            if "httpx" in str(exc):
                self.skipTest(
                    "I need the optional httpx dependency installed before I can run FastAPI integration tests."
                )
            raise


def test_websocket_scores_and_broadcasts_transaction_payload():
    """
    I send a live transaction over WebSocket here because this is the closest
    automated proof of the dashboard event flow the project currently has.
    """
    os.makedirs("/tmp/matplotlib", exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
    client = TestClient(create_app())

    start_time = time.time()
    with client.websocket_connect("/ws/transactions") as websocket:
        websocket.send_json(FRAUD_TRANSACTION)
        payload = websocket.receive_json()
    latency = time.time() - start_time

    assert payload["profile"] == "financial"
    assert "risk" in payload
    assert "details" in payload
    assert payload["details"]["tabular_prob"] >= 0
    assert latency < TIMEOUT_THRESHOLD


def test_nlp_route_predicts_spam_or_safe():
    """
    I call the NLP route directly here because I want automated proof that the
    text-scoring endpoint returns a usable prediction payload.
    """
    client = TestClient(create_app())
    response = client.post(
        "/nlp/predict",
        json={"message": "URGENT: your bank account is locked, click now"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ready"] is True
    assert payload["prediction"] in {0, 1}
    assert payload["verdict"] in {"SPAM", "SAFE"}


def test_cv_route_scores_real_image_and_reports_mode():
    """
    I call the CV route with a real project image because I want to prove the
    endpoint works in either deep-learning or fallback mode.
    """
    if not Path(CV_SAMPLE_IMAGE).exists():
        raise FileNotFoundError(f"I expected a CV sample image at {CV_SAMPLE_IMAGE}.")

    client = TestClient(create_app())
    response = client.post(
        "/cv/predict",
        json={"image_path": CV_SAMPLE_IMAGE},
    )

    assert response.status_code == 200
    payload = response.json()
    assert 0.0 <= payload["fraud_score"] <= 1.0
    assert payload["verdict"] in {"fraud_suspected", "likely_genuine"}
    assert payload["details"]["cv_mode"] in {"deep_learning", "heuristic_fallback"}
