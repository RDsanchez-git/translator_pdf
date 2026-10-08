import os
import psutil
from core.execution.models import ExecutionEnvelope
from core.execution.exceptions import ResourceExhaustedError


class PsutilSelfResourceMonitor:
    """
    Adaptador de infraestructura. Monitorea el proceso actual (daemon).
    Cumple con ResourceMonitorPort.

    Nota: psutil sobre PID propio es exacto en Windows/Linux.
    El tree-monitoring Win32 (HITO_0.7) solo aplica a child processes;
    aquí monitoreamos el self-process, por lo que psutil es válido.
    """
    def __init__(self) -> None:
        self._process = psutil.Process(os.getpid())

    def get_current_rss_mb(self) -> float:
        return self._process.memory_info().rss / (1024 * 1024)

    def check_envelope(self, envelope: ExecutionEnvelope) -> None:
        current_rss = self.get_current_rss_mb()
        if current_rss > envelope.max_rss_mb:
            raise ResourceExhaustedError(
                resource_type="RSS_MB",
                limit=envelope.max_rss_mb,
                actual=current_rss,
            )