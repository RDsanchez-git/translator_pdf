from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping, Tuple, TypeAlias

from core.ast.models import ASTNode

PrimitiveAttribute: TypeAlias = str | int | float | bool | None


class MetricName(StrEnum):
    """Vocabulario cerrado de métricas topológicas registradas en la plataforma."""
    NODE_COUNT = "node_count"
    RECALL = "recall"
    SEQUENCE = "sequence"
    STRUCTURAL = "structural"


@dataclass(frozen=True)
class BenchmarkDocument:
    """Par inmutable de secuencia de candidatos y Ground Truth para un documento."""
    doc_id: str
    candidate: Tuple[ASTNode, ...]
    ground_truth: Tuple[ASTNode, ...]


@dataclass(frozen=True)
class ConfusionMatrix:
    """Value Object inmutable para métricas de clasificación/recuperación semántica."""
    tp: int
    fp: int
    fn: int

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom > 0 else 0.0

    @property
    def f1_score(self) -> float:
        p, r = self.precision, self.recall
        return (2 * p * r) / (p + r) if (p + r) > 0 else 0.0


@dataclass(frozen=True)
class MetricResult:
    """Resultado inmutable de la evaluación de una dimensión topológica individual."""
    metric_name: MetricName
    value: float
    details: Mapping[str, PrimitiveAttribute] = field(
        default_factory=lambda: MappingProxyType({})
    )


@dataclass(frozen=True)
class DocumentEvaluationResult:
    """Resultado observacional del benchmark sobre un documento individual."""
    doc_id: str
    metrics: Tuple[MetricResult, ...]


@dataclass(frozen=True)
class BenchmarkSummaryReport:
    """Reporte consolidado global del benchmark sobre un corpus."""
    provider_name: str
    total_documents: int
    document_results: Tuple[DocumentEvaluationResult, ...]
    summary_metrics: Mapping[MetricName, float] = field(
        default_factory=lambda: MappingProxyType({})
    )