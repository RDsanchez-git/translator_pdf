# core/healing/base.py
"""
core/healing/base.py
Interfaz de contrato estricta para estrategias de curación deterministas O(1).
"""

from abc import ABC, abstractmethod
from core.healing.models import HealingContext, HealingResult

class BaseHealingStrategy(ABC):
    """
    Contrato base para mutaciones de un solo paso sobre el payload de traducción.
    """

    @property
    @abstractmethod
    def invariant_family(self) -> str:
        """Familia del invariante del ADR-003 mapeado a esta estrategia (ej. 'SI-01')."""
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """
        Precedencia de ejecución en pipelines de fallos múltiples concurrentes.
        Menor valor numérico indica mayor prioridad de ejecución (estilo Unix priority/niceness).
        Ejemplo: Perímetro = 100, Estructural = 200.
        """
        pass

    @abstractmethod
    def heal(self, context: HealingContext) -> HealingResult:
        """
        Transformación física del texto. 
        Debe retornar el payload de texto completo modificado en caso de éxito.
        """
        pass