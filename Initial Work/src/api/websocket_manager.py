from typing import List
from fastapi import WebSocket

from src.api.logger import logger


class WebSocketManager:
    def __init__(self):
        # I keep a list of active connections so I can broadcast one scored
        # transaction result to every dashboard client connected right now.
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # I accept the connection before storing it because FastAPI needs the
        # WebSocket handshake to complete before I can use the connection.
        await websocket.accept()
        self.connections.append(websocket)
        logger.info("WebSocket client connected. Active clients: %s", len(self.connections))

    def disconnect(self, websocket: WebSocket):
        # I remove disconnected clients so I do not keep trying to send data
        # to connections that are no longer alive.
        if websocket in self.connections:
            self.connections.remove(websocket)
            logger.info(
                "WebSocket client disconnected. Active clients: %s",
                len(self.connections),
            )

    async def broadcast(self, message: dict):
        # I loop over a copy of the connection list because a failed client may
        # be removed while I am still broadcasting to the others.
        active_connections = list(self.connections)
        for ws in active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                # I drop failed connections here so one broken client does not
                # keep interrupting live updates for the rest.
                logger.warning("I dropped a failed WebSocket client during broadcast.")
                self.disconnect(ws)
