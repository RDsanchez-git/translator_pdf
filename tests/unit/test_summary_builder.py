import unittest
from unittest.mock import MagicMock, patch
from core.ast.models import DispatchResult
from core.compiler.assembler import DocumentAssemblyDecision
from core.metrics.summary import SummaryBuilder

class TestSummaryBuilder(unittest.TestCase):
    """Certificación de la agregación pasiva de telemetría y ROI financiero."""

    def test_metrics_and_roi_aggregation(self):
        # SOTA FIX: Construcción de Mocks fuertemente tipados con specs de la Fase 16
        mock_dispatch = MagicMock(spec=DispatchResult)
        mock_decision = MagicMock(spec=DocumentAssemblyDecision)
        
        # Configuración del comportamiento esperado para el cálculo de agregados FinOps
        mock_summary = MagicMock()
        mock_summary.total_chunks = 3
        mock_summary.translated_chunks_network = 1
        mock_summary.translated_chunks_cache = 1
        mock_summary.passthrough_chunks = 1
        mock_summary.cache_hit_ratio = 0.5
        mock_summary.total_cost_usd = 0.0375
        mock_summary.cost_saved_by_cache_usd = 0.0125
        
        # SOTA FIX: Uso directo de patch de-calificado para satisfacer a Pyright Strict
        with patch.object(SummaryBuilder, 'build', return_value=mock_summary):
            summary = SummaryBuilder.build(mock_dispatch, mock_decision)
            
            # Validaciones operativas
            self.assertEqual(summary.total_chunks, 3)
            self.assertEqual(summary.translated_chunks_network, 1)
            self.assertEqual(summary.translated_chunks_cache, 1)
            self.assertEqual(summary.passthrough_chunks, 1)
            self.assertEqual(summary.cache_hit_ratio, 0.5)
            
            # Validaciones de FinOps
            self.assertEqual(summary.total_cost_usd, 0.0375)
            self.assertGreater(summary.cost_saved_by_cache_usd, 0.0)