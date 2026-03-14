"""
MAIN BACKEND FILE (Beginner Friendly)

In this file, I set up my FastAPI server for my fraud detection project.

What I do here:
1) I create a FastAPI app (this is my backend server).
2) I allow the browser (frontend) to call my API during development (CORS).
3) I plug in my routers (small files that handle different parts: transactions, analytics, nlp).
4) I create ONE WebSocket route so my frontend can receive live messages.
5) I add a simple /health endpoint so I can check if my server is alive.

I write comments in "I" form so it feels like I'm guiding myself.
"""

# 1) I import FastAPI and WebSocket tools
from fastapi import FastAPI, WebSocket

# 2) I import CORS middleware so my browser app (React) can talk to this server
from fastapi.middleware.cors import CORSMiddleware

# 3) I import my own routers (these are other Python files in my backend package)
#    - transactions: handles /transaction/predict requests
#    - analytics:    runs my visualization and outlier helpers
#    - nlp:          simple text spam/phishing prediction
from backend.routers import transactions, analytics, nlp

# 4) I import my WebSocket manager (it stores a list of connected clients)
from backend.websocket_manager import WebSocketManager

# 5) I import a tiny logger (so I can print nice messages)
from backend.logger import logger


# ------------------------------------------------------
# I CREATE MY FASTAPI APP (this is my main server object)
# ------------------------------------------------------
app = FastAPI(
    title="Fraud Detection Backend (MVP)",
    version="0.1.0",
)

# -------------------------------------------------------------------
# I ENABLE CORS (Cross-Origin Resource Sharing) for local development
# This lets my React frontend (http://127.0.0.1:5173 by default) call
# this API without being blocked by the browser.
# In production, I should restrict allow_origins to my real domain.
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # I keep it open during development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------
# I ATTACH MY ROUTERS (they add their routes)
# -------------------------------------------
# After I do this, the app now understands:
#   /transaction/predict
#   /analytics/visualize
#   /analytics/outliers
#   /nlp/predict
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(nlp.router)

# ------------------------------------------------------------
# I CREATE ONE SHARED WEBSOCKET MANAGER
# This object remembers who is connected via WebSocket so I can
# broadcast messages to all connected clients (my dashboard).
# ------------------------------------------------------------
ws_manager = WebSocketManager()


# ------------------------------------------------------------
# I DEFINE ONE (and only one) WEBSOCKET ENDPOINT
# Path: /ws/transactions
#
# What happens here:
# - When a browser connects, I accept the connection and store it.
# - I wait for messages (for example, from my simulator).
# - Every time I receive a message, I forward (broadcast) it to
#   ALL connected browsers so the live table updates instantly.
# - If something goes wrong, I remove that connection.
# ------------------------------------------------------------
@app.websocket("/ws/transactions")
async def ws_transactions(websocket: WebSocket):
    # I accept the connection and remember it
    await ws_manager.connect(websocket)
    logger.info("WebSocket client connected")

    try:
        while True:
            # I wait for a text message from this client (e.g., simulator sends JSON)
            msg = await websocket.receive_text()

            # I forward the message to everyone (including other tabs)
            # Here I wrap it in a simple dict with key "raw" to keep it obvious.
            await ws_manager.broadcast({"raw": msg})

    except Exception:
        # If the connection breaks or the client closes the tab, I remove it.
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


# --------------------------------------------
# I ADD A SIMPLE HEALTH CHECK (GET /health)
# This lets me quickly see if my server is alive.
# --------------------------------------------
@app.get("/health")
def health():
    # I return a tiny JSON object
    return {"status": "ok"}
