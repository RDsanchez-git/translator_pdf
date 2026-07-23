class ProcessRunnerError(Exception):
    """Excepción base para fallas en el ejecutor de subprocesos aislados."""
    pass


class ProcessTimeoutError(ProcessRunnerError):
    """Lanzada cuando la ejecución de la CLI excede el tiempo máximo configurado."""
    pass


class ProcessExecutionError(ProcessRunnerError):
    """Lanzada cuando el subproceso finaliza con código de salida no nulo (exit_code != 0)."""
    pass
