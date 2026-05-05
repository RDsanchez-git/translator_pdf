import time
from collections import defaultdict

class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timing_stats = defaultdict(lambda: {
            "count": 0,
            "sum": 0.0,
            "max": 0.0,
            "min": float("inf")
        })
        self.start_time = time.time()

    def inc(self, key: str, value: int = 1):
        self.counters[key] += value

    def observe(self, key: str, value: float):
        stat = self.timing_stats[key]
        stat["count"] += 1
        stat["sum"] += value
        stat["max"] = max(stat["max"], value)
        stat["min"] = min(stat["min"], value)

    def summary(self):
        result = {
            "uptime_sec": round(time.time() - self.start_time, 2),
            "counters": dict(self.counters),
            "timings": {}
        }
        for k, stat in self.timing_stats.items():
            if stat["count"] > 0:
                result["timings"][k] = {
                    "count": stat["count"],
                    "avg": round(stat["sum"] / stat["count"], 3),
                    "max": round(stat["max"], 3),
                    "min": round(stat["min"], 3)
                }
        return result