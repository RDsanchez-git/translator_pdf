"""B02.2/G5: stage real PNG bytes in a Tectonic-private directory.

No Docker, LLM or Tectonic process is launched: subprocess.run is a stub.
"""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.compiler.tectonic_runner import HostTectonicRunner
from core.compiler.rendering.models import AssetReference
from core.compiler.rendering.image_assets import stage_image_assets


PNG = b"\x89PNG\r\n\x1a\n" + b"synthetic-png-payload"  # staging checks signature+SHA, not image decoder
DIGEST = sha256(PNG).hexdigest()
REL = "data/assets/" + DIGEST + ".png"


def _asset(tmp_path, content=PNG):
    root = tmp_path / "repo"
    folder = root / "data" / "assets"
    folder.mkdir(parents=True)
    (folder / (DIGEST + ".png")).write_bytes(content)
    return root, AssetReference(path=REL)


@pytest.mark.integration
def test_stage_copies_digest_verified_bytes_and_deduplicates(tmp_path):
    root, ref = _asset(tmp_path)
    execution = tmp_path / "private"
    execution.mkdir()
    stage_image_assets((ref, ref), source_root=root, execution_dir=execution)
    assert (execution / "assets" / (DIGEST + ".png")).read_bytes() == PNG


@pytest.mark.integration
def test_staging_detects_tampered_bytes(tmp_path):
    root, ref = _asset(tmp_path, PNG + b"tampered")
    execution = tmp_path / "private"
    execution.mkdir()
    with pytest.raises(ValueError, match="B02_G5_IMAGE_HASH_MISMATCH"):
        stage_image_assets((ref,), source_root=root, execution_dir=execution)


@pytest.mark.integration
def test_staging_detects_missing_asset(tmp_path):
    root, ref = _asset(tmp_path)
    (root / REL).unlink()
    execution = tmp_path / "private"
    execution.mkdir()
    with pytest.raises(FileNotFoundError, match="B02_G5_IMAGE_ASSET_MISSING_OR_LINK"):
        stage_image_assets((ref,), source_root=root, execution_dir=execution)


@pytest.mark.integration
def test_runner_stages_files_for_tectonic_without_real_compiler(tmp_path, monkeypatch):
    root, ref = _asset(tmp_path)
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setenv("APP_ROOT", str(root))
    calls = []

    def fake_run(cmd, *, capture_output, text, encoding, timeout, cwd):
        assert cmd == ["tectonic", "--untrusted", "doc.tex"]
        private = Path(cwd)
        assert (private / "assets" / (DIGEST + ".png")).read_bytes() == PNG
        assert "assets/" + DIGEST + ".png" in (private / "doc.tex").read_text(encoding="utf-8")
        (private / "doc.pdf").write_bytes(b"%PDF-1.5\nsynthetic")
        calls.append(cmd)
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr("apps.compiler.tectonic_runner.subprocess.run", fake_run)
    document = r"\includegraphics{assets/" + DIGEST + ".png}"
    path = HostTectonicRunner().compile(
        document, str(out), "rendered.pdf", image_assets=(ref,)
    )
    assert Path(path).read_bytes().startswith(b"%PDF-")
    assert len(calls) == 1


@pytest.mark.integration
def test_runner_refuses_tampering_before_compiler(tmp_path, monkeypatch):
    root, ref = _asset(tmp_path, PNG + b"tampered")
    out = tmp_path / "out"
    out.mkdir()
    monkeypatch.setenv("APP_ROOT", str(root))
    calls = []
    monkeypatch.setattr("apps.compiler.tectonic_runner.subprocess.run", lambda *a, **k: calls.append(a))
    with pytest.raises(ValueError, match="B02_G5_IMAGE_HASH_MISMATCH"):
        HostTectonicRunner().compile(r"\includegraphics{assets/x.png}", str(out), image_assets=(ref,))
    assert not calls
    assert list(out.iterdir()) == []
