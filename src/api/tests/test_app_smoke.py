from fastapi.testclient import TestClient

from src.api.main import create_app


def test_root_exposes_environment_and_version():
    # I check the root route here because it is often the first endpoint I use
    # to confirm that a deployed API is alive and correctly configured.
    client = TestClient(create_app())
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Fraud Detection API is running."
    assert "environment" in payload
    assert "version" in payload
    assert "/transaction/predict" in payload["routes"]


def test_health_route_returns_operational_metadata():
    # I verify the health payload because production checks usually need more
    # than a bare 200 when I wire the service into monitoring.
    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "environment" in payload
    assert "version" in payload
    assert "X-Process-Time" in response.headers


def test_readiness_route_returns_structured_component_statuses():
    # I check readiness here because deployment tooling needs a detailed view
    # of which models and supporting assets are actually available.
    client = TestClient(create_app())
    response = client.get("/health/ready")

    assert response.status_code in {200, 503}
    payload = response.json()
    assert "status" in payload
    assert "ready" in payload
    assert "components" in payload
    assert "transaction_api" in payload["components"]
    assert "outputs_directory" in payload["components"]


def test_websocket_ping_returns_pong():
    # I use a ping test here because live dashboards depend on the WebSocket
    # staying responsive even before any real fraud events are flowing in.
    client = TestClient(create_app())
    with client.websocket_connect("/ws/transactions") as websocket:
        websocket.send_text("ping")
        payload = websocket.receive_json()

    assert payload == {"type": "pong"}
