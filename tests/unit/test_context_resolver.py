import unittest
from typing import Dict, List
from core.context.context_resolver import InMemoryContextResolver

class FakeRegistry:
    def __init__(self, mappings: Dict[str, List[str]]):
        self._mappings = mappings
        
    @property
    def mappings(self) -> Dict[str, List[str]]:
        return self._mappings

class TestInMemoryContextResolver(unittest.TestCase):
    """Certificación rigurosa de la Fase 14.00.1 (Congelada)."""

    def setUp(self):
        self.fake_registry = FakeRegistry(mappings={
            "CTX_A1": ["Chapter 1", "Methodology"],
            "CTX_ROOT": ["Root"]
        })
        self.resolver = InMemoryContextResolver(registry=self.fake_registry)

    def test_resolve_valid_context(self):
        res = self.resolver.resolve("CTX_A1")
        self.assertEqual(res.context_id, "CTX_A1")
        self.assertEqual(res.breadcrumbs, ("Chapter 1", "Methodology"))
        self.assertEqual(res.depth, 2)

    def test_resolve_unknown_context(self):
        with self.assertRaisesRegex(KeyError, "UNKNOWN_CONTEXT_ID"):
            self.resolver.resolve("CTX_GHOST")

    def test_breadcrumbs_are_tuple(self):
        res = self.resolver.resolve("CTX_A1")
        self.assertIsInstance(res.breadcrumbs, tuple)

    def test_resolved_context_hashable(self):
        res = self.resolver.resolve("CTX_A1")
        cache = {res: "cached_value"}
        self.assertEqual(cache[res], "cached_value")

    def test_resolve_many_success_and_deduplication(self):
        res = self.resolver.resolve_many(["CTX_A1", "CTX_ROOT", "CTX_A1"])
        self.assertEqual(len(res), 2)
        self.assertEqual(res["CTX_A1"].depth, 2)
        self.assertEqual(res["CTX_ROOT"].depth, 1)

    def test_resolve_many_preserves_order(self):
        """Certifica la deduplicación manteniendo estrictamente el orden de inserción original."""
        res = self.resolver.resolve_many(["CTX_ROOT", "CTX_A1", "CTX_ROOT"])
        self.assertEqual(list(res.keys()), ["CTX_ROOT", "CTX_A1"])

    def test_resolve_many_atomic_failure(self):
        with self.assertRaisesRegex(KeyError, "UNKNOWN_CONTEXT_IDS"):
            self.resolver.resolve_many(["CTX_A1", "CTX_GHOST", "CTX_PHANTOM"])