# ============================================================================
# ARCHIVO 3: core/benchmark/topology/criticality/__init__.py (actualizado)
# ============================================================================

"""
Subsistema de criticidad de nodos para regresión topológica graduada.

Exports públicos:
- NodeCriticality: Enum de 3 niveles (CRITICAL, WARNING, INFO)
- CriticalityPolicy: Protocol para políticas de clasificación
- DefaultCriticalityPolicy: Implementación canónica del mapeo
- CriticalityAwareCostContext: Contexto de costos ponderados
- CriticalityVerdictEmitter: Emisor de veredictos por criticidad
- CriticalityVerdict: DTO de veredicto por criticidad
- RecallByNodeType: DTO de recall por tipo de nodo
- ClassificationRecord: Registro de clasificación de un nodo
- ClassificationTrace: Trazabilidad completa de clasificaciones
- ClassificationTracer: Registrador stateless de clasificaciones
- ReclassificationEvent: Evento de gobernanza para reclasificaciones
- create_reclassification_event: Fábrica de eventos de reclasificación
"""
from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.criticality.ports import CriticalityPolicy
from core.benchmark.topology.criticality.policy import DefaultCriticalityPolicy
from core.benchmark.topology.criticality.costs import CriticalityAwareCostContext
from core.benchmark.topology.criticality.verdict import (
    CriticalityVerdictEmitter,
    CriticalityVerdict,
    RecallByNodeType,
)
from core.benchmark.topology.criticality.traceability import (
    ClassificationRecord,
    ClassificationTrace,
    ClassificationTracer,
    ReclassificationEvent,
    create_reclassification_event,
    CRITICALITY_POLICY_VERSION,
)

__all__ = [
    # Models
    "NodeCriticality",
    # Ports
    "CriticalityPolicy",
    # Policy
    "DefaultCriticalityPolicy",
    # Costs
    "CriticalityAwareCostContext",
    # Verdict
    "CriticalityVerdictEmitter",
    "CriticalityVerdict",
    "RecallByNodeType",
    # Traceability
    "ClassificationRecord",
    "ClassificationTrace",
    "ClassificationTracer",
    "ReclassificationEvent",
    "create_reclassification_event",
    "CRITICALITY_POLICY_VERSION",
]