"""W08-2b: derive and verify plan context from the *same* generation AST.

Pure validation only. This does not connect context into SyncProviderBridge or
authorize cache reuse. A missing/mixed context must stop before provider I/O.
"""
from __future__ import annotations

from typing import Any, Sequence, cast

from core.ast.enums import ContentNodeType
from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode, TranslationTaskType
from core.chunking.manifest_contract import ChunkPlan
from core.context.snapshot_contract import ContextSnapshotV1
from core.normalization.enrichers.context_enricher import HierarchicalContextEnricher


def derive_verified_plan_contexts(
    plan: ChunkPlan, ast: Sequence[ASTNode],
) -> dict[str, ContextSnapshotV1]:
    """Rebuild expected context from AST, not the untrusted plan's identifiers.

    Recomputing the enricher is *verification*, not a replacement for the
    separately governed OCR producer. Only inference-bearing units require
    context; PRESERVE does not authorize LLM I/O.
    """
    if not ast or compute_ast_hash(ast) != plan.ast_hash:
        raise ValueError("W08_CONTEXT_AST_GENERATION_MISMATCH")
    validated = ChunkPlan.build(plan.document_id, plan.ast_hash, ast, plan.units)
    if validated.digest != plan.digest:
        raise ValueError("W08_CONTEXT_PLAN_DRIFT")

    enriched, registry, _, _ = HierarchicalContextEnricher().enrich_document(list(ast))
    if (
        registry.get("schema_version") != "1.0.1"
        or registry.get("algorithm") != "blake2b_ephemeral_runtime_v1"
    ):
        raise ValueError("W08_CONTEXT_UNSUPPORTED_PRODUCER")

    source_value: Any = registry.get("mappings")
    if not isinstance(source_value, dict):
        raise ValueError("W08_CONTEXT_PRODUCER_MAPPING_MISSING")
    mappings = cast(dict[str, list[dict[str, object]]], source_value)

    # The enhancer does not annotate heading nodes. They are expected to be
    # PRESERVE; translating a heading without a valid context is not allowed.
    node_contexts: dict[str, str] = {}
    for original, annotated in zip(ast, enriched, strict=True):
        if original.node_type == ContentNodeType.HEADING:
            continue
        context_id: object = annotated.control_plane.get("context_id")
        if not isinstance(context_id, str) or context_id not in mappings:
            raise ValueError("W08_CONTEXT_UNVERIFIABLE_SOURCE")
        original_id = original.control_plane.get("context_id")
        if original_id is not None and original_id != context_id:
            raise ValueError("W08_CONTEXT_AST_ANNOTATION_DRIFT")
        node_contexts[original.node_id] = context_id

    snapshots: dict[str, ContextSnapshotV1] = {}
    for unit in validated.units:
        if unit.chunk_type == TranslationTaskType.PRESERVE:
            continue
        if unit.chunk_type not in (TranslationTaskType.TRANSLATE, TranslationTaskType.PARTIAL):
            raise ValueError("W08_CONTEXT_UNSUPPORTED_INFERENCE_UNIT")
        member_contexts: set[str] = set()
        for member in unit.members:
            expected_id = node_contexts.get(member.node_id)
            if expected_id is None:
                raise ValueError("W08_CONTEXT_UNRESOLVED_MEMBER")
            member_contexts.add(expected_id)
        if len(member_contexts) != 1:
            raise ValueError("W08_CONTEXT_MIXED_INFERENCE_UNIT")
        expected_id = next(iter(member_contexts))
        if unit.context_id != expected_id:
            raise ValueError("W08_CONTEXT_PLAN_ID_MISMATCH")

        frames = mappings[expected_id]
        snapshot = ContextSnapshotV1.from_enricher(
            document_id=plan.document_id,
            ast_hash=plan.ast_hash,
            context_id=expected_id,
            breadcrumbs=frames,
        )
        if unit.context_depth != len(snapshot.breadcrumbs):
            raise ValueError("W08_CONTEXT_PLAN_DEPTH_MISMATCH")

        old = snapshots.get(expected_id)
        if old is not None and old.snapshot_sha256 != snapshot.snapshot_sha256:
            raise ValueError("W08_CONTEXT_SNAPSHOT_CONFLICT")
        snapshots[expected_id] = snapshot
    return snapshots
