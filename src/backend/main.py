from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import transactions, analytics, nlp
from backend.websocket_manager import WebSocketManager
from backend.logger import logger

app = FastAPI(
    title="Fraud Detection Backend (MVP)",
    version="0.1.0",
)

# Allow frontends/tools to call the API easily during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(nlp.router)

# Shared WS manager
ws_manager = WebSocketManager()

from backend.websocket_manager import WebSocketManager
ws_manager = WebSocketManager()

@app.websocket("/ws/transactions")
async def ws_transactions(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()

            # NEW: broadcast the message to all connected browsers
            await ws_manager.broadcast({"raw": msg})

    except Exception:
        ws_manager.disconnect(websocket)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.websocket("/ws/transactions")
async def ws_transactions(websocket: WebSocket):
    await ws_manager.connect(websocket)
    logger.info("WebSocket client connected")
    try:
        while True:
            # We don't expect messages from client in MVP; keep the socket open
            await websocket.receive_text()
    except Exception:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")