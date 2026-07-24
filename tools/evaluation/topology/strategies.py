from types import MappingProxyType
from typing import Sequence

from tools.evaluation.topology.models import (
    BenchmarkSummaryReport,
    DocumentEvaluationResult,
    MetricName,
)
from tools.evaluation.topology.ports import BenchmarkAggregationStrategy


class DefaultBenchmarkAggregationStrategy(BenchmarkAggregationStrategy):
    """Estrategia canónica de agregación que calcula promedios aritméticos simples por métrica."""

    def aggregate(
        self,
        provider_name: str,
        results: Sequence[DocumentEvaluationResult]
    ) -> BenchmarkSummaryReport:
        if not results:
            return BenchmarkSummaryReport(
                provider_name=provider_name,
                total_documents=0,
                document_results=tuple(),
                summary_metrics=MappingProxyType({}),
            )

        metric_sums: dict[MetricName, float] = {}
        metric_counts: dict[MetricName, int] = {}

        for doc_res in results:
            for metric in doc_res.metrics:
                key = metric.metric_name
                metric_sums[key] = metric_sums.get(key, 0.0) + metric.value
                metric_counts[key] = metric_counts.get(key, 0) + 1

        aggregated: dict[MetricName, float] = {
            key: metric_sums[key] / metric_counts[key]
            for key in metric_sums
        }

        return BenchmarkSummaryReport(
            provider_name=provider_name,
            total_documents=len(results),
            document_results=tuple(results),
            summary_metrics=MappingProxyType(aggregated),
        )