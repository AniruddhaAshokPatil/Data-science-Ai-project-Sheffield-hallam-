import base64

import pytest
from fastapi.testclient import TestClient

from src.api.auth import hash_password
from src.api.config import settings
from src.api.db import init_database, upsert_user
from src.api.services.insurance_data import load_claim_history
from src.api.main import app


client = TestClient(app)


def login_as(username: str, password: str) -> dict:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture(autouse=True)
def isolate_persistent_test_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_PATH", tmp_path / "shieldwise_runtime.db")
    monkeypatch.setattr(settings, "EVIDENCE_UPLOADS_DIR", tmp_path / "uploads")
    load_claim_history.cache_clear()
    init_database()
    user_salt, user_hash = hash_password("UserPass123!")
    upsert_user(
        username="demo_user",
        full_name="Demo Policyholder",
        role="user",
        password_salt=user_salt,
        password_hash=user_hash,
    )
    investigator_salt, investigator_hash = hash_password("InvestigatorPass123!")
    upsert_user(
        username="investigator_anna",
        full_name="Anna Hughes",
        role="investigator",
        password_salt=investigator_salt,
        password_hash=investigator_hash,
    )
    yield
    load_claim_history.cache_clear()


def test_health_live_endpoint():
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_ready_endpoint():
    response = client.get("/health/ready")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] in {"ok", "degraded"}
    assert "database_ready" in payload["checks"]


def test_login_returns_role_aware_token():
    payload = login_as("demo_user", "UserPass123!")

    assert payload["token_type"] == "bearer"
    assert payload["role"] == "user"


def test_company_dashboard_requires_investigator_role():
    user_login = login_as("demo_user", "UserPass123!")

    response = client.get(
        "/api/insurance/company-dashboard",
        headers={"Authorization": f"Bearer {user_login['access_token']}"},
    )

    assert response.status_code == 403


def test_customer_dashboard_accepts_user_role():
    user_login = login_as("demo_user", "UserPass123!")

    response = client.get(
        "/api/insurance/customer-dashboard",
        headers={"Authorization": f"Bearer {user_login['access_token']}"},
    )

    assert response.status_code == 200
    assert "claims" in response.json()


def test_insurance_home_endpoint_returns_core_sections():
    response = client.get("/api/insurance/home")

    assert response.status_code == 200
    payload = response.json()

    assert "metrics" in payload
    assert "behavioural_fields" in payload
    assert "claim_email_samples" in payload
    assert len(payload["live_alerts"]) >= 1


def test_company_dashboard_endpoint_returns_queue():
    investigator_login = login_as("investigator_anna", "InvestigatorPass123!")
    response = client.get(
        "/api/insurance/company-dashboard",
        headers={"Authorization": f"Bearer {investigator_login['access_token']}"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert "queue" in payload
    assert len(payload["queue"]) >= 1
    assert payload["queue"][0]["claim_id"].startswith("CLM-")


def test_alerts_websocket_stream_returns_events():
    investigator_login = login_as("investigator_anna", "InvestigatorPass123!")
    with client.websocket_connect(f"/ws/alerts?token={investigator_login['access_token']}") as websocket:
        message = websocket.receive_json()

    assert message["id"].startswith("ALT-")
    assert message["severity"] in {"High", "Review", "Low"}


def test_claim_submission_persists_and_returns_dashboard_items():
    user_login = login_as("demo_user", "UserPass123!")
    response = client.post(
        "/api/insurance/claims",
        headers={"Authorization": f"Bearer {user_login['access_token']}"},
        json={
            "claimant_name": "Rita Lawson",
            "claimant_email": "rita@example.com",
            "policy_type": "gadget",
            "coverage_tier": "premium",
            "item_category": "laptop",
            "incident_type": "theft",
            "claim_amount_gbp": 1999,
            "estimated_item_value_gbp": 1499,
            "prior_claims_count": 2,
            "claims_last_12_months": 1,
            "days_since_policy_start": 14,
            "recent_high_value_purchase_flag": True,
            "unusual_spend_spike_flag": True,
            "account_login_location_change_flag": True,
            "multiple_devices_last_7_days_flag": True,
            "address_change_last_30_days_flag": False,
            "phone_change_last_30_days_flag": False,
            "bank_detail_change_last_30_days_flag": True,
            "late_night_submission_flag": True,
            "weekend_submission_flag": False,
            "receipt_present_flag": True,
            "receipt_mismatch_flag": True,
            "duplicate_receipt_flag": False,
            "image_tamper_flag": False,
            "claim_story": "I need an urgent full payout because my laptop was stolen and I do not remember the exact location. I also changed my bank account recently.",
        },
    )

    assert response.status_code == 201
    payload = response.json()

    assert payload["claim_id"].startswith("CLM-")
    assert payload["customer_claim"]["claim_id"] == payload["claim_id"]
    assert payload["queue_item"]["claim_id"] == payload["claim_id"]
    assert payload["alert"]["severity"] in {"High", "Review", "Low"}


def test_claim_submission_with_evidence_uploads_file_and_scores_document_risk():
    user_login = login_as("demo_user", "UserPass123!")
    sample_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn7h0wAAAAASUVORK5CYII="
    )

    response = client.post(
        "/api/insurance/claims/with-evidence",
        headers={"Authorization": f"Bearer {user_login['access_token']}"},
        data={
            "claimant_name": "Naomi Reed",
            "claimant_email": "naomi@example.com",
            "policy_type": "gadget",
            "coverage_tier": "standard",
            "item_category": "tablet",
            "incident_type": "accidental_damage",
            "claim_amount_gbp": "620",
            "estimated_item_value_gbp": "599",
            "prior_claims_count": "0",
            "claims_last_12_months": "0",
            "days_since_policy_start": "120",
            "recent_high_value_purchase_flag": "false",
            "unusual_spend_spike_flag": "false",
            "account_login_location_change_flag": "false",
            "multiple_devices_last_7_days_flag": "false",
            "address_change_last_30_days_flag": "false",
            "phone_change_last_30_days_flag": "false",
            "bank_detail_change_last_30_days_flag": "false",
            "late_night_submission_flag": "false",
            "weekend_submission_flag": "false",
            "receipt_present_flag": "true",
            "receipt_mismatch_flag": "false",
            "duplicate_receipt_flag": "false",
            "image_tamper_flag": "false",
            "claim_story": "I am submitting a tablet damage claim with the supporting receipt image attached for review.",
        },
        files={"evidence_file": ("receipt.png", sample_png, "image/png")},
    )

    assert response.status_code == 201
    payload = response.json()

    assert payload["evidence_summary"]["evidence_name"] == "receipt.png"
    assert payload["evidence_summary"]["evidence_storage_path"]
    assert payload["evidence_summary"]["document_risk_score"] > 0
