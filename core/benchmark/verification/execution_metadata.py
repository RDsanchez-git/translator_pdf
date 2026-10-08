"""
Metadata operacional de ejecución para Continuous Verification.

NADR-F18-01:
  §5.2 R7/R9: execution identity identificable y registrable.
  §5.2 R8: execution identity MUST NOT formar parte de scientific identity.
  §5.3 R13: operational state registrable como evidencia separada.
  §5.5 R19: artefacto lleva ambas identidades (científica + ejecución).
  §5.5 R20: evidencia operacional trazable a la ejecución que la produjo.

Resuelve DF-13: model_de_execution ausente de identity_chain.
El modo de ejecución se registra como metadata operacional separada,
sin modificar IdentityChain ni execution_id (backward compatible).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionMetadata:
    """
    Metadata operacional de una ejecución de Continuous Verification.
    
    Inmutable. Evidencia operacional separada de la científica (R8, R13).
    
    Fields:
        model_de_execution: Modo de ejecución identificable (R7, R9).
            Ejemplos: "sequential_regression", "sequential_daemon".
        execution_timestamp_iso8601: Timestamp de inicio (evidencia operacional).
        telemetry_execution_id: UUID de telemetría operacional (si aplica).
    """
    model_de_execution: str
    execution_timestamp_iso8601: str
    telemetry_execution_id: str | None = None