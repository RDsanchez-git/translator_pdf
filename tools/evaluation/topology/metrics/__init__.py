from typing import Sequence

from tools.evaluation.topology.metrics.node_count import NodeCountMetric
from tools.evaluation.topology.metrics.recall import EntityRecallMetric
from tools.evaluation.topology.metrics.sequence import SequenceAlignmentMetric
from tools.evaluation.topology.metrics.structural import StructuralTopologyMetric
from tools.evaluation.topology.ports import TopologyMetric


def default_metrics() -> Sequence[TopologyMetric]:
    """Devuelve la colección de métricas topológicas activas en producción."""
    return (
        NodeCountMetric(),
        EntityRecallMetric(),
        SequenceAlignmentMetric(),
        StructuralTopologyMetric(),
    )


__all__ = [
    "NodeCountMetric",
    "EntityRecallMetric",
    "SequenceAlignmentMetric",
    "StructuralTopologyMetric",
    "default_metrics",
]