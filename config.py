import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
MEMORY_FILE = DATA_DIR / "memory.json"
TRADES_FILE = DATA_DIR / "trades.csv"

TRADING_MODE = os.getenv("TRADING_MODE", "paper")
MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")
DELTA_API_KEY = os.getenv("DELTA_API_KEY", "")
DELTA_API_SECRET = os.getenv("DELTA_API_SECRET", "")
DELTA_TESTNET = os.getenv("DELTA_TESTNET", "true").lower() == "true"
DELTA_BASE_URL = os.getenv("DELTA_BASE_URL", "https://api.delta.exchange")
MAX_RISK_PCT = float(os.getenv("MAX_RISK_PCT", "1.0"))
GOLD_SYMBOL = os.getenv("GOLD_SYMBOL", "XAUUSD")
BTC_SYMBOL = os.getenv("BTC_SYMBOL", "BTCUSD")
GOLD_DELTA = os.getenv("GOLD_DELTA_SYMBOL", "XAUTUSD")
BTC_DELTA = os.getenv("BTC_DELTA_SYMBOL", "BTCUSD")
GOLD_SESSIONS = [("07:00", "10:00"), ("12:30", "15:30")]
BTC_SESSIONS = [("06:00", "21:00")]
