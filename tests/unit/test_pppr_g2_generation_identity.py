"""Wave 2.2: exact EN→ES generation identity, distinct from W06 attempts."""

from dataclasses import replace
from hashlib import sha256

import pytest

from core.prompting.inference_identity import (
    InferenceReuseIdentityV1, PPPRGenerationIdentityV1,
)


def digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def generation(**changes: str) -> PPPRGenerationIdentityV1:
    base = dict(
        document_id="doc", ast_hash=digest("AST semantic V2"),
        manifest_sha256=digest("manifest"), chunk_id="chunk",
        context_snapshot_sha256=digest("context"),
        prompt_hash=digest("effective prompt bytes"),
        provider_id="groq", model_name="llama3-70b-8192",
        prompt_version="v1.0", target_language="es",
        effective_config_sha256=digest("temperature+dialect+route"),
    )
    contract = changes.pop("output_contract_version", "G3_CHUNK_RESPONSE_V1")
    source = changes.pop("source_language", "en")
    base.update(changes)
    return PPPRGenerationIdentityV1(
        reuse=InferenceReuseIdentityV1(**base),
        source_language=source, output_contract_version=contract,
    )


@pytest.mark.unit
def test_generation_is_deterministic_and_separate_from_attempt() -> None:
    a = generation()
    b = generation()
    assert a.generation_sha256 == b.generation_sha256
    assert len(a.generation_sha256) == 64
    assert "execution_id" not in a.reuse._body()
    assert "lease_owner" not in a.reuse._body()


@pytest.mark.unit
@pytest.mark.parametrize("field,value", [
    ("document_id", "other"), ("ast_hash", digest("other AST")),
    ("manifest_sha256", digest("other plan")),
    ("chunk_id", "other chunk"),
    ("context_snapshot_sha256", digest("new context")),
    ("prompt_hash", digest("new prompt")),
    ("provider_id", "gemini"), ("model_name", "other model"),
    ("prompt_version", "v2.0"),
    ("effective_config_sha256", digest("temperature changed")),
    ("output_contract_version", "G3_CHUNK_RESPONSE_V2"),
])
def test_generation_changes_with_every_scoped_dimension(field: str, value: str) -> None:
    assert generation().generation_sha256 != generation(**{field: value}).generation_sha256


@pytest.mark.unit
@pytest.mark.parametrize("field,value", [
    ("source_language", "fr"),
    ("target_language", "fr"),
])
def test_other_language_pairs_cannot_claim_en_es_product_generation(field: str, value: str) -> None:
    with pytest.raises(ValueError, match="PPPR_G2_UNSUPPORTED_PRODUCT_LANGUAGE_PAIR"):
        generation(**{field: value})


@pytest.mark.unit
def test_output_generation_not_equal_to_w08_candidate_reuse_key() -> None:
    item = generation()
    assert item.generation_sha256 != item.reuse.reuse_sha256
    assert item != replace(item, output_contract_version="G3_CHUNK_RESPONSE_V2")



@pytest.mark.unit
def test_generation_identity_reproducible_across_processes_and_hash_seeds() -> None:
    """F17BIS-16 §5.2 R7: independent processes produce the same generation key."""
    import os
    from pathlib import Path
    import subprocess
    import sys

    script = """
from hashlib import sha256
from core.prompting.inference_identity import InferenceReuseIdentityV1, PPPRGenerationIdentityV1
def digest(x):
    return sha256(x.encode("utf-8")).hexdigest()
reuse = InferenceReuseIdentityV1(
    document_id="document", ast_hash=digest("AST_V2"),
    manifest_sha256=digest("manifest"), chunk_id="chunk",
    context_snapshot_sha256=digest("context"), prompt_hash=digest("prompt"),
    provider_id="offline", model_name="offline-model", prompt_version="v1",
    target_language="es", effective_config_sha256=digest("effective-config"),
)
print(PPPRGenerationIdentityV1(
    reuse=reuse, source_language="en", output_contract_version="G3_CHUNK_RESPONSE_V1",
).generation_sha256)
"""
    root = Path(__file__).resolve().parents[2]
    values = []
    for seed in ("3", "107"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=root, env=env,
            capture_output=True, text=True, check=True, timeout=25,
        )
        values.append(result.stdout.strip())
    assert values[0] == values[1]
    assert len(values[0]) == 64
