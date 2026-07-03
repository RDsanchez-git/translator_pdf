from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class StageExecutionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    execution_id: str
    stage_name: str
    stage_index: int
    latency_sec: float
    input_type: str
    output_type: str
    status: str  # SUCCESS | FAILED
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TelemetryPort(ABC):
    @abstractmethod
    def record_execution(self, record: StageExecutionRecord) -> None:
        """Emite el registro de ejecución de forma atómica hacia la infraestructura."""
        pass

class NullTelemetryAdapter(TelemetryPort):
    def record_execution(self, record: StageExecutionRecord) -> None:
        pass