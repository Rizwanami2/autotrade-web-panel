import json
from datetime import datetime
import config

class Memory:
    def __init__(self):
        self.file = config.MEMORY_FILE
        self.data = self._load()

    def _load(self):
        if self.file.exists():
            try:
                return json.loads(self.file.read_text())
            except:
                return {"strategies": {}, "lessons": []}
        return {"strategies": {}, "lessons": []}

    def save(self):
        self.data["last_update"] = datetime.utcnow().isoformat()
        self.file.write_text(json.dumps(self.data, indent=2))

    def record_trade(self, strategy, asset, result_r, fees_r=0.0, regime="UNKNOWN"):
        key = f"{strategy}_{asset}"
        if key not in self.data["strategies"]:
            self.data["strategies"][key] = {"trades": 0, "wins": 0, "total_r": 0.0, "recent": []}
        s = self.data["strategies"][key]
        s["trades"] += 1
        if result_r > 0:
            s["wins"] += 1
        s["total_r"] += result_r
        self.save()

    def get_win_rate(self, strategy, asset):
        key = f"{strategy}_{asset}"
        s = self.data["strategies"].get(key, {})
        return s.get("wins", 0) / s.get("trades", 1) if s.get("trades") else 0.5

    def should_trade(self, strategy, asset, min_trades=5, min_wr=0.4):
        key = f"{strategy}_{asset}"
        s = self.data["strategies"].get(key, {})
        if s.get("trades", 0) < min_trades:
            return True
        return self.get_win_rate(strategy, asset) >= min_wr

    def summary(self):
        return {"strategies": self.data["strategies"], "last_update": self.data.get("last_update")}
