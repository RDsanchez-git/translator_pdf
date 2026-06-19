from typing import Protocol, Tuple, Dict, Iterable
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ResolvedContext:
    """SOTA: DTO inmutable, hashable y optimizado en memoria para alta frecuencia."""
    context_id: str
    breadcrumbs: Tuple[str, ...]

    @property
    def depth(self) -> int:
        return len(self.breadcrumbs)

class ContextResolverProtocol(Protocol):
    """Contrato de inversión de dependencias para hidratación topológica."""
    def resolve(self, context_id: str) -> ResolvedContext:
        ...
    
    def resolve_many(self, context_ids: Iterable[str]) -> Dict[str, ResolvedContext]:
        ...

class ContextMappingProvider(Protocol):
    """ISP: Protege el dominio de acoplarse al módulo del Pipeline/Job."""
    @property
    def mappings(self) -> Dict[str, list[str]]:
        ...

class InMemoryContextResolver:
    """Implementación SOTA O(1) en memoria pura."""
    
    def __init__(self, registry: ContextMappingProvider):
        self._mappings = registry.mappings

    def resolve(self, context_id: str) -> ResolvedContext:
        breadcrumbs = self._mappings.get(context_id)

        if breadcrumbs is None:
            raise KeyError(f"UNKNOWN_CONTEXT_ID: Falta mapeo topológico para '{context_id}'")

        return ResolvedContext(context_id=context_id, breadcrumbs=tuple(breadcrumbs))

    def resolve_many(self, context_ids: Iterable[str]) -> Dict[str, ResolvedContext]:
        """Procesamiento por lotes con deduplicación estable (preserva orden) y falla atómica."""
        missing = []
        results = {}
        
        # SOTA: Deduplicación O(N) preservando el orden de llegada original
        unique_ids = dict.fromkeys(context_ids)
        
        for cid in unique_ids:
            breadcrumbs = self._mappings.get(cid)
            if breadcrumbs is None:
                missing.append(cid)
            else:
                results[cid] = ResolvedContext(context_id=cid, breadcrumbs=tuple(breadcrumbs))
        
        if missing:
            raise KeyError(f"UNKNOWN_CONTEXT_IDS: Fallo de hidratación para los siguientes IDs: {missing}")
            
        return results