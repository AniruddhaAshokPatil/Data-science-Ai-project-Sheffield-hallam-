from __future__ import annotations

import asyncio
from contextlib import suppress

from fastapi import WebSocket

from src.api.schemas import AlertItem
from src.api.services.insurance_dashboard import build_live_alert_event


class AlertStreamManager:
    def __init__(self) -> None:
        # I keep a simple counter so every live alert sent over the socket gets a new event id.
        self._event_index = 0
        self._connections: set[WebSocket] = set()

    async def stream_claim_alerts(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

        try:
            # I send one immediate event so the dashboard has a live message as soon as it connects.
            event = build_live_alert_event(self._event_index)
            self._event_index += 1
            await websocket.send_json(event.model_dump())

            while True:
                await websocket.receive_text()
        except Exception:
            pass
        finally:
            self._connections.discard(websocket)
            with suppress(Exception):
                await websocket.close()

    async def broadcast_alert(self, alert: AlertItem) -> None:
        stale_connections = set()
        for connection in self._connections:
            try:
                await connection.send_json(alert.model_dump())
            except Exception:
                stale_connections.add(connection)

        for connection in stale_connections:
            self._connections.discard(connection)

    async def emit_generated_alert(self) -> AlertItem:
        event = build_live_alert_event(self._event_index)
        self._event_index += 1
        await self.broadcast_alert(event)
        return event


alert_stream_manager = AlertStreamManager()
