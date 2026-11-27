import asyncio
import json
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import logging
import numpy as np

import config
from memory import Memory
from strategies import get_team_signals, ensemble_decision, STRATEGIES
from brokers import PaperBroker, MT5Broker, DeltaBroker
import risk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NEUROTRADE Web Panel")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

memory = Memory()
paper_broker = PaperBroker()
mt5_broker = None
delta_broker = None
current_broker_name = "paper"
current_symbol = config.BTC_SYMBOL
current_timeframe = "1h"
autotrade_enabled = False
autotrade_mode = "paper"
last_auto_action = None

def get_active_broker():
    global mt5_broker, delta_broker
    if current_broker_name == "mt5":
        if mt5_broker is None:
            mt5_broker = MT5Broker()
        return mt5_broker
    if current_broker_name == "delta":
        if delta_broker is None:
            delta_broker = DeltaBroker()
        return delta_broker
    return paper_broker

def get_ohlc(symbol, bars=None, timeframe=None):
    bars = bars or getattr(config, "CHART_BARS", 100)
    tf = timeframe or current_timeframe
    # Demo data fallback
    base = 95000 if "BTC" in symbol.upper() else 2650
    times = pd.date_range(end=datetime.utcnow(), periods=bars, freq="1h")
    close = base + np.cumsum(np.random.randn(bars) * 50)
    df = pd.DataFrame({
        "time": times,
        "open": close + np.random.randn(bars)*10,
        "high": close + np.abs(np.random.randn(bars)*20),
        "low": close - np.abs(np.random.randn(bars)*20),
        "close": close
    })
    df.attrs["source"] = "demo"
    return df

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def status():
    return {"broker": current_broker_name, "symbol": current_symbol, "autotrade": autotrade_enabled}

@app.get("/api/chart")
async def chart_data(symbol: str = Query(None), broker: str = Query(None), tf: str = Query(None)):
    global current_symbol, current_broker_name, current_timeframe
    if symbol: current_symbol = symbol
    if broker: current_broker_name = broker
    if tf: current_timeframe = tf
    df = get_ohlc(current_symbol)
    candles = [{"time": int(row["time"].timestamp()), "open": float(row["open"]), "high": float(row["high"]), "low": float(row["low"]), "close": float(row["close"])} for _, row in df.iterrows()]
    return {"symbol": current_symbol, "broker": current_broker_name, "timeframe": current_timeframe, "candles": candles}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            df = get_ohlc(current_symbol, 50)
            if not df.empty:
                signals = get_team_signals(df)
                decision = ensemble_decision(signals, memory, current_symbol)
                await websocket.send_json({
                    "type": "update",
                    "symbol": current_symbol,
                    "price": float(df["close"].iloc[-1]),
                    "decision": decision,
                    "time": datetime.utcnow().isoformat()
                })
            await asyncio.sleep(getattr(config, "WS_INTERVAL", 1))
    except WebSocketDisconnect:
        pass

@app.post("/api/trade")
async def manual_trade(data: dict):
    return {"ok": True, "message": "Paper trade simulated"}

if __name__ == "__main__":
    import uvicorn
    print("Starting NEUROTRADE at http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
