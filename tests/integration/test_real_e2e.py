import os
import unittest
import uuid
from typing import List
from core.ast.models import ASTNode, TranslationUnit, FastWordEstimator, TranslationTaskType
from core.pipeline.job import TranslationJob, JobStatus
from apps.bootstrap.pipeline_factory import build_pipeline

# Importaciones de Infraestructura Real Productiva
from apps.llm_workers.gemini_client import GeminiClient
from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.workers import GeminiWorker
from apps.llm_workers.cache import SQLiteTranslationCache
from apps.llm_workers.dispatcher import AsyncDispatcher

class FinOpsControlledChunker:
    """SOTA: Chunker de control presupuestario para pruebas E2E. Absorbe el AST 
    real pero empaqueta un solo fragmento para mitigar costos de tokens.
    """
    def chunk(self, nodes: List[ASTNode]) -> List[TranslationUnit]:
        return [
            TranslationUnit(
                chunk_index=1,
                chunk_id="chk_e2e_pro_001",
                chunk_fingerprint="fp_e2e_pro_001",           # SOTA: Fase 13
                chunk_type=TranslationTaskType.TRANSLATE,     # SOTA: Fase 13 (Enum)
                source_sequence_range=(1, min(5, max(1, len(nodes)))),
                node_count=min(5, max(1, len(nodes))),
                context_id="CTX_E2E_PRO",                     # SOTA: Fase 13 (Puntero relacional)
                context_depth=1,                              # SOTA: Fase 13
                target_payload="This is a test of the real-time financial translation engine pipeline.",
                estimated_tokens=20,
                payload_sha256="85174c85174c85174c85174c85174c85174c85174c85174c85174c85174c8517"
            )
        ]

class TestRealE2EFinOps(unittest.IsolatedAsyncioTestCase):
    """Certificación de Extremo a Extremo con consumo de tokens de la API real de Google."""

    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.test_id = uuid.uuid4().hex
        self.test_db_path = f"tests/fixtures/e2e_cache_{self.test_id}.db"

        # 1. Validar precondición de red/API
        if not os.environ.get("GEMINI_API_KEY"):
            self.skipTest("GEMINI_API_KEY no detectada en las variables de entorno. Evitando fallo de red.")

        # 2. Inicialización del Grafo Físico Real de Producción
        client = GeminiClient()
        prompt_builder = PromptBuilder()
        estimator = FastWordEstimator()
        
        worker = GeminiWorker(client=client, prompt_builder=prompt_builder, estimator=estimator)
        cache = SQLiteTranslationCache(db_path=self.test_db_path)
        
        # Construcción del despachador concurrente real
        dispatcher = AsyncDispatcher(
            worker=worker,
            cache=cache,
            model_name=client.model_v,
            prompt_version=prompt_builder.PROMPT_VERSION
        )

        # 3. Cableado por Raíz de Composición parametrizada
        self.pipeline = build_pipeline(
            chunker=FinOpsControlledChunker(),
            dispatcher=dispatcher
        )

    def tearDown(self):
        # Limpieza asíncrona de archivos de base de datos volátiles de la prueba
        for suffix in ("", "-wal", "-shm"):
            p = f"{self.test_db_path}{suffix}"
            if os.path.exists(p):
                try:
                    os.remove(p)
                except PermissionError:
                    pass

    async def test_real_pipeline_execution_spends_and_audits_money(self):
        """Consume la API real de Gemini 2.5 Flash y verifica la integridad del reporte FinOps."""
        job = TranslationJob(job_id=f"job_e2e_{self.test_id}", source_path=self.pdf_real_path)
        
        # Despacho de ejecución real a través de los hilos del event loop
        result = await self.pipeline.execute(job)
        
        # 1. Verificación Estructural del Documento Ensamblado
        self.assertIsInstance(result.document.content, str)
        self.assertGreater(len(result.document.content.strip()), 0)
        self.assertEqual(job.status, JobStatus.COMPLETED)
        
        # 2. Corrección 4: Verificación Antifragilidad FinOps (Independiente del estado de la caché)
        self.assertIsNotNone(result.summary)
        self.assertIsInstance(result.summary.total_cost_usd, float)
        self.assertGreaterEqual(result.summary.total_cost_usd, 0.0)
        
        # 3. Validación de Invariantes de Consistencia de Tokens
        self.assertGreater(result.summary.total_input_tokens, 0)
        self.assertGreater(result.summary.total_output_tokens, 0)
        self.assertEqual(result.summary.total_chunks, 1)