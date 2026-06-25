from dataclasses import dataclass
from typing import Protocol, List
from core.benchmark.models import PreparedBenchmarkDataset, ChunkBenchmarkRecord, HardwareTelemetry

@dataclass(frozen=True, slots=True)
class RunnerExecutionResult:
    """SOTA: Retorno crudo de infraestructura antes del colapso estadístico."""
    provider_id: str
    raw_records: List[ChunkBenchmarkRecord]
    document_completion_seconds: float
    hardware_telemetry: HardwareTelemetry

class BenchmarkRunnerProtocol(Protocol):
    """SOTA: Puerto abstracto para aislamiento de los entornos de ejecución (Runners)."""
    async def warmup(self) -> None: ...
    async def teardown(self) -> None: ...
    
    async def execute_dataset(
        self, 
        dataset: PreparedBenchmarkDataset,
        force_cache_bypass: bool = True
    ) -> RunnerExecutionResult: ...

