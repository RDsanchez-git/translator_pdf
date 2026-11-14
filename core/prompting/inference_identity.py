"""W08-2a: deterministic inference reuse identity, separate from W06 attempt authority.

This key is *only* a candidate cache/reuse identity. Neither a replay
authorization nor a claim that an external effect was NOT_STARTED.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

_SHA256 = re.compile(r"[0-9a-f]{64}")
_SCHEMA_VERSION = 1


def _nonempty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"W08_INFERENCE_MISSING_IDENTITY: {name}")


def _digest(name: str, value: str) -> None:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"W08_INFERENCE_INVALID_DIGEST: {name}")


@dataclass(frozen=True, slots=True)
class InferenceReuseIdentityV1:
    """All known output-affecting inputs plus exact G3 generation and chunk.

    `effective_config_sha256` must be calculated by the *composition root*
    over effective options (temperature, provider route, dialect, etc.).
    A placeholder or missing config is invalid: this pure DTO cannot prove
    that its caller captured the true options.

    W06 `execution_id` and leases must never form part of this reuse identity;
    they are separate, runtime-owned authorization facts.
    """

    document_id: str
    ast_hash: str
    manifest_sha256: str
    chunk_id: str
    context_snapshot_sha256: str
    prompt_hash: str
    provider_id: str
    model_name: str
    prompt_version: str
    target_language: str
    effective_config_sha256: str

    def __post_init__(self) -> None:
        for name in (
            "document_id", "ast_hash", "chunk_id", "provider_id",
            "model_name", "prompt_version", "target_language",
        ):
            _nonempty(name, getattr(self, name))
        for name in (
            "manifest_sha256", "context_snapshot_sha256",
            "prompt_hash", "effective_config_sha256",
        ):
            _digest(name, getattr(self, name))

    def _body(self) -> dict[str, str | int]:
        return {
            "schema_version": _SCHEMA_VERSION,
            "document_id": self.document_id,
            "ast_hash": self.ast_hash,
            "manifest_sha256": self.manifest_sha256,
            "chunk_id": self.chunk_id,
            "context_snapshot_sha256": self.context_snapshot_sha256,
            "prompt_hash": self.prompt_hash,
            "provider_id": self.provider_id,
            "model_name": self.model_name,
            "prompt_version": self.prompt_version,
            "target_language": self.target_language,
            "effective_config_sha256": self.effective_config_sha256,
        }

    @property
    def reuse_sha256(self) -> str:
        encoded = json.dumps(
            self._body(), sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")
        return sha256(encoded).hexdigest()
