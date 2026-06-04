import unittest
import os
from datetime import datetime
from typing import List
from core.ast.models import ASTNode, TranslationUnit, TranslatedUnit
from core.pipeline.job import TranslationJob, JobStatus, PipelineStep
from apps.bootstrap.pipeline_factory import build_pipeline

class FakeChunker:
    """Implementación de control estricta para cumplir con ChunkerProtocol."""
    def chunk(self, nodes: List[ASTNode]) -> List[TranslationUnit]:
        return [
            TranslationUnit(
                chunk_index=1,
                chunk_id="chk_mock_001",
                chunk_type="translate",
                source_sequence_range=(1, len(nodes)),
                node_count=len(nodes),
                reference_context="Contexto de control",
                target_payload="Payload extraído del AST real",
                estimated_tokens=150,
                payload_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            )
        ]

class FakeDispatcher:
    """Implementación asíncrona que emula el transporte de red sin llamadas externas."""
    async def dispatch(self, units: List[TranslationUnit]) -> List[TranslatedUnit]:
        return [
            TranslatedUnit(
                chunk_index=u.chunk_index,
                chunk_id=u.chunk_id,
                chunk_type=u.chunk_type,
                source_sequence_range=u.source_sequence_range,
                translated_payload="Texto traducido simulado",
                payload_sha256=u.payload_sha256,
                # SOTA Fix: Usar el nombre de modelo real esperado por el PricingEngine
                model_name="gemini-2.5-flash",
                prompt_version="v3_latex_optimized",
                input_tokens=120,
                output_tokens=140,
                latency_ms=45.2
            ) for u in units
        ]

class TestPipelineOrchestration(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación del cableado del orquestador desde el binario (Fase 11B.3)."""

    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.pipeline = build_pipeline(
            chunker=FakeChunker(),
            dispatcher=FakeDispatcher()
        )

        if not os.path.exists(self.pdf_real_path):
            raise FileNotFoundError(f"Falta el binario de control: {self.pdf_real_path}")

    async def test_pipeline_executes_successfully_with_real_pdf_source(self):
        """Certifica que el pipeline orqueste la transformación física mutando el Job."""
        job = TranslationJob(job_id="job_orch_prod_001", source_path=self.pdf_real_path)
        
        self.assertEqual(job.status, JobStatus.PENDING)
        
        result = await self.pipeline.execute(job)
        
        # Validación de firmas y presencia volumétrica
        self.assertIsInstance(result.document.content, str)
        self.assertGreater(len(result.document.content.strip()), 0)
        
        # Validación de transiciones de la máquina de estados del Job
        self.assertEqual(job.status, JobStatus.COMPLETED)
        self.assertEqual(job.current_step, PipelineStep.FINISHED)
        self.assertIsNone(job.error_type)
        
        self.assertIsNotNone(job.audit_summary)
        self.assertEqual(result.summary, job.audit_summary)
        
        self.assertIsInstance(job.started_at, datetime)
        self.assertIsInstance(job.finished_at, datetime)

        