from typing import Callable, Dict, Sequence

from tools.evaluation.topology.metrics.node_count import NodeCountMetric
from tools.evaluation.topology.metrics.recall import EntityRecallMetric
from tools.evaluation.topology.metrics.sequence import SequenceAlignmentMetric
from tools.evaluation.topology.metrics.structural import StructuralTopologyMetric
from tools.evaluation.topology.ports import TopologyMetric


class UnknownMetricProfileError(ValueError):
    """Excepción de configuración al solicitar un perfil de métricas no registrado."""

    pass


def default_metrics() -> Sequence[TopologyMetric]:
    """Devuelve la colección de métricas topológicas activas en producción."""
    return (
        NodeCountMetric(),
        EntityRecallMetric(),
        SequenceAlignmentMetric(),
        StructuralTopologyMetric(),
    )


MetricFactory = Callable[[], Sequence[TopologyMetric]]


class MetricRegistry:
    """Registro centralizado para resolución dinámica y composición perezosa de métricas."""

    _profiles: Dict[str, MetricFactory] = {
        "default": default_metrics,
    }

    @classmethod
    def register(cls, profile: str, factory: MetricFactory) -> None:
        """
        Registra una fábrica de métricas bajo un identificador de perfil.
        Uso exclusivo durante la fase de bootstrap/inicialización de la aplicación.
        """
        cls._profiles[profile] = factory

    @classmethod
    def resolve(cls, profile: str = "default") -> Sequence[TopologyMetric]:
        """Resuelve e instancia perezosamente el perfil de métricas solicitado."""
        if profile not in cls._profiles:
            available = ", ".join(cls._profiles.keys())
            raise UnknownMetricProfileError(
                f"Perfil de métrica '{profile}' no registrado. Perfiles disponibles: {available}"
            )
        return cls._profiles[profile]()


__all__ = [
    "NodeCountMetric",
    "EntityRecallMetric",
    "SequenceAlignmentMetric",
    "StructuralTopologyMetric",
    "default_metrics",
    "MetricRegistry",
    "UnknownMetricProfileError",
]