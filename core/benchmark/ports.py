"""
core/benchmark/ports.py

Puertos y contratos abstractos para la infraestructura de benchmarking.
Garantiza el Principio de Inversión de Dependencias (DIP) e inyecta
interfaces abstractas puras para Candidate Providers y Evaluators.
"""

from typing import Any, Protocol, runtime_checkable

from core.benchmark.models import (
    MetricResult,
    PreparedBenchmarkDataset,
    RunnerExecutionResult,
)
from core.benchmark.types import BenchmarkArtifact


class BenchmarkRunnerProtocol(Protocol):
    """SOTA: Puerto abstracto para aislamiento de los entornos de ejecución (Runners)."""

    async def warmup(self) -> None:
        ...

    async def teardown(self) -> None:
        ...

    async def execute_dataset(
        self, dataset: PreparedBenchmarkDataset, force_cache_bypass: bool = True
    ) -> RunnerExecutionResult:
        ...


@runtime_checkable
class BenchmarkCandidateProvider(Protocol):
    """SOTA: Contrato abstracto para proveedores de candidatos a evaluar."""

    @property
    def provider_name(self) -> str:
        ...

    def provide(self, document_id: str) -> BenchmarkArtifact:
        ...


@runtime_checkable
class BenchmarkEvaluatorProtocol(Protocol):
    """SOTA: Contrato abstracto para métricas y evaluadores de benchmark."""

    @property
    def metric_name(self) -> str:
        ...

    def evaluate(self, candidate: Any, ground_truth: Any) -> MetricResult:
        ...

@runtime_checkable
class GroundTruthProviderProtocol(Protocol):
    """SOTA: Contrato abstracto para la provisión del Ground Truth (Golden AST o Referencia)."""

    def get_ground_truth(self, document_id: str) -> Any:
        ...
    