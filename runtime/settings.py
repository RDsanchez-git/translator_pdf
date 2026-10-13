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
    # === F18.1: Configuración existente ===
    reconciliation_enabled: bool = True
    sweep_interval_seconds: float = 45.0
    sweep_jitter_seconds: float = 5.0
    
    # === F18.2: Activación de contratos de ejecución durable ===
    # Gate 1: Autoridad de ejecución y recuperación conservadora
    conservative_recovery_enabled: bool = False
    semantic_classification_enabled: bool = False
    
    # Gate 3: Observabilidad estratificada de duplicación
    stratified_observability_enabled: bool = False