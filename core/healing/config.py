# core/healing/config.py
"""
core/healing/config.py
Políticas de control y umbrales operacionales para el subsistema de resiliencia.
"""

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class HealingPolicy:
    """Contrato formal de tolerancias y límites de reparación mecánica."""
    max_autofix_braces: int = 3
    max_autofix_math: int = 2