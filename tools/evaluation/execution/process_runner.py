import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence

from tools.evaluation.execution.errors import (
    ProcessExecutionError,
    ProcessTimeoutError,
)


@dataclass(frozen=True)
class ProcessExecutionResult:
    """DTO inmutable de telemetría y resultado de subproceso aislado."""
    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    elapsed_time_ms: float
    artifacts: tuple[Path, ...] = field(default_factory=tuple)


class ExternalProcessRunner:
    """
    Ejecutor de subprocesos aislados para la invocación de herramientas CLI externas
    en el ecosistema de evaluación y benchmarking.
    
    Responsabilidad exclusiva: Invocación de bajo nivel, aislamiento y verificación de presencia
    de artefactos en disco. La ausencia de artefactos esperados no constituye un error del runner.
    Corresponde al consumidor (ExtractionProvider) decidir si la falta de dichos archivos invalida
    la extracción.
    """

    def __init__(self, timeout_seconds: float = 300.0) -> None:
        self._timeout_seconds = timeout_seconds

    def run(
        self,
        command: Sequence[str],
        expected_outputs: Optional[Sequence[Path]] = None,
        cwd: Optional[Path] = None,
        env: Optional[Mapping[str, str]] = None
    ) -> ProcessExecutionResult:
        start_time = time.perf_counter()
        cmd_tuple = tuple(command)
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)

        try:
            completed = subprocess.run(
                list(cmd_tuple),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=self._timeout_seconds,
                cwd=cwd,
                env=exec_env,
                check=False
            )
        except subprocess.TimeoutExpired as err:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            raise ProcessTimeoutError(
                f"El subproceso excedió el tiempo límite de {self._timeout_seconds}s. "
                f"Comando: '{' '.join(cmd_tuple)}'. Transcurrido: {elapsed_ms:.2f}ms"
            ) from err

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if completed.returncode != 0:
            raise ProcessExecutionError(
                f"El subproceso falló con exit_code={completed.returncode}.\n"
                f"Comando: {' '.join(cmd_tuple)}\n"
                f"STDERR:\n{completed.stderr.strip()}\n"
                f"STDOUT:\n{completed.stdout.strip()}"
            )

        found_artifacts: list[Path] = []
        if expected_outputs:
            for artifact_path in expected_outputs:
                if artifact_path.exists() and artifact_path.is_file():
                    found_artifacts.append(artifact_path)

        return ProcessExecutionResult(
            command=cmd_tuple,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            elapsed_time_ms=elapsed_ms,
            artifacts=tuple(found_artifacts)
        )