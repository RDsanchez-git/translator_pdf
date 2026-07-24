from typing import Protocol, Sequence, runtime_checkable

from core.ast.models import ASTNode
from tools.evaluation.topology.models import (
    BenchmarkSummaryReport,
    DocumentEvaluationResult,
    MetricName,
    MetricResult,
)


@runtime_checkable
class TopologyMetric(Protocol):
    """Protocolo puro para métricas topológicas atomizadas sobre un documento completo."""

    @property
    def name(self) -> MetricName:
        ...

    def evaluate(
        self,
        candidate: Sequence[ASTNode],
        ground_truth: Sequence[ASTNode]
    ) -> MetricResult:
        ...


@runtime_checkable
class BenchmarkAggregationStrategy(Protocol):
    """Protocolo de agregación para colapsar resultados en un reporte global."""

    def aggregate(
        self,
        provider_name: str,
        results: Sequence[DocumentEvaluationResult]
    ) -> BenchmarkSummaryReport:
        ...