"""G3-B3/1: response contract and node recomposition for durable chunk plans.

Pure functions only: no provider, SQLite, daemon, or persistence side effects.
The input ChunkPlan MUST have been validated with ChunkPlan.build/from_json.
"""

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from core.ast.models import ChunkMember, TranslationTaskType
from core.chunking.manifest_contract import ChunkPlan

_SCHEMA_VERSION = 1
_MAX_RESPONSE_BYTES = 4 * 1024 * 1024
_ENVELOPE_FIELDS = frozenset({
    "schema_version", "document_id", "ast_hash", "manifest_sha256", "chunk_id", "members",
})
_MEMBER_FIELDS = frozenset({"node_id", "segment_index", "source_sha256", "translated_text"})


@dataclass(frozen=True, slots=True)
class MemberTranslation:
    node_id: str
    segment_index: int
    translated_text: str


@dataclass(frozen=True, slots=True)
class ChunkTranslation:
    chunk_id: str
    members: tuple[MemberTranslation, ...]


@dataclass(frozen=True, slots=True)
class NodeMaterialization:
    document_id: str
    ast_hash: str
    node_id: str
    text: str
    text_sha256: str
    chunk_ids: tuple[str, ...]


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"G3_B3_DUPLICATE_JSON_KEY: {key}")
        obj[key] = value
    return obj


def _reject_constant(value: str) -> None:
    raise ValueError(f"G3_B3_INVALID_JSON_CONSTANT: {value}")


def _hash_text(value: str) -> str:
    try:
        return sha256(value.encode("utf-8")).hexdigest()
    except UnicodeError as exc:
        raise ValueError("G3_B3_INVALID_UNICODE") from exc


def _index_chunks(plan: ChunkPlan) -> dict[str, Any]:
    units = {u.chunk_id: u for u in plan.units}
    if len(units) != len(plan.units):
        raise ValueError("G3_B3_INVALID_PLAN_DUPLICATE_CHUNKS")
    return units


def parse_chunk_response(plan: ChunkPlan, chunk_id: str, raw_json: str) -> ChunkTranslation:
    """Accept one exact result per expected member, independently of response order.

    A PRESERVE unit must bypass the provider entirely. No raw-text splitting,
    implicit missing-member fallback, or untyped coercion is performed.
    """
    units = _index_chunks(plan)
    unit = units.get(chunk_id)
    if unit is None:
        raise ValueError(f"G3_B3_UNKNOWN_CHUNK: {chunk_id}")
    if unit.chunk_type == TranslationTaskType.PRESERVE:
        raise ValueError(f"G3_B3_PRESERVE_RESPONSE_FORBIDDEN: {chunk_id}")
    if unit.chunk_type not in (TranslationTaskType.TRANSLATE, TranslationTaskType.PARTIAL):
        raise ValueError(f"G3_B3_UNKNOWN_TASK_TYPE: {chunk_id}")
    if type(raw_json) is not str:
        raise ValueError("G3_B3_RESPONSE_MUST_BE_JSON_TEXT")
    try:
        if len(raw_json.encode("utf-8")) > _MAX_RESPONSE_BYTES:
            raise ValueError("G3_B3_RESPONSE_TOO_LARGE")
    except UnicodeError as exc:
        raise ValueError("G3_B3_INVALID_UNICODE") from exc
    try:
        envelope = json.loads(
            raw_json, object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (TypeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("G3_B3_INVALID_RESPONSE_JSON") from exc
    if type(envelope) is not dict or envelope.keys() != _ENVELOPE_FIELDS:
        raise ValueError("G3_B3_INVALID_RESPONSE_ENVELOPE")
    if type(envelope["schema_version"]) is not int or envelope["schema_version"] != _SCHEMA_VERSION:
        raise ValueError("G3_B3_UNSUPPORTED_RESPONSE_SCHEMA")
    if (envelope["document_id"] != plan.document_id
            or envelope["ast_hash"] != plan.ast_hash
            or envelope["manifest_sha256"] != plan.digest
            or envelope["chunk_id"] != chunk_id):
        raise ValueError("G3_B3_RESPONSE_BINDING_MISMATCH")
    raw_members = envelope["members"]
    if type(raw_members) is not list or len(raw_members) != len(unit.members):
        raise ValueError("G3_B3_MEMBER_COVERAGE_MISMATCH")
    expected = {(m.node_id, m.segment_index): m for m in unit.members}
    if len(expected) != len(unit.members):
        raise ValueError("G3_B3_INVALID_PLAN_DUPLICATE_MEMBERS")
    seen: dict[tuple[str, int], str] = {}
    for item in raw_members:
        if type(item) is not dict or item.keys() != _MEMBER_FIELDS:
            raise ValueError("G3_B3_INVALID_MEMBER_ENVELOPE")
        node_id, segment_index = item["node_id"], item["segment_index"]
        source_sha256, translated_text = item["source_sha256"], item["translated_text"]
        if (type(node_id) is not str or not node_id or type(segment_index) is not int
                or type(source_sha256) is not str or type(translated_text) is not str):
            raise ValueError("G3_B3_INVALID_MEMBER_TYPES")
        key = (node_id, segment_index)
        if key in seen:
            raise ValueError(f"G3_B3_DUPLICATE_MEMBER: {node_id}:{segment_index}")
        member = expected.get(key)
        if member is None:
            raise ValueError(f"G3_B3_UNEXPECTED_MEMBER: {node_id}:{segment_index}")
        if source_sha256 != _hash_text(member.source_text):
            raise ValueError(f"G3_B3_SOURCE_HASH_MISMATCH: {node_id}:{segment_index}")
        if not translated_text.strip():
            raise ValueError(f"G3_B3_EMPTY_TRANSLATION: {node_id}:{segment_index}")
        if translated_text != translated_text.strip():
            raise ValueError(f"G3_B3_TRANSLATION_BOUNDARY_WHITESPACE: {node_id}:{segment_index}")
        _hash_text(translated_text)
        seen[key] = translated_text
    if seen.keys() != expected.keys():
        raise ValueError("G3_B3_MEMBER_COVERAGE_MISMATCH")
    return ChunkTranslation(
        chunk_id=chunk_id,
        members=tuple(MemberTranslation(m.node_id, m.segment_index, seen[(m.node_id, m.segment_index)])
                      for m in unit.members),
    )


def _preserve_source_boundaries(member: ChunkMember, translation: str) -> str:
    """Keep source boundary whitespace; never invent delimiters between fragments."""
    original = member.source_text
    if not original.strip():
        raise ValueError(f"G3_B3_WHITESPACE_ONLY_SOURCE: {member.node_id}")
    leading_len = len(original) - len(original.lstrip())
    trailing_len = len(original) - len(original.rstrip())
    leading = original[:leading_len]
    trailing = original[len(original) - trailing_len:] if trailing_len else ""
    return leading + translation + trailing


def materialize_node_results(
    plan: ChunkPlan, raw_responses: Mapping[str, str],
) -> tuple[NodeMaterialization, ...]:
    """All-or-nothing pure recomposition, in AST order, for a validated plan.

    Does not write the materialized plane. Callers must persist these outputs
    with their own transaction/fencing protocol after this function succeeds.
    """
    if not isinstance(raw_responses, Mapping):
        raise ValueError("G3_B3_RESPONSES_NOT_MAPPING")
    _index_chunks(plan)
    required = {u.chunk_id for u in plan.units if u.chunk_type != TranslationTaskType.PRESERVE}
    if set(raw_responses) != required:
        raise ValueError("G3_B3_CHUNK_RESPONSE_COVERAGE_MISMATCH")
    segments: dict[str, list[str]] = {}
    chunks_per_node: dict[str, list[str]] = {}
    order: list[str] = []
    for unit in plan.units:
        translated: dict[tuple[str, int], str] = {}
        if unit.chunk_type != TranslationTaskType.PRESERVE:
            result = parse_chunk_response(plan, unit.chunk_id, raw_responses[unit.chunk_id])
            translated = {(m.node_id, m.segment_index): m.translated_text for m in result.members}
        for member in unit.members:
            if member.node_id not in segments:
                segments[member.node_id] = []
                chunks_per_node[member.node_id] = []
                order.append(member.node_id)
            if not chunks_per_node[member.node_id] or chunks_per_node[member.node_id][-1] != unit.chunk_id:
                chunks_per_node[member.node_id].append(unit.chunk_id)
            if unit.chunk_type == TranslationTaskType.PRESERVE:
                part = member.source_text
            else:
                part = _preserve_source_boundaries(
                    member, translated[(member.node_id, member.segment_index)],
                )
            segments[member.node_id].append(part)
    return tuple(
        NodeMaterialization(
            document_id=plan.document_id,
            ast_hash=plan.ast_hash,
            node_id=node_id,
            text="".join(segments[node_id]),
            text_sha256=_hash_text("".join(segments[node_id])),
            chunk_ids=tuple(chunks_per_node[node_id]),
        )
        for node_id in order
    )
