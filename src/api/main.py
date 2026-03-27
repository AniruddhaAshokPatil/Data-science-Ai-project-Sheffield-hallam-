import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.api.routers.analytics import router as analytics_router
from src.api.routers.cv import router as cv_router
from src.api.routers.nlp import router as nlp_router
from src.api.routers.transactions import score_transaction_features
from src.api.routers.transactions import router as transactions_router
from src.api.websocket_manager import WebSocketManager


app = FastAPI(
    title="Fraud Detection API",
    version="1.0.0",
    description="Unified API for transaction, NLP, analytics, and CV fraud scoring.",
)

ws_manager = WebSocketManager()


@app.get("/")
def root():
    return {
        "message": "Fraud Detection API is running.",
        "routes": [
            "/transaction/predict",
            "/nlp/predict",
            "/analytics/visualize",
            "/analytics/outliers",
            "/cv/predict",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(transactions_router)
app.include_router(nlp_router)
app.include_router(analytics_router)
app.include_router(cv_router)


@app.websocket("/ws/transactions")
async def transactions_websocket(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            raw_message = await websocket.receive_text()
            if raw_message.strip().lower() == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            payload = json.loads(raw_message)
            features = payload.get("features")
            if not isinstance(features, dict):
                await websocket.send_json({"error": "Payload must include a features object."})
                continue

            result = score_transaction_features(features).model_dump()
            await ws_manager.broadcast(result)
    except (WebSocketDisconnect, json.JSONDecodeError):
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
        raise
