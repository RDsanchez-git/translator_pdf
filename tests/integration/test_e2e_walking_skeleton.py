"""Legacy R1 dispatcher/cache contract — not the supported OCR/G3/G5 PDF→PDF path.

Uses synthetic AST-like input, a local fake provider, and a temporary SQLite DB.
A cache hit is measured through the actual CachedLLMProvider, never assigned by
the test to an immutable TranslatedUnit.
"""
import hashlib
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from core.ast.models import TranslationUnit, TranslationTaskType
from core.context.context_resolver import ResolvedContext
from core.metrics.summary import SummaryBuilder
from core.prompting.inference_result import InferenceResult
from apps.llm_workers.prompt_builder import PromptBuilder, PromptEnvelope
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.cache_provider import CachedLLMProvider
from apps.llm_workers.dispatcher import AsyncDispatcher, NullEventPlane
from core.validation.estimators import ExactBPEEstimator
from core.validation.pipeline import ValidationPipeline
from core.healing.pipeline import HealingPipeline

TEST_DOCUMENT_ID = "test_legacy_cache_dispatch"
TEST_AST_HASH = "test_hash_legacy_cache"


class FakeLLMProvider:
    def __init__(self) -> None:
        self.translate_calls = 0

    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        self.translate_calls += 1
        return InferenceResult(
            chunk_id=envelope.chunk_id,
            content="MOCK::TRANSLATION",
            input_tokens=5,
            output_tokens=5,
            latency_ms=10.0,
            finish_reason="stop",
        )


class TestLegacyDispatcherCache(unittest.IsolatedAsyncioTestCase):
    """Two real legacy dispatches; no physical PDF, daemon, or provider network."""

    async def asyncSetUp(self) -> None:
        scratch = tempfile.TemporaryDirectory(prefix="tst-stab-legacy-cache-")
        self.addCleanup(scratch.cleanup)
        self.test_db_path = str(Path(scratch.name) / "cache.db")

        from core.finops.measurement import InferenceMeasurementService
        from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy

        estimator = ExactBPEEstimator()
        self.prompt_builder = PromptBuilder(
            model_name="bypass_passthrough",
            prompt_version="v1.0",
            measurement_service=InferenceMeasurementService(estimator=estimator),
            budget_calculator=PromptBudgetCalculator(),
            compression_policy=StandardCompressionPolicy(),
        )

        self.fake_provider = FakeLLMProvider()
        quota = QuotaManager(rpm_limit=1000, tpm_limit=100000)
        rate_provider = RateLimitedProvider(underlying=self.fake_provider, quota_manager=quota)
        self.cache_provider = CachedLLMProvider(
            underlying=rate_provider, db_path=self.test_db_path
        )
        await self.cache_provider.initialize()

        resolver = MagicMock()
        resolver.resolve_many.return_value = {
            "CTX_E2E_MOCK": ResolvedContext(context_id="CTX_E2E_MOCK", breadcrumbs=())
        }

        validation_pipeline = ValidationPipeline()
        healing_pipeline = HealingPipeline(validation_pipeline, strategies=[])
        self.dispatcher = AsyncDispatcher(
            context_resolver=resolver,
            prompt_builder=self.prompt_builder,
            provider_stack=self.cache_provider,
            validation_pipeline=validation_pipeline,
            healing_pipeline=healing_pipeline,
            event_plane=NullEventPlane(),
        )

    def _bridge_ast_to_units(self, ast_nodes: list[dict[str, Any]]) -> list[TranslationUnit]:
        """Map synthetic node records to legacy TranslationUnit DTOs, not canonical AST."""
        units: list[TranslationUnit] = []
        for i, node in enumerate(ast_nodes, start=1):
            node_type = node.get("type", "unknown")
            is_passthrough = node_type in [
                "equation", "table", "image", "inline_math", "Table", "Image"
            ]
            payload = node.get("content") or node.get("latex") or node.get("text") or ""
            if not payload.strip():
                continue
            units.append(TranslationUnit(
                chunk_index=i,
                chunk_id=str(node.get("node_id", f"node_{i}")),
                chunk_fingerprint=f"mock_fingerprint_{i}",
                chunk_type=TranslationTaskType.PRESERVE if is_passthrough else TranslationTaskType.TRANSLATE,
                source_sequence_range=(i, i),
                node_count=1,
                context_id="CTX_E2E_MOCK",
                context_depth=1,
                target_payload=str(payload),
                estimated_tokens=max(1, len(str(payload)) // 4),
                payload_sha256=hashlib.sha256(str(payload).encode("utf-8")).hexdigest(),
            ))
        return units

    async def test_legacy_cache_hit_observed_across_two_dispatches(self) -> None:
        # Input is explicit and deterministic; no self-created fixture on disk.
        units = self._bridge_ast_to_units([
            {"node_id": "n1", "sequence_id": 1, "type": "paragraph",
             "content": "Hello scientific world."},
        ])
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].chunk_type, TranslationTaskType.TRANSLATE)

        first = await self.dispatcher.dispatch(
            units, document_id=TEST_DOCUMENT_ID, ast_hash=TEST_AST_HASH
        )
        self.assertEqual(len(first.outcomes), 1)
        self.assertTrue(first.outcomes[0].is_success, first.outcomes[0].error_message)
        self.assertEqual(first.outcomes[0].translated_unit.translated_payload, "MOCK::TRANSLATION")
        self.assertEqual(self.fake_provider.translate_calls, 1)
        self.assertEqual(self.cache_provider.metrics["cache_misses"], 1)
        self.assertEqual(self.cache_provider.metrics["cache_writes"], 1)
        self.assertEqual(self.cache_provider.metrics["cache_hits"], 0)

        second = await self.dispatcher.dispatch(
            units, document_id=TEST_DOCUMENT_ID, ast_hash=TEST_AST_HASH
        )
        self.assertEqual(len(second.outcomes), 1)
        self.assertTrue(second.outcomes[0].is_success, second.outcomes[0].error_message)
        self.assertEqual(self.fake_provider.translate_calls, 1, "Cache hit must avoid a second fake provider call")
        self.assertEqual(self.cache_provider.metrics["cache_hits"], 1)
        self.assertEqual(self.cache_provider.metrics["cache_misses"], 1)

        translated = second.outcomes[0].translated_unit
        self.assertIsNotNone(translated)
        assert translated is not None
        self.assertEqual(translated.translated_payload, "MOCK::TRANSLATION")
        self.assertEqual(translated.model_name, "cache_hit:bypass_passthrough")

        # Actual SummaryBuilder, not a mocked summary assembled by this test.
        summary = SummaryBuilder.build(second)
        self.assertEqual(summary.total_chunks, 1)
        self.assertEqual(summary.translated_chunks_cache, 1)
        self.assertEqual(summary.translated_chunks_network, 0)
        self.assertEqual(summary.cache_hit_ratio, 1.0)
