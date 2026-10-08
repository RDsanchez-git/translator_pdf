"""
Mecanismo de admisión del execution plane.

NADR-F18-02 §5.2:
  R5: Mecanismo de admisión explícito.
  R6: No retención de recursos para trabajo rechazado.
  R7: Mecanismo/política separados (mecanismo = cómo se decide;
      política = cuándo se admite, corresponde a Subfase 18.3).

Este módulo define el MECANISMO (puerto + modelo). La implementación
concreta está en runtime/admission_mechanism.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol, runtime_checkable


class AdmissionStatus(Enum):
    """
    Estados de una decisión de admisión.
    
    ALLOW: Admisión concedida, se puede reclamar trabajo.
    REJECT: Rechazo definitivo (ej. recursos agotados, envelope violado).
    HOLD: Pausa temporal (ej. presión transitoria de recursos).
    """
    ALLOW = auto()
    REJECT = auto()
    HOLD = auto()


@dataclass(frozen=True)
class AdmissionDecision:
    """
    Resultado inmutable de una decisión de admisión.
    
    NADR-F18-02 §5.2 R5: la decisión es explícita y verificable.
    NADR-F18-02 §5.1 R4: outcome operacional identificable.
    """
    status: AdmissionStatus
    reason: str = ""

    @classmethod
    def allow(cls, reason: str = "envelope_ok") -> "AdmissionDecision":
        """Admisión concedida: el envelope permite reclamar trabajo."""
        return cls(status=AdmissionStatus.ALLOW, reason=reason)

    @classmethod
    def reject(cls, reason: str) -> "AdmissionDecision":
        """Admisión denegada definitivamente."""
        return cls(status=AdmissionStatus.REJECT, reason=reason)

    @classmethod
    def hold(cls, reason: str) -> "AdmissionDecision":
        """Admisión pausada temporalmente (backpressure)."""
        return cls(status=AdmissionStatus.HOLD, reason=reason)


@runtime_checkable
class AdmissionMechanismPort(Protocol):
    """
    Puerto hexagonal para el mecanismo de admisión.
    
    NADR-F18-02 §5.2 R7: el mecanismo es separable de la política.
    Implementado en runtime/admission_mechanism.py.
    """
    def evaluate(self, current_rss_mb: float, max_rss_mb: float) -> AdmissionDecision:
        """
        Evalúa si se puede admitir nueva tarea.
        
        NADR-F18-02 §5.2 R6: si se deniega, NO se retienen recursos
        (el daemon simplemente no reclama y espera).
        
        Args:
            current_rss_mb: RSS actual del proceso en MB.
            max_rss_mb: Límite máximo del envelope en MB.
            
        Returns:
            AdmissionDecision: ALLOW, REJECT o HOLD.
        """
        ...