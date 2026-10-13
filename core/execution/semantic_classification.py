"""
Clasificación semántica de resultados de efectos externos.

NADR-F18-03 §5.2 R5-R8:
- CONFIRMED: Existe evidencia autoritativa de que el efecto externo ocurrió.
- NOT_STARTED: Demostrablemente no se inició el efecto externo.
- UNCERTAIN: No se puede determinar si el efecto externo ocurrió o no.

Principio rector (NADR-F18-03 §5.2 R8): Comportamiento por defecto conservador.

Diseño conforme a NADR-F18-03 §5.2: "Implementar distinción sin exigir enums
físicos específicos". Se usa typing.Literal para type-safety sin la rigidez
de un Enum físico, y una función pura derivada de evidencia observable.

Cumple NADR-F18-05 §5.5 R13: La clasificación es siempre consistente con la
evidencia real, nunca puede desincronizarse (no hay fuentes de verdad paralelas).
"""
from typing import Literal
from dataclasses import dataclass

# NADR-F18-03 §5.2: Taxonomía semántica de resultados de efectos externos.
# Literal en lugar de Enum físico: type-safety + exhaustiveness sin rigidez.
ExternalEffectKind = Literal["CONFIRMED", "NOT_STARTED", "UNCERTAIN"]

# Estados de tarea observables en el control plane (chunk_tasks.task_state).
# PENDING es el único estado que demuestra que la tarea nunca fue tomada.
_NOT_STARTED_STATES = frozenset({"PENDING"})


@dataclass(frozen=True)
class ExternalEffectEvidence:
    """
    Evidencia mínima necesaria para clasificación semántica.
    
    Esta estructura encapsula los datos observables requeridos para derivar
    la clasificación sin crear fuentes de verdad paralelas (NADR-F18-05 §5.5 R13).
    
    Inmutable (frozen=True) conforme a ENGINEERING_PRINCIPLES §III.
    
    Attributes:
        task_state: Estado actual de la tarea en el control plane
            (PENDING, PROCESSING, COMPLETED, FAILED, RETRYABLE_ERROR).
        has_generated_event: True si existe un evento GENERATED en el journal
            para el node_id de esta tarea. Es la evidencia autoritativa de
            que el efecto externo ocurrió (NADR-F18-03 §5.2 R6).
    """
    task_state: str
    has_generated_event: bool


def classify_external_effect(evidence: ExternalEffectEvidence) -> ExternalEffectKind:
    """
    Deriva la clasificación semántica basada estrictamente en evidencia observable.
    
    Función pura y determinista (ENGINEERING_PRINCIPLES §II: Functional Core).
    Sin I/O, sin efectos secundarios, sin estado.
    
    Args:
        evidence: Evidencia observable del estado de la tarea y el journal.
    
    Returns:
        ExternalEffectKind: Clasificación semántica del resultado.
    
    Note:
        Comportamiento por defecto conservador (NADR-F18-03 §5.2 R8):
        si no podemos demostrar que el efecto NO se inició, asumimos UNCERTAIN.
        Esto previene reejecución automática de efectos potencialmente duplicados.
    """
    # (a) CONFIRMED: existe evento GENERATED en el journal.
    # Esta es evidencia autoritativa de que el efecto externo ocurrió y
    # tenemos el resultado persistido (NADR-F18-03 §5.2 R6).
    if evidence.has_generated_event:
        return "CONFIRMED"
    
    # (b) NOT_STARTED: el estado de la tarea demuestra que nunca se ejecutó.
    # Solo PENDING garantiza que la tarea nunca fue tomada por un worker.
    # (NADR-F18-03 §5.2 R7: no-inicio demostrablemente verificado)
    if evidence.task_state in _NOT_STARTED_STATES:
        return "NOT_STARTED"
    
    # (c) UNCERTAIN: comportamiento por defecto conservador.
    # Esto incluye:
    # - PROCESSING: crash durante I/O (efecto externo pudo ocurrir)
    # - FAILED: pudo fallar POST-effecto/pre-journal
    # - RETRYABLE_ERROR: misma razón
    # - COMPLETED sin evento: inconsistencia (defensivo)
    # - Cualquier otro estado no explícitamente NOT_STARTED
    #
    # No podemos demostrar que el efecto externo no se inició, por lo tanto
    # asumimos incertidumbre. El reconciler (Task 1.2.1) decidirá si reejecutar.
    # (NADR-F18-03 §5.2 R8)
    return "UNCERTAIN"