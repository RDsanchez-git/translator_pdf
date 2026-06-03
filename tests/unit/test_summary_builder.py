import unittest
from core.ast.models import TranslatedUnit, ReconstructedDocument
from core.metrics.summary import SummaryBuilder

class TestSummaryBuilder(unittest.TestCase):
    """Certificación de la agregación pasiva de telemetría y ROI financiero."""

    def test_metrics_and_roi_aggregation(self):
        # Corrección: 11 argumentos posicionales exactos mapeados al DTO de producción
        units = [
            # 1. Network Flash (Costo: $0.0375)
            TranslatedUnit(1, "chk_1", "translate", (1,1), "Traducido A", "h1", "gemini-2.5-flash", "v1", 100_000, 100_000, 100.0),
            # 2. Passthrough
            TranslatedUnit(2, "chk_2", "passthrough", (2,2), "Preservado B", "h2", "bypass_passthrough", "v1", 0, 0, 10.0),
            # 3. Cache Hit (400 chars ~ 100 tokens eludidos)
            TranslatedUnit(3, "chk_3", "translate", (3,3), "X" * 400, "h3", "cache_hit:gemini-2.5-flash", "v1", 0, 0, 5.0)
        ]
        
        doc = ReconstructedDocument("Traducido A\n\nPreservado B\n\n" + "X" * 400, 3, 2, 1, 100_000, 100_000)
        
        summary = SummaryBuilder.build(units, doc)
        
        # Validaciones operativas
        self.assertEqual(summary.total_chunks, 3)
        self.assertEqual(summary.translated_chunks_network, 1)
        self.assertEqual(summary.translated_chunks_cache, 1)
        self.assertEqual(summary.passthrough_chunks, 1)
        self.assertEqual(summary.cache_hit_ratio, 0.5)
        
        # Validaciones de FinOps
        self.assertEqual(summary.total_cost_usd, 0.0375)
        self.assertGreater(summary.cost_saved_by_cache_usd, 0.0)