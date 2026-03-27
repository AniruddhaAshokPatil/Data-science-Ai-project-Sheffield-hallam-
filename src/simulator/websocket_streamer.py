import asyncio
import json

import pandas as pd
import websockets

from src.simulator.simulator_config import cfg


async def stream_over_websocket(df: pd.DataFrame):
    print("🔌 Connecting to WebSocket:", cfg.backend_ws)

    async with websockets.connect(cfg.backend_ws) as ws:
        for _, row in df.iterrows():
            payload = {"features": row.to_dict()}
            await ws.send(json.dumps(payload))
            print("📤 Sent:", payload)
            await asyncio.sleep(cfg.delay_seconds)

    print("✅ WebSocket streaming complete!")
    
