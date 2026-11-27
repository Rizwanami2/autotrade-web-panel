from datetime import datetime
import config

def in_session(asset, now=None):
    now = now or datetime.utcnow()
    time_str = now.strftime("%H:%M")
    sessions = config.GOLD_SESSIONS if "XAU" in asset.upper() or "GOLD" in asset.upper() else config.BTC_SESSIONS
    for start, end in sessions:
        if start <= time_str <= end:
            return True
    return False
