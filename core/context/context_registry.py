# core/context/context_registry.py
"""
Dueño único de los mappings de contexto jerárquico.

NADR-05 §5.1 R1: El contexto debe ser una capacidad real en todo punto de inyección.
NADR-05 §5.1 R3: Si el contexto no puede resolverse, el sistema MUST fallar de forma explícita.

El registry encapsula el estado mutable internamente.
Nunca expone el dict mutable. Solo expone snapshots readonly.
"""

from types import MappingProxyType
from typing import Dict, List, Mapping


class ContextRegistry:
    """
    Dueño único de los mappings de contexto jerárquico.

    HierarchicalContextEnricher genera los mappings en runtime.
    TranslationPipeline.execute() actualiza este registry.
    RuntimeContextMappingProvider expone snapshots readonly.
    DynamicContextResolver consulta via el provider.

    NADR-05: El registry es mutable internamente pero expone
    snapshots inmutables externamente.
    """

    def __init__(self) -> None:
        self._mappings: Dict[str, List[str]] = {}

    def update(self, new_mappings: Dict[str, List[str]]) -> None:
        """
        Reemplaza los mappings completos con copia defensiva.

        AJUSTE OBLIGATORIO: Copia profunda superficial de las listas internas
        para prevenir que referencias externas muten el estado del registry.
        """
        self._mappings = {
            k: list(v)
            for k, v in new_mappings.items()
        }

    def get(self, context_id: str) -> List[str] | None:
        """Retorna una copia de las breadcrumbs para un context_id, o None si no existe."""
        breadcrumbs = self._mappings.get(context_id)
        if breadcrumbs is None:
            return None
        return list(breadcrumbs)

    def snapshot(self) -> Mapping[str, List[str]]:
        """
        Retorna un snapshot readonly de los mappings.

        Usa MappingProxyType para prevenir modificación accidental.
        Las listas internas se copian para aislamiento completo.
        """
        return MappingProxyType({
            k: list(v) for k, v in self._mappings.items()
        })

    def clear(self) -> None:
        """Vacía el registry. Útil para reinicialización entre documentos."""
        self._mappings = {}

    def __len__(self) -> int:
        """Cantidad de contextos registrados."""
        return len(self._mappings)

    def __contains__(self, context_id: str) -> bool:
        """Verifica si un context_id existe en el registry."""
        return context_id in self._mappings

    def is_empty(self) -> bool:
        """Indica si el registry no tiene contextos registrados."""
        return len(self._mappings) == 0