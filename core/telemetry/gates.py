import logging
from enum import Enum
from core.telemetry.models import ProductionHealthReport

logger = logging.getLogger(__name__)

class SystemHealthState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    BLOCKED = "blocked"

class HealthGateEvaluator:
    """SOTA: Controlador de admisión y disyuntor de estado de migración."""
    
    @staticmethod
    def evaluate(report: ProductionHealthReport) -> SystemHealthState:
        if report.is_healthy:
            return SystemHealthState.HEALTHY

        is_blocked = False
        is_degraded = False

        for violation in report.slo_violations:
            if violation.metric in ("translation_failure_ratio", "context_overflow_ratio"):
                logger.critical(f"[HEALTH GATE FATAL] Violación de {violation.metric}: {violation.actual_value} > {violation.threshold}")
                is_blocked = True
            
            elif violation.metric in ("p95_quota_wait_ms", "effective_tps"):
                logger.warning(f"[HEALTH DEGRADATION] Violación de {violation.metric}: {violation.actual_value} vs límite {violation.threshold}")
                is_degraded = True

        if is_blocked:
            return SystemHealthState.BLOCKED
        if is_degraded:
            return SystemHealthState.DEGRADED
            
        return SystemHealthState.HEALTHY

    @staticmethod
    def enforce(report: ProductionHealthReport) -> None:
        state = HealthGateEvaluator.evaluate(report)
        
        if state == SystemHealthState.BLOCKED:
            raise RuntimeError(
                f"MIGRATION BLOCKED (Execution {report.execution_id}): Abortando ejecución "
                "por ruptura irrecuperable de SLOs de integridad documental."
            )
        elif state == SystemHealthState.DEGRADED:
            logger.warning("El sistema opera en estado DEGRADED. Rendimiento por debajo del Baseline operativo.")