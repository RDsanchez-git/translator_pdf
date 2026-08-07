# core/context/dynamic_resolver.py
"""
Resolver dinámico que consulta el registry en cada llamada.

NADR-05 §5.1 R3: Si el contexto no puede resolverse, el sistema
MUST fallar de forma explícita (fail-fast).

POLÍTICA DE RESOLUCIÓN:
- Fail Fast: si un context_id no existe, se lanza KeyError inmediatamente.
- Sin fallback: nunca se retorna un ResolvedContext con breadcrumbs vacías.
- Sin degradación: no existe camino de ejecución que produzca
  una traducción descontextualizada silenciosamente.
- Sin warning: la ausencia de contexto es un error, no un warning.
- Siempre UNKNOWN_CONTEXT_ID si el contexto no existe.
"""

from typing import Dict, Iterable
from core.context.context_registry import ContextRegistry
from core.context.context_resolver import ResolvedContext


class DynamicContextResolver:
    """
    Resolver que consulta el ContextRegistry dinámicamente en cada llamada.

    Implementa ContextResolverProtocol.

    Diferencia con InMemoryContextResolver:
    - InMemoryContextResolver: snapshot inmutable en construcción.
    - DynamicContextResolver: consulta el registry en cada llamada.

    Ambos implementan el mismo protocolo. El Composition Root elige
    cuál usar según el modo de ejecución.
    """

    def __init__(self, registry: ContextRegistry) -> None:
        self._registry = registry

    def resolve(self, context_id: str) -> ResolvedContext:
        """
        Resuelve un contexto individual.

        Lanza KeyError si el context_id no existe en el registry.
        NADR-05 §5.1 R3: Fail fast. Sin fallback.
        """
        breadcrumbs = self._registry.get(context_id)

        if breadcrumbs is None:
            raise KeyError(
                f"UNKNOWN_CONTEXT_ID: Falta mapeo topológico para '{context_id}'"
            )

        return ResolvedContext(context_id=context_id, breadcrumbs=tuple(breadcrumbs))

    def resolve_many(self, context_ids: Iterable[str]) -> Dict[str, ResolvedContext]:
        """
        Resuelve múltiples contextos con deduplicación y falla atómica.

        NADR-05 §5.1 R3: Si algún context_id no existe, se lanzan
        todos los IDs faltantes en un solo KeyError. No se resuelve
        parcialmente.
        """
        missing = []
        results = {}

        unique_ids = dict.fromkeys(context_ids)

        for cid in unique_ids:
            breadcrumbs = self._registry.get(cid)
            if breadcrumbs is None:
                missing.append(cid)
            else:
                results[cid] = ResolvedContext(context_id=cid, breadcrumbs=tuple(breadcrumbs))

        if missing:
            raise KeyError(
                f"UNKNOWN_CONTEXT_IDS: Fallo de hidratación para los siguientes IDs: {missing}"
            )

        return results