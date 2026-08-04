"""
Configuración del runtime inyectada desde la Composition Root.

NADR-10 §5.2 R11: La activación de mecanismos del runtime MUST estar
gobernada por configuración externa, no por banderas hardcodeadas.
NADR-11 §5.1 R1: La inyección se realiza por constructor desde la Composition Root.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSettings:
    """
    Configuración inmutable del runtime.
    
    El daemon de reconciliación y otros componentes del runtime
    reciben esta configuración por inyección. No consultan variables
    de entorno directamente.
    """
    reconciliation_enabled: bool = True
    sweep_interval_seconds: float = 45.0
    sweep_jitter_seconds: float = 5.0