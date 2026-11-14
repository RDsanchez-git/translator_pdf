"""W08-2a: pure contract witnesses; no providers, filesystem, DB or network."""
from dataclasses import replace
from hashlib import sha256
import json

import pytest

from core.context.snapshot_contract import (
    ContextBreadcrumbV1,
    ContextSnapshotV1,
)
from core.prompting.inference_identity import InferenceReuseIdentityV1


def _hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _snapshot(
    *, context_id: str = "CTX_AABBCCDDEEFF", title: str = "Methods",
    ast_hash: str = "ast-a",
) -> ContextSnapshotV1:
    return ContextSnapshotV1.from_enricher(
        document_id="doc-a", ast_hash=ast_hash, context_id=context_id,
        breadcrumbs=[{"level": 1, "title": title}],
    )


@pytest.mark.unit
def test_w08_context_snapshot_round_trip_is_deterministic() -> None:
    first = _snapshot()
    other = _snapshot()
    assert first == other
    assert first.snapshot_sha256 == other.snapshot_sha256
    assert first.to_json() == other.to_json()
    assert ContextSnapshotV1.from_json(first.to_json()) == first


@pytest.mark.unit
def test_w08_context_snapshot_is_sensitive_to_structure_and_generation() -> None:
    base = _snapshot()
    assert base.snapshot_sha256 != _snapshot(title="Results").snapshot_sha256
    assert base.snapshot_sha256 != _snapshot(ast_hash="ast-b").snapshot_sha256
    assert base.snapshot_sha256 != _snapshot(context_id="CTX_001122334455").snapshot_sha256


@pytest.mark.unit
@pytest.mark.parametrize(
    ("frame", "error"),
    [
        ({"level": "1", "title": "Methods"}, "W08_CONTEXT_INVALID_FRAME_TYPES"),
        ({"level": 1, "title": ""}, "W08_CONTEXT_MISSING_IDENTITY"),
        ({"level": 1, "title": "Methods", "index": 1}, "W08_CONTEXT_INVALID_FRAME_FIELDS"),
        ({"level": True, "title": "Methods"}, "W08_CONTEXT_INVALID_FRAME_TYPES"),
    ],
)
def test_w08_context_snapshot_rejects_invalid_producer_frame(
    frame: dict[str, object], error: str,
) -> None:
    with pytest.raises(ValueError, match=error):
        ContextSnapshotV1.from_enricher(
            document_id="doc-a", ast_hash="ast-a",
            context_id="CTX_AABBCCDDEEFF", breadcrumbs=[frame],
        )


@pytest.mark.unit
def test_w08_context_root_is_explicit_and_not_missing_global_root() -> None:
    root = ContextSnapshotV1(
        document_id="doc-a", ast_hash="ast-a", context_id="CTX_001122334455",
        breadcrumbs=(ContextBreadcrumbV1(0, "[ROOT_DOCUMENT_CONTEXT]"),),
    )
    assert ContextSnapshotV1.from_json(root.to_json()) == root
    with pytest.raises(ValueError, match="W08_UNRESOLVED_GLOBAL_ROOT"):
        replace(root, context_id="GLOBAL_ROOT")
    with pytest.raises(ValueError, match="W08_CONTEXT_INVALID_ROOT"):
        replace(root, breadcrumbs=(ContextBreadcrumbV1(0, "invented-root"),))


@pytest.mark.unit
def test_w08_context_rejects_tampered_serialized_payload() -> None:
    original = _snapshot()
    value = json.loads(original.to_json())
    value["breadcrumbs"][0]["title"] = "Different"
    with pytest.raises(ValueError, match="W08_CONTEXT_SNAPSHOT_HASH_MISMATCH"):
        ContextSnapshotV1.from_json(json.dumps(value))
    with pytest.raises(ValueError, match="W08_CONTEXT_DUPLICATE_JSON_KEY"):
        ContextSnapshotV1.from_json('{"document_id":"x","document_id":"y"}')


def _identity(**changes: str) -> InferenceReuseIdentityV1:
    original = {
        "document_id": "doc-a",
        "ast_hash": "ast-a",
        "manifest_sha256": _hash("manifest-a"),
        "chunk_id": "chunk-a",
        "context_snapshot_sha256": _snapshot().snapshot_sha256,
        "prompt_hash": _hash("actual-prompt-schema"),
        "provider_id": "groq",
        "model_name": "model-a",
        "prompt_version": "v1",
        "target_language": "es",
        "effective_config_sha256": _hash("effective-options-a"),
    }
    original.update(changes)
    return InferenceReuseIdentityV1(**original)


@pytest.mark.unit
def test_w08_inference_reuse_identity_deterministic_and_attempt_independent() -> None:
    first = _identity()
    second = _identity()
    assert first.reuse_sha256 == second.reuse_sha256
    assert len(first.reuse_sha256) == 64
    assert "execution_id" not in first._body()
    assert "lease_owner" not in first._body()


@pytest.mark.unit
@pytest.mark.parametrize(
    ("field", "new_value"),
    [
        ("document_id", "doc-b"),
        ("ast_hash", "ast-b"),
        ("manifest_sha256", _hash("manifest-b")),
        ("chunk_id", "chunk-b"),
        ("context_snapshot_sha256", _hash("context-b")),
        ("prompt_hash", _hash("different-effective-schema")),
        ("provider_id", "gemini"),
        ("model_name", "model-b"),
        ("prompt_version", "v2"),
        ("target_language", "fr"),
        ("effective_config_sha256", _hash("changed-temperature")),
    ],
)
def test_w08_inference_reuse_identity_invalidates_every_dimension(
    field: str, new_value: str,
) -> None:
    old = _identity()
    assert old.reuse_sha256 != _identity(**{field: new_value}).reuse_sha256


@pytest.mark.unit
def test_w08_inference_identity_rejects_missing_or_untrusted_digest() -> None:
    with pytest.raises(ValueError, match="W08_INFERENCE_INVALID_DIGEST"):
        _identity(effective_config_sha256="")
    with pytest.raises(ValueError, match="W08_INFERENCE_INVALID_DIGEST"):
        _identity(prompt_hash="not-a-sha256")
    with pytest.raises(ValueError, match="W08_INFERENCE_MISSING_IDENTITY"):
        _identity(target_language="   ")
