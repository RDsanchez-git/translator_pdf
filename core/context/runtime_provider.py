# core/context/runtime_provider.py
"""
Provider que implementa ContextMappingProvider exponiendo
snapshots del ContextRegistry.

NADR-05: El provider no almacena mappings propios.
Almacena una referencia al registry. Existe una sola copia del estado.

AJUSTE OBLIGATORIO: Devuelve el snapshot del registry directamente,
sin reconstruirlo. El snapshot ya es readonly via MappingProxyType.
"""

from typing import List, Mapping
from core.context.context_registry import ContextRegistry


class RuntimeContextMappingProvider:
    """
    Implementación de ContextMappingProvider que delega al ContextRegistry.

    No copia mappings. Almacena una referencia al registry.
    La propiedad mappings() retorna el snapshot readonly del registry directamente.

    Esto garantiza que existe una sola copia del estado. Nunca dos.
    """

    def __init__(self, registry: ContextRegistry) -> None:
        self._registry = registry

    @property
    def mappings(self) -> Mapping[str, List[str]]:
        """
        Snapshot readonly de los mappings actuales del registry.

        AJUSTE OBLIGATORIO: Devuelve el snapshot directamente.
        No se reconstruye el dict. El MappingProxyType del registry
        ya garantiza inmutabilidad.
        """
        return self._registry.snapshot()