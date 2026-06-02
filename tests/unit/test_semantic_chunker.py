import logging
import unittest
from core.ast.models import ASTNode, ContentNodeType, StructuralNodeType, FastWordEstimator
from core.ast.hashing import SemanticChunker, ChunkPolicy

logger = logging.getLogger(__name__)

class TestSemanticChunkerZeroLoss(unittest.TestCase):
    """Suite de certificación SOTA para el motor de empaquetado semántico."""

    def setUp(self):
        self.estimator = FastWordEstimator()
        self.policy = ChunkPolicy(
            max_tokens=300,
            sliding_window_tokens=50,
            prompt_overhead_tokens=20
        )
        self.chunker = SemanticChunker(estimator=self.estimator, policy=self.policy)

    def test_zero_loss_reconstruction(self):
        """10B.2.8: Verifica la conservación estricta de bytes y secuencias topológicas."""
        mock_ast = [
            ASTNode(node_id="n1", sequence_id=1, type=StructuralNodeType.SECTION, content="1. Ground Truth"),
            ASTNode(node_id="n2", sequence_id=2, type=ContentNodeType.PARAGRAPH, content="Alpha text paragraph content."),
            ASTNode(node_id="n3", sequence_id=3, type=ContentNodeType.PARAGRAPH, content="Beta text paragraph content for testing."),
            ASTNode(node_id="n4", sequence_id=4, type=ContentNodeType.TABLE, content="|col1|col2|\n|---|---|"),
            ASTNode(node_id="n5", sequence_id=5, type=ContentNodeType.PARAGRAPH, content="Gamma text post protected element.")
        ]

        units = self.chunker.chunk_document(mock_ast)

        # 1. Conservación Topológica (Conteo de nodos inyectados vs extraídos)
        self.assertEqual(sum(u.node_count for u in units), len(mock_ast))

        # 2. Conservación Secuencial (Detección de huecos / gaps)
        reconstructed_seqs = []
        for u in units:
            reconstructed_seqs.extend(range(u.source_sequence_range[0], u.source_sequence_range[1] + 1))
        self.assertEqual(reconstructed_seqs, list(range(1, 6)), "Fallo: Hueco topológico detectado.")

        # 3. Conservación de Contenido (Normalización estricta por líneas)
        def normalize(s: str) -> str:
            return "\n".join(line.strip() for line in (s or "").splitlines() if line.strip())
        
        original_text = normalize("\n".join([n.content for n in mock_ast if n.content]))
        reconstructed_text = normalize("\n".join([u.target_payload for u in units if u.chunk_type in ("translate", "passthrough")]))
        
        self.assertEqual(original_text, reconstructed_text, "Fuga de datos: Alteración detectada en la concatenación.")
        
    def test_deterministic_purity(self):
        """10B.2.10: Certifica que ejecuciones sucesivas en el mismo proceso producen hashes idénticos."""
        mock_ast = [
            ASTNode(node_id="n1", sequence_id=1, type=ContentNodeType.PARAGRAPH, content="Deterministic Node")
        ]
        units_a = self.chunker.chunk_document(mock_ast)
        units_b = self.chunker.chunk_document(mock_ast)
        self.assertEqual(units_a, units_b, "Violación de idempotencia: El chunker retiene estado residual.")

    def test_sliding_window_token_inclusion(self):
        """10B.2.6: Certifica la inyección del Sliding Window."""
        mock_ast = [
            ASTNode(node_id="p1", sequence_id=1, type=ContentNodeType.PARAGRAPH, content="Context Node Header."),
            # Forzar desbordamiento de la ventana de 25 tokens inyectando una cadena densa
            ASTNode(node_id="p2", sequence_id=2, type=ContentNodeType.PARAGRAPH, content="Trigger Node Flush " * 30)
        ]
        micro_policy = ChunkPolicy(max_tokens=30, sliding_window_tokens=15, prompt_overhead_tokens=5)
        chunker = SemanticChunker(estimator=self.estimator, policy=micro_policy)
        units = chunker.chunk_document(mock_ast)
        
        self.assertEqual(len(units), 2)
        self.assertEqual(units[1].reference_context, "Context Node Header.")