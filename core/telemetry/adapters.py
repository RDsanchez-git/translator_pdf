from typing import Dict, Any
from core.telemetry.ports import TelemetryPort

class NullTelemetryAdapter(TelemetryPort):
    """Adaptador de contingencia para desarrollo y tests. Evita acoplamiento prematuro con SQLite."""
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str]) -> None:
        pass

    def record_event(self, name: str, payload: Dict[str, Any]) -> None:
        pass