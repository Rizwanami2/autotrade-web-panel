# Trading Bot Web Panel

Python FastAPI AutoTrade bot with web panel.

## Features
- Live chart (WebSocket updates every few seconds)
- Multi timeframe switch: 1m, 5m, 15m, 1H, 4H, 1D
- Broker switch: Paper / MT5 / Delta (chart follows)
- Autotrade with Paper / Demo / Live mode switch (Live restricted for safety)
- Strategy team + self-learning memory
- Runs on Windows (start.bat), Termux, Oracle Cloud Free, any Linux

## Run
```bash
pip install -r requirements.txt
python main.py
```
Open http://127.0.0.1:8000 or your server IP:8000

Copy .env.example to .env for credentials.
