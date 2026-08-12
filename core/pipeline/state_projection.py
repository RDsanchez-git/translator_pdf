# core/pipeline/state_projection.py
"""
Proyección del ciclo de vida operacional sobre el modelo de dominio.

NADR-09 §5.1 R3: Los pasos de la aplicación MUST estar sincronizados
con los estados de la máquina de estados finitos.

Ubicación: core/pipeline/ (NO core/execution/).
Dirección de dependencia correcta: pipeline → execution.
El dominio (DocumentState) nunca depende de la vista operacional (PipelineStep).

La proyección es UNIDIRECCIONAL: PipelineStep → DocumentState.
"""

from typing import Protocol, runtime_checkable

from core.pipeline.job import PipelineStep
from core.execution.state import DocumentState


@runtime_checkable
class PipelineStateProjectionPolicy(Protocol):
    """
    Política de proyección PipelineStep → DocumentState.

    Relación N:1 — múltiples pasos operacionales pueden proyectar
    al mismo estado de dominio (ej: CHUNKING y DISPATCHING → PROCESSING).
    """

    def project(self, step: PipelineStep) -> DocumentState:
        """
        Proyecta un paso operacional a un estado de dominio.

        Raises:
            ValueError: Si el paso no tiene proyección definida.
        """
        ...


class DefaultPipelineStateProjection:
    """
    Proyección por defecto para el pipeline de producción.

    Matriz de transición normativa (Task 4.1.1, Paso A.1.a — FROZEN).
    """

    _PROJECTION: dict[PipelineStep, DocumentState] = {
        PipelineStep.INITIALIZING: DocumentState.CREATED,
        PipelineStep.PARSING: DocumentState.PARSING,
        PipelineStep.CHUNKING: DocumentState.PROCESSING,
        PipelineStep.DISPATCHING: DocumentState.PROCESSING,
        PipelineStep.READY_FOR_ASSEMBLY: DocumentState.READY_FOR_ASSEMBLY,
        PipelineStep.ASSEMBLING: DocumentState.ASSEMBLING,
        PipelineStep.READY_FOR_COMPILATION: DocumentState.READY_FOR_COMPILATION,
        PipelineStep.COMPILING: DocumentState.COMPILING,
        PipelineStep.FINISHED: DocumentState.COMPLETED,
    }

    def project(self, step: PipelineStep) -> DocumentState:
        projected = self._PROJECTION.get(step)
        if projected is None:
            raise ValueError(
                f"PipelineStep.{step.name} no tiene proyección a DocumentState. "
                f"Verificar matriz de transición normativa (NADR-09 §5.1 R3)."
            )
        return projected