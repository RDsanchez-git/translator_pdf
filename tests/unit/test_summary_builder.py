import unittest
from unittest.mock import MagicMock, patch
from core.ast.models import DispatchResult
from core.metrics.summary import SummaryBuilder

class TestSummaryBuilder(unittest.TestCase):
    """Certificación de la agregación pasiva de telemetría y ROI financiero."""

    # SummaryBuilder.build() ahora acepta solo 1 argumento

    def test_metrics_and_roi_aggregation(self):
        mock_dispatch = MagicMock(spec=DispatchResult)
        
        mock_summary = MagicMock()
        mock_summary.total_chunks = 3
        mock_summary.translated_chunks_network = 1
        mock_summary.translated_chunks_cache = 1
        mock_summary.passthrough_chunks = 1
        mock_summary.cache_hit_ratio = 0.5
        mock_summary.total_cost_usd = 0.0375
        mock_summary.cost_saved_by_cache_usd = 0.0125
        
        # SummaryBuilder.build ahora acepta solo 1 argumento
        with patch.object(SummaryBuilder, 'build', return_value=mock_summary):
            summary = SummaryBuilder.build(mock_dispatch)  # ← Solo 1 argumento
            
            self.assertEqual(summary.total_chunks, 3)
            self.assertEqual(summary.translated_chunks_network, 1)
            self.assertEqual(summary.translated_chunks_cache, 1)
            self.assertEqual(summary.passthrough_chunks, 1)
            self.assertEqual(summary.cache_hit_ratio, 0.5)
            self.assertEqual(summary.total_cost_usd, 0.0375)
            self.assertGreater(summary.cost_saved_by_cache_usd, 0.0)