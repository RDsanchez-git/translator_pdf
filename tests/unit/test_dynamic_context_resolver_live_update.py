"""
Verifica que DynamicContextResolver resuelve contextos después de
actualizaciones del registry en runtime.

NADR-05 §5.1 R1: El contexto debe ser una capacidad real.
NADR-05 §5.1 R3: Fail-fast si el contexto no existe.
"""

import pytest
from core.context.context_registry import ContextRegistry
from core.context.dynamic_resolver import DynamicContextResolver


def test_resolver_resolves_after_update():
    """Registry vacío → resolver → update() → resolve() → debe resolver."""
    registry = ContextRegistry()
    resolver = DynamicContextResolver(registry=registry)

    # Registry vacío: debe fallar
    with pytest.raises(KeyError, match="UNKNOWN_CONTEXT_ID"):
        resolver.resolve("CTX_AAA")

    # Actualizar registry
    registry.update({
        "CTX_AAA": ["Root", "Section 1"],
        "CTX_BBB": ["Root", "Section 2"],
    })

    # Ahora debe resolver
    result = resolver.resolve("CTX_AAA")
    assert result.context_id == "CTX_AAA"
    assert result.breadcrumbs == ("Root", "Section 1")


def test_resolver_uses_latest_version_after_second_update():
    """update() → update() → resolve() → debe usar la última versión."""
    registry = ContextRegistry()
    resolver = DynamicContextResolver(registry=registry)

    registry.update({"CTX_AAA": ["Root", "Old Section"]})
    registry.update({"CTX_AAA": ["Root", "New Section", "Subsection"]})

    result = resolver.resolve("CTX_AAA")
    assert result.breadcrumbs == ("Root", "New Section", "Subsection")


def test_registry_update_defensive_copy():
    """update() debe copiar las listas internamente. Modificaciones externas no afectan."""
    registry = ContextRegistry()
    resolver = DynamicContextResolver(registry=registry)

    external_list = ["Root", "Section 1"]
    registry.update({"CTX_AAA": external_list})

    # Mutar la lista externa
    external_list.append("HACKED")

    # El registry no debe verse afectado
    result = resolver.resolve("CTX_AAA")
    assert result.breadcrumbs == ("Root", "Section 1")
    assert "HACKED" not in result.breadcrumbs


def test_resolve_many_atomic_failure():
    """resolve_many() debe fallar atómicamente si falta algún contexto."""
    registry = ContextRegistry()
    resolver = DynamicContextResolver(registry=registry)

    registry.update({"CTX_AAA": ["Root"]})

    with pytest.raises(KeyError, match="UNKNOWN_CONTEXT_IDS"):
        resolver.resolve_many(["CTX_AAA", "CTX_MISSING"])


def test_registry_len_contains_is_empty():
    """Utilidades de ContextRegistry."""
    registry = ContextRegistry()

    assert registry.is_empty()
    assert len(registry) == 0
    assert "CTX_AAA" not in registry

    registry.update({"CTX_AAA": ["Root"], "CTX_BBB": ["Root"]})

    assert not registry.is_empty()
    assert len(registry) == 2
    assert "CTX_AAA" in registry
    assert "CTX_CCC" not in registry