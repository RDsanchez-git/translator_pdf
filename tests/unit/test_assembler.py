import unittest
from core.ast.models import TranslatedUnit
from core.compiler.assembler import DocumentAssembler
from core.execution.exceptions import IncompleteDocumentError

class TestDocumentAssembler(unittest.TestCase):
    """SOTA: Certificación del motor de ensamblaje (Fase 10D)."""

    def setUp(self):
        self.assembler = DocumentAssembler(separator="")

    def _mock_unit(self, index: int, chunk_type: str, payload: str, tokens: int = 10) -> TranslatedUnit:
        return TranslatedUnit(
            chunk_index=index,
            chunk_id=f"chunk_{index}",
            chunk_type=chunk_type,
            source_sequence_range=(index, index),
            translated_payload=payload,
            payload_sha256="hash",
            model_name="test",
            prompt_version="v1",
            input_tokens=tokens,
            output_tokens=tokens + 2,
            latency_ms=1.0
        )

    def test_successful_assembly_and_token_telemetry(self):
        """10D.3: Certifica el ensamblaje correcto y el procesamiento de métricas agregadas."""
        units = [
            self._mock_unit(1, "translate", "Hola ", tokens=10),
            self._mock_unit(2, "passthrough", "Mundo", tokens=5)
        ]
        
        doc = self.assembler.assemble(units)
        
        self.assertEqual(doc.content, "Hola Mundo")
        self.assertEqual(doc.total_chunks, 2)
        self.assertEqual(doc.total_input_tokens, 15)  # 10 + 5
        self.assertEqual(doc.total_output_tokens, 19) # 12 + 7

    def test_missing_chunk_raises_incomplete_error(self):
        """10D.2: Certifica el lanzamiento exacto de IncompleteDocumentError ante huecos."""
        units = [
            self._mock_unit(1, "translate", "A"),
            self._mock_unit(3, "translate", "C")
        ]
        
        with self.assertRaises(IncompleteDocumentError) as context:
            self.assembler.assemble(units)
        self.assertEqual(context.exception.expected, 2)

    def test_duplicate_chunk_raises_value_error(self):
        """10D.2: Ajuste 2: Certifica la interceptación específica de duplicaciones indexadas."""
        units = [
            self._mock_unit(1, "translate", "A"),
            self._mock_unit(2, "translate", "B"),
            self._mock_unit(2, "translate", "B_copy")
        ]
        
        with self.assertRaises(ValueError) as context:
            self.assembler.assemble(units)
        self.assertEqual(str(context.exception), "Duplicate chunk_index detected")