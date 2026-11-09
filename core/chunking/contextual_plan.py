"""W08-2c: OCR composition of contextual AST, semantic units and G3 plan.

Preserves the exact semantic AST hash. Only inference-bearing groups carry
resolved CTX identities; headings are isolated PRESERVE units with an explicit
non-inference marker, never the implicit GLOBAL_ROOT fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, cast

from core.ast.enums import ContentNodeType
from core.ast.hashing import compute_ast_hash
from core.ast.grouper import SemanticGroup
from core.ast.models import ASTNode, ChunkingReport
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from core.normalization.enrichers.context_enricher import HierarchicalContextEnricher
from core.validation.protocols import TokenEstimatorProtocol


_PRESERVE_HEADING = "PRESERVE_HEADING_NO_INFERENCE"


@dataclass(frozen=True, slots=True)
class ContextualPlanPreparation:
    ast: tuple[ASTNode, ...]
    plan: ChunkPlan
    report: ChunkingReport


def prepare_contextual_plan(
    *, document_id: str, raw_ast: Sequence[ASTNode], estimator: TokenEstimatorProtocol,
) -> ContextualPlanPreparation:
    """Enrich once and group inference work by the verified contextual boundary."""
    if not raw_ast:
        raise ValueError("W08_OCR_EMPTY_AST")
    original_hash = compute_ast_hash(raw_ast)
    annotated, registry, _, _ = HierarchicalContextEnricher().enrich_document(list(raw_ast))
    if compute_ast_hash(annotated) != original_hash:
        raise ValueError("W08_OCR_SEMANTIC_AST_DRIFT")
    if registry.get("schema_version") != "1.0.1":
        raise ValueError("W08_OCR_CONTEXT_PRODUCER_VERSION")
    mapping_value = registry.get("mappings")
    if not isinstance(mapping_value, dict):
        raise ValueError("W08_OCR_CONTEXT_MAPPING_MISSING")
    mappings = cast(dict[str, list[dict[str, object]]], mapping_value)

    groups: list[SemanticGroup] = []
    current: SemanticGroup | None = None
    for node in annotated:
        if node.node_type == ContentNodeType.HEADING:
            if current is not None:
                groups.append(current)
                current = None
            groups.append(SemanticGroup(
                structural_path=(), context_id=_PRESERVE_HEADING, nodes=[node],
            ))
            continue

        context_id = node.control_plane.get("context_id")
        if not isinstance(context_id, str) or context_id not in mappings:
            raise ValueError("W08_OCR_CONTEXT_UNRESOLVED_NODE")
        frames = mappings[context_id]
        if not frames:
            raise ValueError("W08_OCR_CONTEXT_MISSING_BREADCRUMBS")
        structure = tuple(
            f"H{frame['level']}:{frame['title']}" for frame in frames
        )
        # Check the full identity, not merely the displayable structure:
        # homonymous headings can produce different CTX IDs.
        if current is None or current.context_id != context_id:
            if current is not None:
                groups.append(current)
            current = SemanticGroup(
                structural_path=structure, context_id=context_id, nodes=[node],
            )
        else:
            current.nodes.append(node)

    if current is not None:
        groups.append(current)

    chunker = TokenBudgetChunker(estimator, ChunkPolicy())
    chunker.report.total_groups = len(groups)
    units = []
    next_index = 1
    for group in groups:
        produced = chunker.chunk_group(group, start_index=next_index)
        units.extend(produced)
        next_index += len(produced)
        chunker.report.context_switches += 1
    if units:
        chunker.report.average_chunk_tokens = int(
            sum(unit.estimated_tokens for unit in units) / len(units)
        )
    plan = ChunkPlan.build(document_id, original_hash, annotated, units)
    return ContextualPlanPreparation(ast=tuple(annotated), plan=plan, report=chunker.report)
