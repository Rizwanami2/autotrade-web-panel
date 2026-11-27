import asyncio
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket
import uvicorn

BASE_DIR = Path(__file__).parent
TEMPLATES = BASE_DIR / "templates"

def generate_ohlc(symbol="BTCUSD", bars=100):
    base = 96200 if "BTC" in symbol.upper() else 2680
    times = pd.date_range(end=datetime.utcnow(), periods=bars, freq="5min")
    close = base + np.cumsum(np.random.randn(bars) * 25)
    return pd.DataFrame({"time": times, "open": close, "high": close+10, "low": close-10, "close": close})

async def homepage(request):
    html = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)

async def api_chart(request):
    symbol = request.query_params.get("symbol", "BTCUSD")
    df = generate_ohlc(symbol, 100)
    candles = [{"time": int(r["time"].timestamp()), "open": float(r["open"]), "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])} for _, r in df.iterrows()]
    return JSONResponse({"symbol": symbol, "candles": candles, "source": "demo", "broker": "paper"})

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            df = generate_ohlc("BTCUSD", 30)
            await websocket.send_json({"type": "update", "symbol": "BTCUSD", "price": float(df["close"].iloc[-1]), "decision": {"action": "HOLD", "votes": 0, "reason": "Demo"}, "neural": {"buy_votes": 1, "sell_votes": 0, "hold_votes": 1, "avg_confidence": 0.4}})
            await asyncio.sleep(1)
    except Exception:
        pass

app = Starlette(routes=[
    Route("/", homepage),
    Route("/api/chart", api_chart),
    WebSocketRoute("/ws", websocket_endpoint),
])

if __name__ == "__main__":
    print("NEUROTRADE: http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
