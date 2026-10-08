"""
Implementación de visibilidad operacional vía logging estructurado.

NADR-F18-02 §5.7 R23/R26: mínima, sin observabilidad profunda.
R25: los logs son evidencia operacional; el contenido científico vive
en el materialized plane y el AST, nunca aquí.

Durabilidad: los estados terminales YA persisten de forma durable en el
control plane (mark_task_completed / abandon_execution) y en el WAL
(chunk_completed / chunk_cancelled). Este mecanismo agrega la superficie
observable unificada (R24) sin duplicar persistencia (YAGNI).

ENGINEERING_PRINCIPLES §IV: observe() es fail-safe: si el sink falla,
se registra el fallo del sink pero NO se propaga ni se silencia.
"""
from __future__ import annotations

import logging

from core.execution.visibility import WorkUnitObservation

logger = logging.getLogger(__name__)


class StructuredLogVisibility:
    """
    Emite observaciones como logs estructurados indexables.
    Cumple OperationalVisibilityPort.
    """

    def observe(self, observation: WorkUnitObservation) -> None:
        try:
            logger.info(
                "[VISIBILITY] task=%s worker=%s status=%s reason=%s t=%.3f",
                observation.task_id[:8],
                observation.worker_id,
                observation.status.name,
                observation.reason,
                observation.observed_at,
            )
        except Exception as e:
            # Fail-safe: la visibilidad nunca rompe la ejecución (R23),
            # pero el fallo del sink no se silencia (§IV).
            logger.error(f"[VISIBILITY] observe failed: {e}")