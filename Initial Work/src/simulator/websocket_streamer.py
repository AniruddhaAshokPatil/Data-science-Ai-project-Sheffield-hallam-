import asyncio
import json

import pandas as pd
import websockets

from src.simulator.simulator_config import cfg


async def stream_over_websocket(df: pd.DataFrame):
    # I use a separate async function here because WebSocket sending works naturally with asyncio.
    print("Connecting to WebSocket:", cfg.backend_ws)

    async with websockets.connect(cfg.backend_ws) as ws:
        for _, row in df.iterrows():
            features = row.to_dict()
            payload = {"features": features}
            message = json.dumps(payload)

            await ws.send(message)
            print("Sent:", payload)
            await asyncio.sleep(cfg.delay_seconds)

    print("WebSocket streaming complete!")
    
