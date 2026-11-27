"""Broker abstractions for MT5 and Delta. Paper mode always available."""
import pandas as pd
from datetime import datetime
import config
import logging
import requests

logger = logging.getLogger(__name__)

class PaperBroker:
    def __init__(self):
        self.positions = []
        self.balance = 10000.0

    def get_balance(self):
        return self.balance

    def get_positions(self):
        return self.positions

    def place_order(self, symbol, side, qty, sl=None, tp=None, comment=""):
        price = 100.0
        pos = {"ticket": len(self.positions)+1, "symbol": symbol, "side": side, "qty": qty, "entry": price, "sl": sl, "tp": tp, "time": datetime.utcnow().isoformat(), "status": "OPEN"}
        self.positions.append(pos)
        return {"ok": True, "ticket": pos["ticket"], "price": price}

class MT5Broker:
    def __init__(self):
        self.connected = False
        try:
            import MetaTrader5 as mt5
            self.mt5 = mt5
            self.connected = mt5.initialize()
            if self.connected and config.MT5_LOGIN:
                mt5.login(config.MT5_LOGIN, config.MT5_PASSWORD, config.MT5_SERVER)
        except Exception as e:
            logger.warning(f"MT5 not available: {e}")
            self.mt5 = None

    def get_ohlc(self, symbol, timeframe="H1", bars=100):
        if not self.connected:
            return pd.DataFrame()
        tf_map = {"M1": self.mt5.TIMEFRAME_M1, "M5": self.mt5.TIMEFRAME_M5, "H1": self.mt5.TIMEFRAME_H1, "D1": self.mt5.TIMEFRAME_D1}
        rates = self.mt5.copy_rates_from_pos(symbol, tf_map.get(timeframe, self.mt5.TIMEFRAME_H1), 0, bars)
        if rates is None:
            return pd.DataFrame()
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df[["time", "open", "high", "low", "close", "tick_volume"]].rename(columns={"tick_volume": "volume"})

class DeltaBroker:
    def get_ohlc(self, symbol, resolution="1h", limit=100):
        try:
            end = int(datetime.utcnow().timestamp())
            start = end - limit * 3600
            url = "https://api.india.delta.exchange/v2/history/candles"
            r = requests.get(url, params={"symbol": symbol, "resolution": resolution, "start": start, "end": end}, timeout=10)
            data = r.json()
            if not data.get("result"):
                return pd.DataFrame()
            candles = list(reversed(data["result"]))
            df = pd.DataFrame(candles)
            if "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"], unit="s")
            df = df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close"})
            return df[["time", "open", "high", "low", "close"]].tail(limit)
        except Exception as e:
            logger.warning(f"Delta OHLC failed: {e}")
            return pd.DataFrame()
