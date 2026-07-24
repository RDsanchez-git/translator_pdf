from typing import Sequence

from tools.evaluation.topology.metrics import default_metrics
from tools.evaluation.topology.models import (
    BenchmarkDocument,
    BenchmarkSummaryReport,
    DocumentEvaluationResult,
    MetricResult,
)
from tools.evaluation.topology.ports import (
    BenchmarkAggregationStrategy,
    TopologyMetric,
)
from tools.evaluation.topology.strategies import DefaultBenchmarkAggregationStrategy


class TopologyBenchmarkService:
    """
    Servicio de aplicación puro para la orquestación del benchmark topológico.

    Opera exclusivamente en memoria sobre objetos DTO `BenchmarkDocument`.
    """

    def __init__(
        self,
        metrics: Sequence[TopologyMetric] | None = None,
        aggregation_strategy: BenchmarkAggregationStrategy | None = None,
    ) -> None:
        self._metrics = tuple(metrics) if metrics is not None else default_metrics()
        self._strategy = aggregation_strategy or DefaultBenchmarkAggregationStrategy()

    def evaluate_document(
        self,
        doc: BenchmarkDocument,
    ) -> DocumentEvaluationResult:
        results: list[MetricResult] = [
            metric.evaluate(doc.candidate, doc.ground_truth) for metric in self._metrics
        ]
        return DocumentEvaluationResult(doc_id=doc.doc_id, metrics=tuple(results))

    def evaluate_corpus(
        self,
        provider_name: str,
        documents: Sequence[BenchmarkDocument],
    ) -> BenchmarkSummaryReport:
        doc_results = [self.evaluate_document(doc) for doc in documents]
        return self._strategy.aggregate(
            provider_name=provider_name,
            results=doc_results,
        )