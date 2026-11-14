"""W08-2a: canonical, immutable context snapshot contract (pure domain code).

This proves *internal* snapshot integrity, not producer provenance or persistence.
The caller must bind the snapshot to a verified ChunkPlan before inference.
No legacy GLOBAL_ROOT fallback, network, SQLite or implicit breadcrumb coercion.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Mapping, Sequence, cast


_SCHEMA_VERSION = 1
_CONTEXT_ID_PATTERN = re.compile(r"CTX_[0-9A-F]{12}")


def _canonical(value: dict[str, object]) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"W08_CONTEXT_DUPLICATE_JSON_KEY: {key}")
        result[key] = value
    return result


def _required_nonempty(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"W08_CONTEXT_MISSING_IDENTITY: {name}")


@dataclass(frozen=True, slots=True)
class ContextBreadcrumbV1:
    """One hierarchical segment, preserving level and title exactly."""

    level: int
    title: str

    def __post_init__(self) -> None:
        if type(self.level) is not int or self.level < 0:
            raise ValueError("W08_CONTEXT_INVALID_LEVEL")
        _required_nonempty("title", self.title)


@dataclass(frozen=True, slots=True)
class ContextSnapshotV1:
    """Generation-bound semantic context; not an authorization token.

    A producer must persist and verify this snapshot under the same
    (document_id, ast_hash, context_id) as its ChunkPlan before any LLM I/O.
    """

    document_id: str
    ast_hash: str
    context_id: str
    breadcrumbs: tuple[ContextBreadcrumbV1, ...]

    def __post_init__(self) -> None:
        _required_nonempty("document_id", self.document_id)
        _required_nonempty("ast_hash", self.ast_hash)
        if self.context_id == "GLOBAL_ROOT":
            raise ValueError("W08_UNRESOLVED_GLOBAL_ROOT")
        if not isinstance(self.context_id, str) or not _CONTEXT_ID_PATTERN.fullmatch(
            self.context_id
        ):
            raise ValueError("W08_CONTEXT_INVALID_ID")
        if (
            not isinstance(self.breadcrumbs, tuple)
            or not self.breadcrumbs
            or any(not isinstance(item, ContextBreadcrumbV1) for item in self.breadcrumbs)
        ):
            raise ValueError("W08_CONTEXT_INVALID_BREADCRUMBS")
        if self.breadcrumbs[0].level == 0:
            if self.breadcrumbs != (
                ContextBreadcrumbV1(level=0, title="[ROOT_DOCUMENT_CONTEXT]"),
            ):
                raise ValueError("W08_CONTEXT_INVALID_ROOT")
        elif any(item.level == 0 for item in self.breadcrumbs):
            raise ValueError("W08_CONTEXT_ROOT_IN_HIERARCHY")

    @classmethod
    def from_enricher(
        cls, *, document_id: str, ast_hash: str, context_id: str,
        breadcrumbs: Sequence[Mapping[str, object]],
    ) -> ContextSnapshotV1:
        """Accept the actual HierarchicalContextEnricher shape, without str(dict)."""
        frames: list[ContextBreadcrumbV1] = []
        for raw in breadcrumbs:
            if set(raw) != {"level", "title"}:
                raise ValueError("W08_CONTEXT_INVALID_FRAME_FIELDS")
            level = raw["level"]
            title = raw["title"]
            if type(level) is not int or not isinstance(title, str):
                raise ValueError("W08_CONTEXT_INVALID_FRAME_TYPES")
            frames.append(ContextBreadcrumbV1(level=level, title=title))
        return cls(
            document_id=document_id, ast_hash=ast_hash,
            context_id=context_id, breadcrumbs=tuple(frames),
        )

    def _body(self) -> dict[str, object]:
        return {
            "schema_version": _SCHEMA_VERSION,
            "document_id": self.document_id,
            "ast_hash": self.ast_hash,
            "context_id": self.context_id,
            "breadcrumbs": [
                {"level": item.level, "title": item.title} for item in self.breadcrumbs
            ],
        }

    @property
    def snapshot_sha256(self) -> str:
        return sha256(_canonical(self._body())).hexdigest()

    def to_json(self) -> str:
        return _canonical({
            **self._body(), "snapshot_sha256": self.snapshot_sha256,
        }).decode("utf-8")

    @classmethod
    def from_json(cls, payload: str) -> ContextSnapshotV1:
        raw_value: object = json.loads(
            payload, object_pairs_hook=_reject_duplicate_keys,
        )
        if not isinstance(raw_value, dict) or any(
            not isinstance(k, str) for k in raw_value
        ):
            raise ValueError("W08_CONTEXT_INVALID_ENVELOPE")
        value = cast(dict[str, object], raw_value)
        if set(value) != {
            "schema_version", "document_id", "ast_hash", "context_id",
            "breadcrumbs", "snapshot_sha256",
        } or type(value["schema_version"]) is not int or value["schema_version"] != 1:
            raise ValueError("W08_CONTEXT_INVALID_ENVELOPE")
        raw_frames = value["breadcrumbs"]
        if not isinstance(raw_frames, list):
            raise ValueError("W08_CONTEXT_INVALID_BREADCRUMBS")
        frames: list[Mapping[str, object]] = []
        for raw in raw_frames:
            if not isinstance(raw, dict) or any(
                not isinstance(k, str) for k in raw
            ):
                raise ValueError("W08_CONTEXT_INVALID_FRAME_FIELDS")
            frames.append(cast(dict[str, object], raw))
        document_id = value["document_id"]
        ast_hash = value["ast_hash"]
        context_id = value["context_id"]
        if not all(isinstance(v, str) for v in (document_id, ast_hash, context_id)):
            raise ValueError("W08_CONTEXT_INVALID_ENVELOPE")
        result = cls.from_enricher(
            document_id=cast(str, document_id),
            ast_hash=cast(str, ast_hash),
            context_id=cast(str, context_id),
            breadcrumbs=frames,
        )
        if value["snapshot_sha256"] != result.snapshot_sha256:
            raise ValueError("W08_CONTEXT_SNAPSHOT_HASH_MISMATCH")
        return result
