import pandas as pd
import numpy as np

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

class RSI2Strategy:
    name = "RSI2"
    def signal(self, df):
        if len(df) < 20: return {"action": "HOLD", "confidence": 0}
        df = df.copy()
        df["rsi2"] = rsi(df["close"], 2)
        last = df.iloc[-1]
        if last["rsi2"] < 10:
            return {"action": "BUY", "sl": last["low"]*0.995, "tp": last["close"]*1.01, "confidence": 0.7, "reason": "RSI2"}
        if last["rsi2"] > 90:
            return {"action": "SELL", "sl": last["high"]*1.005, "tp": last["close"]*0.99, "confidence": 0.7, "reason": "RSI2"}
        return {"action": "HOLD", "confidence": 0.3}

class DualThrustStrategy:
    name = "DualThrust"
    def signal(self, df):
        if len(df) < 30: return {"action": "HOLD", "confidence": 0}
        recent = df.iloc[-21:-1]
        rng = max(recent["high"].max() - recent["close"].min(), recent["close"].max() - recent["low"].min())
        upper = df.iloc[-1]["open"] + 0.5 * rng
        lower = df.iloc[-1]["open"] - 0.5 * rng
        price = df.iloc[-1]["close"]
        if price > upper:
            return {"action": "BUY", "sl": lower, "tp": price + (price-lower)*1.5, "confidence": 0.65, "reason": "DualThrust"}
        if price < lower:
            return {"action": "SELL", "sl": upper, "tp": price - (upper-price)*1.5, "confidence": 0.65, "reason": "DualThrust"}
        return {"action": "HOLD", "confidence": 0.4}

STRATEGIES = [RSI2Strategy(), DualThrustStrategy()]

def get_team_signals(df):
    return [{"strategy": s.name, **s.signal(df)} for s in STRATEGIES]

def ensemble_decision(signals, memory=None, asset="BTC"):
    buys = [s for s in signals if s.get("action") == "BUY" and s.get("confidence",0) > 0.5]
    sells = [s for s in signals if s.get("action") == "SELL" and s.get("confidence",0) > 0.5]
    if len(buys) >= 1 and len(buys) > len(sells):
        best = max(buys, key=lambda x: x.get("confidence",0))
        return {"action": "BUY", "sl": best.get("sl"), "tp": best.get("tp"), "votes": len(buys), "reason": "Ensemble"}
    if len(sells) >= 1 and len(sells) > len(buys):
        best = max(sells, key=lambda x: x.get("confidence",0))
        return {"action": "SELL", "sl": best.get("sl"), "tp": best.get("tp"), "votes": len(sells), "reason": "Ensemble"}
    return {"action": "HOLD", "votes": 0, "reason": "No consensus"}
