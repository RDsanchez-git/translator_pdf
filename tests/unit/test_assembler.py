import unittest
from unittest.mock import MagicMock
from core.compiler.assembler import DocumentAssembler
from core.ast.models import DispatchResult, ChunkOutcome

class TestDocumentAssembler(unittest.TestCase):
    """SOTA: Certificación del motor de ensamblaje (Fase 16.10)."""

    def setUp(self):
        # SOTA FIX: Inyección del repositorio de integridad requerido por el constructor
        self.mock_repo = MagicMock()
        self.assembler = DocumentAssembler(repository=self.mock_repo, separator="")

    def _create_mock_outcome(self, index: int, success: bool = True) -> MagicMock:
        outcome = MagicMock(spec=ChunkOutcome)
        outcome.success = success
        outcome.chunk_index = index
        outcome.chunk_id = f"chunk_{index}"
        outcome.did_overflow = False
        return outcome

    def test_successful_assembly_and_token_telemetry(self):
        """Certifica la correcta evaluación del orquestador de ensamble ante lotes limpios."""
        mock_dispatch = MagicMock(spec=DispatchResult)
        outcomes = [
            self._create_mock_outcome(1, success=True),
            self._create_mock_outcome(2, success=True)
        ]
        mock_dispatch.outcomes = outcomes
        mock_dispatch.__iter__.return_value = outcomes

        decision = self.assembler.assemble(job_id="job_test", dispatch_result=mock_dispatch)
        self.assertIsNotNone(decision)

    def test_missing_chunk_raises_incomplete_error(self):
        """Certifica el disparo preventivo ante discontinuidades e índices ausentes en la secuencia."""
        mock_dispatch = MagicMock(spec=DispatchResult)
        outcomes = [
            self._create_mock_outcome(1, success=True),
            self._create_mock_outcome(3, success=True)
        ]
        mock_dispatch.outcomes = outcomes
        mock_dispatch.__iter__.return_value = outcomes
        
        with self.assertRaises(Exception):
            self.assembler.assemble(job_id="job_test", dispatch_result=mock_dispatch)

    def test_duplicate_chunk_raises_value_error(self):
        """Certifica la intercepción inmediata de colisiones e índices duplicados."""
        mock_dispatch = MagicMock(spec=DispatchResult)
        outcomes = [
            self._create_mock_outcome(1, success=True),
            self._create_mock_outcome(2, success=True),
            self._create_mock_outcome(2, success=True)
        ]
        mock_dispatch.outcomes = outcomes
        mock_dispatch.__iter__.return_value = outcomes
        
        with self.assertRaises(Exception):
            self.assembler.assemble(job_id="job_test", dispatch_result=mock_dispatch)