"""W08-1: offline characterization of context and cache identity boundaries.

All tests are synthetic: no Docker, HTTP, paid inference or canonical PDFs.
STRICT XFAIL witnesses are *open defects*, not a certification or a PASS.
Do not mutate FROZEN oracles or production schemas in this review.
"""
import asyncio
from hashlib import sha256
import json
from types import SimpleNamespace

import pytest

from apps.llm_workers.cache_provider import CachedLLMProvider
from apps.llm_workers.sync_bridge import SyncProviderBridge
from core.ast.models import ChunkMember, TranslationTaskType, TranslationUnit
from core.chunking.manifest_contract import ChunkPlan
from core.context.context_registry import ContextRegistry
from core.context.dynamic_resolver import DynamicContextResolver
from core.prompting.canonicalizer import PromptCanonicalizer
from core.prompting.models import (
    PromptConstraints, PromptContext, PromptIntent, PromptPayload, PromptSchema,
)


def _prompt_schema(breadcrumbs: tuple[str, ...]) -> PromptSchema:
    return PromptSchema(
        intent=PromptIntent.TRANSLATE,
        context=PromptContext(
            chunk_index=1, depth=len(breadcrumbs),
            breadcrumbs=list(breadcrumbs), is_pruned=False,
        ),
        constraints=PromptConstraints(),
        payload=PromptPayload(content="Alpha."),
    )


def test_w08_effective_prompt_hash_is_stable_and_context_sensitive() -> None:
    first = _prompt_schema(("Introduction",))
    same = _prompt_schema(("Introduction",))
    changed = _prompt_schema(("Methods",))
    assert PromptCanonicalizer.compute_hash(first) == PromptCanonicalizer.compute_hash(same)
    assert PromptCanonicalizer.compute_hash(first) != PromptCanonicalizer.compute_hash(changed)


def test_w08_missing_context_registry_mapping_fails_explicitly() -> None:
    registry = ContextRegistry()
    registry.update({"CTX_KNOWN": ["Introduction"]})
    resolver = DynamicContextResolver(registry)
    assert resolver.resolve("CTX_KNOWN").breadcrumbs == ("Introduction",)
    with pytest.raises(KeyError, match="UNKNOWN_CONTEXT_ID"):
        resolver.resolve("GLOBAL_ROOT")


def _g3_plan() -> tuple[ChunkPlan, TranslationUnit]:
    source = "Alpha."
    member = ChunkMember(
        node_id="node_a", sequence_id=1, segment_index=0, segment_count=1,
        source_text=source, node_type="paragraph", strategy="translate",
    )
    unit = TranslationUnit(
        chunk_index=1, chunk_id="chunk_w08", chunk_fingerprint="fp_w08",
        chunk_type=TranslationTaskType.TRANSLATE, source_sequence_range=(1, 1),
        node_count=1, context_id="CTX_KNOWN", context_depth=1,
        target_payload=source, estimated_tokens=2,
        payload_sha256=sha256(source.encode("utf-8")).hexdigest(), members=(member,),
    )
    return ChunkPlan("doc_w08", "ast_w08", (unit,)), unit


class _CaptureBuilder:
    model_name = "offline"
    prompt_version = "w08-test"

    def __init__(self) -> None:
        self.contexts = []

    def build(self, unit, resolved_context, target_lang_expansion=1.2):
        self.contexts.append(resolved_context)
        return SimpleNamespace(
            status="success", envelope=SimpleNamespace(chunk_id=unit.chunk_id),
        )


class _CaptureProvider:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls = 0

    async def translate(self, envelope):
        self.calls += 1
        return SimpleNamespace(chunk_id=envelope.chunk_id, content=self.content)


@pytest.mark.xfail(
    strict=True,
    reason="W08 OPEN: execute_chunk substitutes empty breadcrumbs for non-root context",
)
def test_w08_g3_uses_real_hierarchical_context_before_provider() -> None:
    plan, unit = _g3_plan()
    response = json.dumps({
        "schema_version": 1, "document_id": plan.document_id,
        "ast_hash": plan.ast_hash, "manifest_sha256": plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [{
            "node_id": "node_a", "segment_index": 0,
            "source_sha256": sha256(b"Alpha.").hexdigest(),
            "translated_text": "Alfa.",
        }],
    })
    builder = _CaptureBuilder()
    provider = _CaptureProvider(response)
    bridge = SyncProviderBridge(provider, builder)
    try:
        bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()
    assert provider.calls == 1
    assert builder.contexts[0].context_id == "CTX_KNOWN"
    assert builder.contexts[0].breadcrumbs == ("Introduction",)


class _CountingProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def translate(self, envelope):
        self.calls += 1
        return SimpleNamespace(
            chunk_id=envelope.chunk_id, content=f"provider-call-{self.calls}",
            input_tokens=1, output_tokens=1, latency_ms=1.0,
            finish_reason="stop",
        )


def _envelope(*, prompt_hash: str, model: str = "model-a",
              version: str = "v1", chunk: str = "chunk-a"):
    return SimpleNamespace(
        prompt_hash=prompt_hash, model_name=model,
        prompt_version=version, chunk_id=chunk,
    )


def test_w08_cache_exact_same_identity_reuses_completed_result(tmp_path) -> None:
    async def scenario() -> None:
        provider = _CountingProvider()
        cache = CachedLLMProvider(provider, str(tmp_path / "cache.db"))
        await cache.initialize()
        env = _envelope(prompt_hash="same-hash")
        first = await cache.translate(env)
        replay = await cache.translate(env)
        assert first.content == replay.content == "provider-call-1"
        assert provider.calls == 1
        assert replay.finish_reason == "cache_hit"
    asyncio.run(scenario())


@pytest.mark.xfail(
    strict=True,
    reason="W08 OPEN: cache read validates prompt_hash only, not model/version",
)
def test_w08_cache_rejects_same_hash_with_different_model(tmp_path) -> None:
    async def scenario() -> None:
        provider = _CountingProvider()
        cache = CachedLLMProvider(provider, str(tmp_path / "cache.db"))
        await cache.initialize()
        first = await cache.translate(_envelope(prompt_hash="shared", model="model-a"))
        second = await cache.translate(_envelope(prompt_hash="shared", model="model-b"))
        assert second.content != first.content, "W08_CROSS_MODEL_CACHE_REUSE"
    asyncio.run(scenario())


@pytest.mark.xfail(
    strict=True,
    reason="W08 OPEN: cache hit silently rebinds stored content to a different chunk",
)
def test_w08_cache_rejects_same_hash_with_different_chunk(tmp_path) -> None:
    async def scenario() -> None:
        provider = _CountingProvider()
        cache = CachedLLMProvider(provider, str(tmp_path / "cache.db"))
        await cache.initialize()
        first = await cache.translate(_envelope(prompt_hash="shared", chunk="chunk-a"))
        second = await cache.translate(_envelope(prompt_hash="shared", chunk="chunk-b"))
        assert second.content != first.content, "W08_CROSS_CHUNK_CACHE_REUSE"
    asyncio.run(scenario())


@pytest.mark.xfail(
    strict=True,
    reason="W08 OPEN: cache I/O failures are silently downgraded to misses",
)
def test_w08_cache_read_failure_does_not_start_uncertain_external_effect(tmp_path) -> None:
    async def scenario() -> None:
        provider = _CountingProvider()
        cache = CachedLLMProvider(provider, str(tmp_path / "cache.db"))
        await cache.initialize()
        cache._db_path = str(tmp_path / "missing" / "cache.db")
        with pytest.raises(OSError):
            await cache.translate(_envelope(prompt_hash="new"))
        assert provider.calls == 0
    asyncio.run(scenario())
