"""Offline compiler inputs and pre-effect guards; no network or native compiler."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.compiler.tectonic_runner import CachedTectonicResources, HostTectonicRunner
from apps.lab import pppr_offline_compiler as compiler
from apps.lab.pppr_offline_scope import OfflineLabScope
from core.execution.exceptions import G3ExternalEffectNotStartedError


def test_missing_compiler_scope_fails_closed():
    with pytest.raises(G3ExternalEffectNotStartedError, match="COMPILER_RESOURCES_REQUIRED"):
        OfflineLabScope("a" * 64).require_compiler_resources()


def test_font_identity_checks_bytes_not_only_name_and_size(tmp_path, monkeypatch):
    data = b"OTTOverified"
    name = "lmroman12-bold.otf"
    path = tmp_path / name
    path.write_bytes(data)
    monkeypatch.setattr(compiler, "EXTRA_FONTS", ((name, len(data), sha256(data).hexdigest()),))
    assert compiler.read_extra_fonts(tmp_path) == ((name, data),)
    path.write_bytes(b"OTTOverifieD")
    with pytest.raises(ValueError, match="FONT_IDENTITY_DRIFT"):
        compiler.read_extra_fonts(tmp_path)


def test_font_missing_before_acquisition_or_docker(tmp_path):
    with pytest.raises(ValueError, match="FONT_MISSING_OR_SIZE_DRIFT"):
        compiler.read_extra_fonts(tmp_path)


@pytest.mark.parametrize("names", [("../escape.otf",), ("font.otf", "font.otf"), ()])
def test_cached_resource_rejects_invalid_names(tmp_path, names):
    with pytest.raises(ValueError, match="INVALID_CACHED_RESOURCES"):
        CachedTectonicResources(tmp_path, tuple((name, b"OTTOdata") for name in names))


def test_cache_only_runner_stages_font_and_config_per_execution(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    cache.mkdir()
    font = b"OTTOverified"
    resources = CachedTectonicResources(cache, (("font.otf", font),))
    observed = []

    def run(cmd, **kwargs):
        work = Path(kwargs["cwd"])
        env = kwargs["env"]
        assert cmd == ["tectonic", "--untrusted", "--only-cached", "doc.tex"]
        assert (work / "font.otf").read_bytes() == font
        assert env["XDG_CACHE_HOME"] == str(cache)
        assert env["FONTCONFIG_FILE"] == str(work / "fonts.conf")
        assert str(work) in (work / "fonts.conf").read_text()
        (work / "doc.pdf").write_bytes(b"%PDF-1.4")
        observed.append(work)
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr("apps.compiler.tectonic_runner.subprocess.run", run)
    result = HostTectonicRunner(cached_resources=resources).compile("test", str(tmp_path))
    assert Path(result).read_bytes() == b"%PDF-1.4"
    assert len(observed) == 1 and not observed[0].exists()
    assert list(cache.iterdir()) == []


def test_default_runner_retains_existing_command(tmp_path, monkeypatch):
    def run(cmd, **kwargs):
        assert cmd == ["tectonic", "--untrusted", "doc.tex"]
        assert "env" not in kwargs
        assert not (Path(kwargs["cwd"]) / "fonts.conf").exists()
        (Path(kwargs["cwd"]) / "doc.pdf").write_bytes(b"%PDF-1.4")
        return SimpleNamespace(returncode=0, stderr="")
    monkeypatch.setattr("apps.compiler.tectonic_runner.subprocess.run", run)
    assert Path(HostTectonicRunner().compile("test", str(tmp_path))).is_file()


def test_cache_tree_rejects_missing_coverage(tmp_path):
    with pytest.raises(ValueError, match="CACHE_IDENTITY_DRIFT"):
        compiler.verify_cache(tmp_path)


def test_missing_fonts_stops_launcher_before_workspace(tmp_path, monkeypatch):
    from apps.lab import offline_pdf_lab as lab
    monkeypatch.setattr(lab, "_check_checkout", lambda _: None)
    monkeypatch.setattr(lab, "_check_history", lambda _: None)
    monkeypatch.setattr(lab, "_docker_image_id", lambda: lab.IMAGE_ID)
    monkeypatch.setattr(lab.shutil, "disk_usage", lambda _: SimpleNamespace(free=40*1024**3))
    def forbidden(*args, **kwargs):
        pytest.fail("workspace created before fonts validated")
    monkeypatch.setattr(lab.tempfile, "mkdtemp", forbidden)
    with pytest.raises(lab.LabError, match="FONT_DIRECTORY_REQUIRED"):
        lab._launch(tmp_path, tmp_path / "history.zip", source=None,
                    export_dir=tmp_path / "output")
