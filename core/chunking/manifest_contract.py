"""Contrato puro de identidad N->1->N; sin E/S, proveedor ni estado global.

Un chunk es unidad de inferencia; un miembro identifica un nodo AST o fragmento.
Un resultado multimiembro no se proyecta sin validacion adicional de respuesta.
"""

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Sequence

from core.ast.models import ASTNode, ChunkMember, TranslationTaskType, TranslationUnit
from core.ast.enums import ContentNodeType, TranslationStrategy

_SCHEMA = 1


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError(f"G3_MANIFEST_DUPLICATE_JSON_KEY: {k}")
        obj[k] = v
    return obj


_PROTECTED_TYPES = frozenset({
    ContentNodeType.HEADING.value, ContentNodeType.DISPLAY_EQUATION.value,
    ContentNodeType.INLINE_EQUATION.value, ContentNodeType.CODE.value,
})
_PARTIAL_TYPES = frozenset({
    ContentNodeType.TABLE_SIMPLE.value, ContentNodeType.TABLE_COMPLEX.value,
    ContentNodeType.IMAGE.value,
})


def build_target_payload(members: Sequence[ChunkMember]) -> str:
    """Frontera estable: entre nodos diferentes se separa con dos LF;
    entre fragmentos del MISMO nodo no se altera el texto original.
    """
    if not members:
        raise ValueError("G3_EMPTY_CHUNK_MEMBERS")
    out = [members[0].source_text]
    for previous, member in zip(members, members[1:]):
        if previous.node_id != member.node_id:
            out.append("\n\n")
        out.append(member.source_text)
    return "".join(out)


def expected_task_type(member: ChunkMember) -> TranslationTaskType:
    """Taxonomia segura de política a partir de la identidad ya validada."""
    if member.strategy in (
        TranslationStrategy.PASSTHROUGH.value, TranslationStrategy.KEEP_ORIGINAL.value
    ) or member.node_type in _PROTECTED_TYPES:
        return TranslationTaskType.PRESERVE
    if member.node_type in _PARTIAL_TYPES:
        return TranslationTaskType.PARTIAL
    return TranslationTaskType.TRANSLATE


def validate_chunk_coverage(ast: Sequence[ASTNode], units: Sequence[TranslationUnit]) -> None:
    """Fail-closed: unicidad, orden, bytes originales y cobertura por segmento."""
    nodes: dict[str, ASTNode] = {}
    ordered_node_ids: list[str] = []
    for n in ast:
        if n.node_id in nodes:
            raise ValueError(f"G3_DUPLICATE_AST_NODE: {n.node_id}")
        nodes[n.node_id] = n
        if n.text_content and n.strategy != TranslationStrategy.OMIT:
            ordered_node_ids.append(n.node_id)

    expected_order = {node_id: i for i, node_id in enumerate(ordered_node_ids)}
    members_by_node: dict[str, list[ChunkMember]] = {key: [] for key in ordered_node_ids}
    seen_chunk_ids: set[str] = set()
    previous_position = (-1, -1)
    for unit in units:
        if unit.chunk_id in seen_chunk_ids:
            raise ValueError(f"G3_DUPLICATE_CHUNK: {unit.chunk_id}")
        seen_chunk_ids.add(unit.chunk_id)
        if not unit.members or unit.node_count != len(unit.members):
            raise ValueError(f"G3_MISSING_MEMBERS: {unit.chunk_id}")
        text = build_target_payload(unit.members)
        if text != unit.target_payload or sha256(text.encode("utf-8")).hexdigest() != unit.payload_sha256:
            raise ValueError(f"G3_INVALID_CHUNK_CONTENT: {unit.chunk_id}")
        if unit.source_sequence_range != (unit.members[0].sequence_id, unit.members[-1].sequence_id):
            raise ValueError(f"G3_INVALID_SEQUENCE_RANGE: {unit.chunk_id}")
        if unit.chunk_type != TranslationTaskType.TRANSLATE and len(unit.members) != 1:
            raise ValueError(f"G3_PROTECTED_NOT_ATOMIC: {unit.chunk_id}")
        for member in unit.members:
            node = nodes.get(member.node_id)
            if member.node_id not in members_by_node or node is None:
                raise ValueError(f"G3_UNKNOWN_OR_OMITTED_NODE: {member.node_id}")
            if member.sequence_id != node.sequence_id or member.node_type != node.node_type.value:
                raise ValueError(f"G3_WRONG_NODE_METADATA: {member.node_id}")
            if member.strategy != node.strategy.value:
                raise ValueError(f"G3_WRONG_STRATEGY: {member.node_id}")
            if unit.chunk_type != expected_task_type(member):
                raise ValueError(f"G3_TASK_POLICY_MISMATCH: {member.node_id}")
            if node.strategy == TranslationStrategy.DEFER:
                raise ValueError(f"G3_UNRESOLVED_STRATEGY: {member.node_id}")
            if node.strategy in (TranslationStrategy.PASSTHROUGH, TranslationStrategy.KEEP_ORIGINAL) and unit.chunk_type != TranslationTaskType.PRESERVE:
                raise ValueError(f"G3_PRESERVE_ROUTED_TO_LLM: {member.node_id}")
            if member.segment_count < 1 or not 0 <= member.segment_index < member.segment_count:
                raise ValueError(f"G3_INVALID_SEGMENT: {member.node_id}")
            current_position = (expected_order[member.node_id], member.segment_index)
            if current_position <= previous_position:
                raise ValueError(f"G3_OUT_OF_ORDER_OR_DUPLICATE: {member.node_id}:{member.segment_index}")
            previous_position = current_position
            members_by_node[member.node_id].append(member)

    for node_id, members in members_by_node.items():
        if not members:
            raise ValueError(f"G3_MISSING_NODE: {node_id}")
        expected_count = members[0].segment_count
        if len(members) != expected_count or [m.segment_index for m in members] != list(range(expected_count)):
            raise ValueError(f"G3_SEGMENT_COVERAGE_ERROR: {node_id}")
        if any(m.segment_count != expected_count for m in members):
            raise ValueError(f"G3_SEGMENT_COUNT_DRIFT: {node_id}")
        if "".join(m.source_text for m in members) != (nodes[node_id].text_content or ""):
            raise ValueError(f"G3_SOURCE_LOSS_OR_DUPLICATION: {node_id}")


@dataclass(frozen=True, slots=True)
class ChunkPlan:
    """Snapshot autocontenido de unidades y miembros, ligado a generacion AST."""

    document_id: str
    ast_hash: str
    units: tuple[TranslationUnit, ...]

    @classmethod
    def build(cls, document_id: str, ast_hash: str, ast: Sequence[ASTNode], units: Sequence[TranslationUnit]) -> "ChunkPlan":
        if not document_id or not ast_hash:
            raise ValueError("G3_MISSING_GENERATION")
        if not ast or not units:
            raise ValueError("G3_EMPTY_PLAN")
        validate_chunk_coverage(ast, units)
        return cls(document_id, ast_hash, tuple(units))

    def _body(self) -> dict[str, Any]:
        return {
            "schema_version": _SCHEMA,
            "document_id": self.document_id,
            "ast_hash": self.ast_hash,
            "units": [asdict(u) for u in self.units],
        }

    @property
    def digest(self) -> str:
        return sha256(_canonical(self._body())).hexdigest()

    def to_json(self) -> str:
        return _canonical({**self._body(), "manifest_sha256": self.digest}).decode("utf-8")

    @classmethod
    def from_json(cls, data: str, ast: Sequence[ASTNode], *, document_id: str, ast_hash: str) -> "ChunkPlan":
        obj = json.loads(data, object_pairs_hook=_reject_duplicate_keys)
        if not isinstance(obj, dict) or set(obj) != {"schema_version", "document_id", "ast_hash", "units", "manifest_sha256"}:
            raise ValueError("G3_INVALID_MANIFEST_ENVELOPE")
        if type(obj["schema_version"]) is not int or obj["schema_version"] != _SCHEMA:
            raise ValueError("G3_UNSUPPORTED_SCHEMA")
        if obj["document_id"] != document_id or obj["ast_hash"] != ast_hash:
            raise ValueError("G3_GENERATION_MISMATCH")
        actual_sha = obj.pop("manifest_sha256")
        if not isinstance(actual_sha, str) or sha256(_canonical(obj)).hexdigest() != actual_sha:
            raise ValueError("G3_MANIFEST_HASH_MISMATCH")
        from dataclasses import fields
        unit_keys = {f.name for f in fields(TranslationUnit)}
        member_keys = {f.name for f in fields(ChunkMember)}
        units: list[TranslationUnit] = []
        if not isinstance(obj["units"], list):
            raise ValueError("G3_INVALID_UNITS")
        for raw in obj["units"]:
            if not isinstance(raw, dict) or set(raw) != unit_keys or not isinstance(raw["members"], list):
                raise ValueError("G3_INVALID_UNIT_FIELDS")
            members = []
            for item in raw["members"]:
                if not isinstance(item, dict) or set(item) != member_keys:
                    raise ValueError("G3_INVALID_MEMBER_FIELDS")
                members.append(ChunkMember(**item))
            payload = dict(raw)
            payload["chunk_type"] = TranslationTaskType(payload["chunk_type"])
            payload["source_sequence_range"] = tuple(payload["source_sequence_range"])
            payload["members"] = tuple(members)
            units.append(TranslationUnit(**payload))
        return cls.build(obj["document_id"], obj["ast_hash"], ast, units)
