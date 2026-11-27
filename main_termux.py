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
current_symbol = "BTCUSD"

def generate_ohlc(symbol="BTCUSD", bars=80):
    base = 95000 if "BTC" in symbol.upper() else 2650
    times = pd.date_range(end=datetime.utcnow(), periods=bars, freq="1h")
    close = base + np.cumsum(np.random.randn(bars) * 40)
    return pd.DataFrame({"time": times, "open": close, "high": close+10, "low": close-10, "close": close})

async def homepage(request):
    html = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)

async def api_chart(request):
    symbol = request.query_params.get("symbol", current_symbol)
    df = generate_ohlc(symbol)
    candles = [{"time": int(r["time"].timestamp()), "open": float(r["open"]), "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])} for _, r in df.iterrows()]
    return JSONResponse({"symbol": symbol, "candles": candles, "source": "demo"})

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            df = generate_ohlc(current_symbol, 40)
            await websocket.send_json({"type": "update", "symbol": current_symbol, "price": float(df["close"].iloc[-1]), "decision": {"action": "HOLD", "votes": 0}})
            await asyncio.sleep(1)
    except Exception:
        pass

app = Starlette(routes=[
    Route("/", homepage),
    Route("/api/chart", api_chart),
    WebSocketRoute("/ws", websocket_endpoint),
])

if __name__ == "__main__":
    print("NEUROTRADE Termux mode: http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
