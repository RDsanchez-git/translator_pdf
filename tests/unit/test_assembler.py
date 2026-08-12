# Este test necesita una reescritura completa porque DocumentAssembler.assemble()
# ahora acepta AssemblyExecutionContext en lugar de job_id + dispatch_result

import unittest
from unittest.mock import MagicMock
from core.compiler.assembler import DocumentAssembler, AssemblyStatus
from core.compiler.assembly_context import AssemblyExecutionContext
from core.ast.models import ASTNode
from core.execution.ports import ProjectionRecord
from core.ast.enums import ContentNodeType

class TestDocumentAssembler(unittest.TestCase):
    """SOTA: Certificación del motor de ensamblaje (Fase 16.10)."""

    def setUp(self):
        self.mock_repo = MagicMock()
        self.assembler = DocumentAssembler(repository=self.mock_repo, separator="")

    def _create_mock_context(self, node_count: int = 2, missing_count: int = 0) -> AssemblyExecutionContext:
        """Crea un contexto de ensamblado mock."""
        from core.ast.models import ParagraphPayload
        
        nodes = tuple(
            ASTNode(
                node_id=f"node_{i}",
                sequence_id=i,
                node_type=ContentNodeType.PARAGRAPH,  # ← Enum, no string
                payload=ParagraphPayload(content=f"Contenido del nodo {i}")
            )
            for i in range(1, node_count + 1)
        )
        
        projections = tuple(
            ProjectionRecord(
                node_id=f"node_{i}",
                normalized_response=f"Contenido traducido del fragmento {i}",
                projection_version=1
            )
            for i in range(1, node_count + 1 - missing_count)
        )
        
        return AssemblyExecutionContext(
            document_id="doc_test",
            ast_hash="hash_test",
            ast_nodes=nodes,
            projections=projections,
            projection_version=1
        )

    def test_successful_assembly(self):
        """Certifica la correcta evaluación del ensamblador ante contextos completos."""
        context = self._create_mock_context(node_count=2, missing_count=0)
        decision = self.assembler.assemble(context)
        
        self.assertIsNotNone(decision)
        self.assertEqual(decision.status, AssemblyStatus.SUCCESS)
        self.assertEqual(len(decision.missing_node_ids), 0)

    def test_degraded_assembly_with_missing_projections(self):
        """Certifica el ensamblado degradado cuando faltan proyecciones."""
        context = self._create_mock_context(node_count=3, missing_count=1)
        
        # Configurar política para permitir fallback
        from core.compiler.assembler import AssemblyPolicy
        self.assembler.policy = AssemblyPolicy(tolerance_ratio=0.5, allow_fallback=True)
        
        decision = self.assembler.assemble(context)
        
        self.assertIsNotNone(decision)
        self.assertEqual(decision.status, AssemblyStatus.DEGRADED)
        self.assertEqual(len(decision.missing_node_ids), 1)

    def test_rejected_assembly_beyond_tolerance(self):
        """Certifica el rechazo cuando faltan demasiadas proyecciones."""
        context = self._create_mock_context(node_count=3, missing_count=2)
        
        # Configurar política estricta
        from core.compiler.assembler import AssemblyPolicy
        self.assembler.policy = AssemblyPolicy(tolerance_ratio=0.1, allow_fallback=False)
        
        decision = self.assembler.assemble(context)
        
        self.assertIsNotNone(decision)
        self.assertEqual(decision.status, AssemblyStatus.REJECTED)
        self.assertIsNotNone(decision.rejection_reason)