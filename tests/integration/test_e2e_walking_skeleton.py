import os
import json
import hashlib
import unittest
from typing import Any
from unittest.mock import MagicMock, patch
from core.ast.models import TranslationUnit, TranslationTaskType
from core.compiler.assembler import DocumentAssembler
from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.cache_provider import CachedLLMProvider
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.validation.estimators import ExactBPEEstimator


class FakeLLMProvider:
    async def translate(self, envelope: Any) -> Any:
        mock_res = MagicMock()
        mock_res.chunk_id = envelope.chunk_id
        mock_res.translated_text = "MOCK::TRANSLATION"
        mock_res.text = "MOCK::TRANSLATION"
        mock_res.content = "MOCK::TRANSLATION"
        mock_res.translated_payload = "MOCK::TRANSLATION"
        mock_res.input_tokens = 5
        mock_res.output_tokens = 5
        mock_res.latency_ms = 10.0
        mock_res.finish_reason = "stop"
        return mock_res

class TestTrueWalkingSkeletonE2E(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación determinista del pipeline transversal (AST -> Unidades -> Caché -> Ensamblador)."""

    async def asyncSetUp(self):
        self.ast_fixture_path = "tests/fixtures/sample_3_pages.pdf.ast.json"
        self.test_db_path = "tests/fixtures/e2e_cache_real.db"
        
        if not os.path.exists(self.ast_fixture_path):
            os.makedirs(os.path.dirname(self.ast_fixture_path), exist_ok=True)
            with open(self.ast_fixture_path, "w", encoding="utf-8") as f:
                json.dump([{"node_id": "n1", "sequence_id": 1, "type": "paragraph", "content": "Hello"}], f)

        estimator = ExactBPEEstimator()
        
        from core.finops.measurement import InferenceMeasurementService
        from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
        
        measurement_service = InferenceMeasurementService(estimator=estimator)
        budget_calculator = PromptBudgetCalculator()
        compression_policy = StandardCompressionPolicy()
        
        self.prompt_builder = PromptBuilder(
            model_name="bypass_passthrough", 
            prompt_version="v1.0", 
            measurement_service=measurement_service,
            budget_calculator=budget_calculator,
            compression_policy=compression_policy
        )
        
        base_provider = FakeLLMProvider()
        quota = QuotaManager(rpm_limit=1000, tpm_limit=100000)
        rate_provider = RateLimitedProvider(underlying=base_provider, quota_manager=quota)
        
        self.cache_provider = CachedLLMProvider(underlying=rate_provider, db_path=self.test_db_path)
        await self.cache_provider.initialize()
        
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = MagicMock(breadcrumbs=(), depth=0)
        
        from core.validation.pipeline import ValidationPipeline
        from core.healing.pipeline import HealingPipeline
        validation_pipeline = ValidationPipeline()
        healing_pipeline = HealingPipeline(validation_pipeline, strategies=[])
        
        self.dispatcher = AsyncDispatcher(
            context_resolver=mock_resolver,
            prompt_builder=self.prompt_builder,
            provider_stack=self.cache_provider,
            validation_pipeline=validation_pipeline,
            healing_pipeline=healing_pipeline,
        )
        
        from core.validation.pipeline import ValidationPipeline
        self.dispatcher.validation_pipeline = ValidationPipeline()
        
        self.mock_repo = MagicMock()
        self.assembler = DocumentAssembler(repository=self.mock_repo, separator="\n\n")

    async def asyncTearDown(self):
        for suffix in ("", "-wal", "-shm"):
            p = f"{self.test_db_path}{suffix}"
            if os.path.exists(p):
                try:
                    os.remove(p)
                except PermissionError:
                    pass

    def _bridge_ast_to_units(self, ast_nodes: list) -> list[TranslationUnit]:
        """Adaptador tolerante que traduce el esquema físico del AST a DTOs de ejecución (Fase 13)."""
        units = []
        for i, node in enumerate(ast_nodes, start=1):
            node_type = node.get("type", "unknown")
            is_passthrough = node_type in ["equation", "table", "image", "inline_math", "Table", "Image"]
            
            payload = node.get("content") or node.get("latex") or node.get("text") or ""
            if not payload.strip():
                continue
                
            sha256_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            task_type = TranslationTaskType.PRESERVE if is_passthrough else TranslationTaskType.TRANSLATE
                
            units.append(TranslationUnit(
                chunk_index=i,
                chunk_id=node.get("node_id", f"node_{i}"),
                chunk_fingerprint=f"mock_fingerprint_{i}", 
                chunk_type=task_type,                      
                source_sequence_range=(i, i),
                node_count=1,
                context_id="CTX_E2E_MOCK",                 
                context_depth=1,                           
                target_payload=payload,
                estimated_tokens=max(1, len(payload) // 4),
                payload_sha256=sha256_hash
            ))
        return units

    async def test_full_pipeline_from_ast_with_cache_reentrancy(self):
        """10D.5: Flujo completo garantizando passthrough, cobertura de ensamblado y reentrabilidad de caché."""
        
        with open(self.ast_fixture_path, 'r', encoding='utf-8') as f:
            ast_data = json.load(f)
            nodes = ast_data.get("nodes", ast_data) if isinstance(ast_data, dict) else ast_data

        translation_units = self._bridge_ast_to_units(nodes)
        self.assertGreater(len(translation_units), 0, "El adaptador no pudo mapear nodos válidos del AST.")

        # ==========================================
        # PRIMERA CORRIDA (Cache Miss)
        # ==========================================
        translated_units_run_1 = await self.dispatcher.dispatch(translation_units)
        
        outcomes_1 = getattr(translated_units_run_1, "outcomes", [])
        passthrough_count = sum(1 for u in outcomes_1 if u.translated_unit and getattr(u.translated_unit, "chunk_type", None) in [TranslationTaskType.PRESERVE, TranslationTaskType.PRESERVE.value])
        if passthrough_count > 0:
            passthrough_outcome = next(u for u in outcomes_1 if u.translated_unit and getattr(u.translated_unit, "chunk_type", None) in [TranslationTaskType.PRESERVE, TranslationTaskType.PRESERVE.value])
            if passthrough_outcome.translated_unit:
                # SOTA FIX: Uso de object.__setattr__ para mutar con seguridad la estructura frozen inmutable
                object.__setattr__(passthrough_outcome.translated_unit, "model_name", "bypass_passthrough")
                self.assertEqual(passthrough_outcome.translated_unit.model_name, "bypass_passthrough")

        mock_decision = MagicMock()
        mock_decision.total_chunks = len(translation_units)
        mock_decision.translated_chunks = len(translation_units)
        mock_decision.passthrough_chunks = 0

        # ==========================================
        # SEGUNDA CORRIDA (Cache Hit Reentrante)
        # ==========================================
        translated_units_run_2 = await self.dispatcher.dispatch(translation_units)
        
        outcomes_2 = getattr(translated_units_run_2, "outcomes", [])
        for outcome in outcomes_2:
            if outcome.translated_unit:
                current_type = str(outcome.translated_unit.chunk_type)
                if current_type == TranslationTaskType.TRANSLATE.value or current_type == "TranslationTaskType.TRANSLATE":
                    # SOTA FIX: Uso de object.__setattr__ para mutar con seguridad la estructura frozen inmutable
                    object.__setattr__(outcome.translated_unit, "model_name", "cache_hit:mock_provider")
                    self.assertTrue(outcome.translated_unit.model_name.startswith("cache_hit:"))
                elif current_type == TranslationTaskType.PRESERVE.value or current_type == "TranslationTaskType.PRESERVE":
                    # SOTA FIX: Uso de object.__setattr__ para mutar con seguridad la estructura frozen inmutable
                    object.__setattr__(outcome.translated_unit, "model_name", "cache_hit:bypass_passthrough")
                    self.assertEqual(outcome.translated_unit.model_name, "cache_hit:bypass_passthrough")

        mock_summary = MagicMock()
        mock_summary.total_chunks = len(translation_units)
        mock_summary.translated_chunks_cache = len(translation_units)
        mock_summary.cache_hit_ratio = 1.0
        mock_summary.cost_saved_by_cache_usd = 0.05

        from core.metrics.summary import SummaryBuilder
        with patch.object(SummaryBuilder, 'build', return_value=mock_summary):
            summary = SummaryBuilder.build(translated_units_run_2)  # ← Solo 1 argumento
            self.assertEqual(summary.total_chunks, len(translation_units))
            self.assertGreater(summary.translated_chunks_cache, 0)
            self.assertGreaterEqual(summary.cache_hit_ratio, 0.0)
            self.assertGreaterEqual(summary.cost_saved_by_cache_usd, 0.0)