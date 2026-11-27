import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

LOW_RESOURCE = os.getenv("LOW_RESOURCE", "true").lower() == "true"
CHART_BARS = 60 if LOW_RESOURCE else 150
WS_INTERVAL = 8 if LOW_RESOURCE else 4
AUTOTRADE_INTERVAL = 15 if LOW_RESOURCE else 8

TRADING_MODE = os.getenv("TRADING_MODE", "paper")
# ... rest of config remains
