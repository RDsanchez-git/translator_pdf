import logging
import unittest
from core.ast.models import ASTNode, ContentNodeType, StructuralNodeType, FastWordEstimator, TranslationTaskType
from core.ast.hashing import build_semantic_chunks_as_units, ChunkPolicy

logger = logging.getLogger(__name__)

class TestSemanticChunkerZeroLoss(unittest.TestCase):
    """Suite de certificación SOTA para el motor de empaquetado semántico (Fase 13)."""

    def setUp(self):
        self.estimator = FastWordEstimator()
        # SOTA: La política se alinea con el nuevo TokenBudgetChunker sin sliding window
        self.policy = ChunkPolicy(
            max_tokens=300,
            prompt_overhead_tokens=20
        )

    def _create_node(self, node_id: str, seq: int, n_type, content: str, ctx_id: str = "CTX_1", path: tuple = ("Root",)):
        """Factory method para inyectar el control_plane requerido por ContextAwareSemanticGrouper."""
        return ASTNode(
            node_id=node_id,
            sequence_id=seq,
            type=n_type,
            content=content,
            control_plane={"context_id": ctx_id, "structural_path": path}
        )

    def test_zero_loss_reconstruction(self):
        """10B.2.8: Verifica la conservación estricta de bytes y secuencias topológicas."""
        mock_ast = [
            self._create_node("n1", 1, StructuralNodeType.SECTION, "1. Ground Truth"),
            self._create_node("n2", 2, ContentNodeType.PARAGRAPH, "Alpha text paragraph content."),
            self._create_node("n3", 3, ContentNodeType.PARAGRAPH, "Beta text paragraph content for testing."),
            self._create_node("n4", 4, ContentNodeType.TABLE, "|col1|col2|\n|---|---|"),
            self._create_node("n5", 5, ContentNodeType.PARAGRAPH, "Gamma text post protected element.")
        ]

        # SOTA: Desempaquetado de la tupla estructural de la Fase 13
        units, report = build_semantic_chunks_as_units(mock_ast, self.estimator)

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
        reconstructed_text = normalize("\n".join([
            u.target_payload for u in units 
            if u.chunk_type in (TranslationTaskType.TRANSLATE, TranslationTaskType.PRESERVE, TranslationTaskType.PARTIAL)
        ]))
        
        self.assertEqual(original_text, reconstructed_text, "Fuga de datos: Alteración detectada en la concatenación.")
        
    def test_deterministic_purity(self):
        """10B.2.10: Certifica que ejecuciones sucesivas en el mismo proceso producen hashes idénticos."""
        mock_ast = [
            self._create_node("n1", 1, ContentNodeType.PARAGRAPH, "Deterministic Node")
        ]
        units_a, _ = build_semantic_chunks_as_units(mock_ast, self.estimator)
        units_b, _ = build_semantic_chunks_as_units(mock_ast, self.estimator)
        self.assertEqual(units_a, units_b, "Violación de idempotencia: El chunker retiene estado residual.")

    def test_context_aware_hard_boundary(self):
        """13.00: Certifica la partición topológica estricta ante cambios de dominio (Reemplaza al test de Sliding Window)."""
        mock_ast = [
            self._create_node("p1", 1, ContentNodeType.PARAGRAPH, "Context A - Node 1", ctx_id="CTX_A", path=("A",)),
            self._create_node("p2", 2, ContentNodeType.PARAGRAPH, "Context A - Node 2", ctx_id="CTX_A", path=("A",)),
            # Este nodo forzará un Hard Boundary inmediato aunque sobre presupuesto de tokens
            self._create_node("p3", 3, ContentNodeType.PARAGRAPH, "Context B - Node 1", ctx_id="CTX_B", path=("B",))
        ]
        
        units, report = build_semantic_chunks_as_units(mock_ast, self.estimator)
        
        self.assertEqual(len(units), 2, "Fallo de aislamiento: El Grouper mezcló contextos lógicos.")
        self.assertEqual(units[0].context_id, "CTX_A")
        self.assertEqual(units[0].node_count, 2)
        self.assertEqual(units[1].context_id, "CTX_B")
        self.assertEqual(units[1].node_count, 1)