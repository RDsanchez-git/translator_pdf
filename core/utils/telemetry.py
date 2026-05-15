import logging
import json
import time
from functools import wraps
from contextvars import ContextVar
from datetime import datetime, timezone

# SOTA: Variables de Contexto Distribuido. 
# Viajan invisiblemente a través del Call Stack del hilo actual.
ctx_execution_id: ContextVar[str] = ContextVar("execution_id", default="-")
ctx_worker_id: ContextVar[str] = ContextVar("worker_id", default="-")
ctx_task_id: ContextVar[str] = ContextVar("task_id", default="-")
ctx_node_id: ContextVar[str] = ContextVar("node_id", default="-")

class DistributedContextFilter(logging.Filter):
    """Inyecta la causalidad distribuida en cada registro de log sin pasarlo por parámetros."""
    def filter(self, record):
        record.execution_id = ctx_execution_id.get()
        record.worker_id = ctx_worker_id.get()
        record.task_id = ctx_task_id.get()
        record.node_id = ctx_node_id.get()
        return True

class JSONFormatter(logging.Formatter):
    """SOTA: Salida estructurada obligatoria para observabilidad de plataformas."""
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "trace_id": getattr(record, "execution_id", "-"),
            "worker_id": getattr(record, "worker_id", "-"),
            "task_id": getattr(record, "task_id", "-"),
            "node_id": getattr(record, "node_id", "-"),
            "message": record.getMessage(),
        }
        
        # Merge de datos extra inyectados manualmente (ej: extra={"extra_data": {"metric": 1}})
        # Extraer de forma segura para satisfacer al Type Checker
        extra_data = getattr(record, "extra_data", None)
        if isinstance(extra_data, dict):
            log_record.update(extra_data)
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        # SOTA: default=str evita crashes por Enums, UUIDs o Exceptions no serializables nativamente
        return json.dumps(log_record, default=str)

_LOGGER_INITIALIZED = False

def setup_distributed_logger():
    """Configura el logger root confiando estrictamente en el centinela local."""
    global _LOGGER_INITIALIZED
    
    # SOTA: Ignoramos logger.handlers para no colisionar con frameworks externos
    if _LOGGER_INITIALIZED:
        return logging.getLogger()
        
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.addFilter(DistributedContextFilter())
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    _LOGGER_INITIALIZED = True
    return logger


def track_latency(operation_name: str):
    """Decorador SOTA para emitir automáticamente logs con duration_ms."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            except Exception:
                # SOTA: Contrato explícito de propagación de excepciones en capa de telemetría
                raise
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                logger = logging.getLogger(func.__module__)
                logger.info(
                    f"{operation_name} completed", 
                    extra={"extra_data": {"duration_ms": round(duration_ms, 2), "operation": operation_name}}
                )
        return wrapper
    return decorator