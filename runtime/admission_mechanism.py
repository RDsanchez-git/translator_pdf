"""
Implementación del mecanismo de admisión basado en recursos.

NADR-F18-02 §5.2 R5: mecanismo explícito.
DC-01: el daemon es secuencial, la admisión es un check de envelope
antes de reclamar. Si se deniega, el daemon NO reclama (R6: no retención).
"""
from __future__ import annotations

from core.execution.admission import AdmissionDecision


class SequentialAdmissionMechanism:
    """
    Mecanismo de admisión para daemon secuencial.
    
    Evalúa el resource envelope ANTES de reclamar trabajo.
    Si el envelope se viola, deniega la admisión sin retener recursos.
    
    NADR-F18-02 §5.2 R6: sin retención de recursos para trabajo rechazado.
    DC-01: daemon secuencial, no hay concurrencia que bounded.
    """

    def __init__(self, safety_margin: float = 0.90) -> None:
        """
        Args:
            safety_margin: Fracción del límite máximo que triggera HOLD.
                           Default 0.90 (90% del límite = HOLD).
        """
        self._safety_margin = safety_margin

    def evaluate(self, current_rss_mb: float, max_rss_mb: float) -> AdmissionDecision:
        """
        Evalúa si el envelope permite admitir nueva tarea.
        
        Lógica:
        - Si RSS > max_rss: REJECT (envelope violado)
        - Si RSS > max_rss * safety_margin: HOLD (presión de recursos)
        - Si RSS <= max_rss * safety_margin: ALLOW (envelope OK)
        """
        # Envelope violado: rechazo definitivo
        if current_rss_mb > max_rss_mb:
            return AdmissionDecision.reject(
                f"CRITICAL: RSS {current_rss_mb:.2f}MB > Limit {max_rss_mb:.2f}MB"
            )

        # Presión de recursos: HOLD (backpressure sin detener)
        threshold_mb = max_rss_mb * self._safety_margin
        if current_rss_mb > threshold_mb:
            return AdmissionDecision.hold(
                f"Pressure: RSS {current_rss_mb:.2f}MB > Threshold {threshold_mb:.2f}MB"
            )

        # Envelope OK: ALLOW
        return AdmissionDecision.allow()