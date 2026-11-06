"""B03.2 isolation and historical cache selection; never invokes Docker or LLM."""
import hashlib
from pathlib import Path
from types import SimpleNamespace
import tarfile
import zipfile

import pytest

from apps.lab import offline_pdf_lab as lab


def test_container_reuses_pinned_runtime_and_never_has_external_network(tmp_path):
    repo = tmp_path / "repo"
    work = tmp_path / "work"
    source = tmp_path / "source.pdf"
    args = lab._container_command(repo, work, source=source)
    assert args[:5] == ["docker", "run", "--rm", "--pull", "never"]
    assert args[args.index("--network") + 1] == "none"
    assert args[args.index("--entrypoint") + 1] == "python"
    assert args[-2:] == ["--inside-source", "/lab_source.pdf"]
    assert "--privileged" not in args
    assert "--publish" not in args and "-p" not in args
    assert "--env-file" not in args
    assert args.count("--mount") == 6
    assert "type=bind,source=" + str(repo) + ",target=/workspace,readonly" in args
    assert "type=bind,source=" + str(repo) + ",target=/app,readonly" not in args
    assert args[args.index("--workdir") + 1] == "/app"
    assert "type=bind,source=" + str(source) + ",target=/lab_source.pdf,readonly" in args
    assert lab.RUNTIME_IMAGE in args
    assert "GROQ_API_KEY=" + lab.DUMMY_KEY in args
    assert "GROQ_BASE_URL=http://127.0.0.1:8080" in args
    assert "SQLITE_STATE_DIR=/app/state" in args
    assert "PYTHONPATH=/workspace" in args
    assert "PYTHONSAFEPATH=1" in args
    assert "HTTP_PROXY=" in args and "NO_PROXY=localhost,127.0.0.1" in args


def test_container_smoke_has_no_pdf_input_mount(tmp_path):
    args = lab._container_command(tmp_path, tmp_path / "work", source=None)
    assert args.count("--mount") == 5
    assert "--inside-source" not in args
    assert args[-4:] == ["-B", "-m", "apps.lab.offline_pdf_lab", "--inside-run"]
    # Nested volumes target a writable image /app, not the read-only source.
    mounts = [args[i + 1] for i, a in enumerate(args[:-1]) if a == "--mount"]
    assert "/workspace,readonly" in mounts[0]
    assert "/app/data" in mounts[1] and "/app/output" in mounts[2]


@pytest.mark.parametrize("path,expected", [
    ("volumes/tectonic_cache/files/00/abcdef", "cache/files/00/abcdef"),
    ("volumes/g3_runtime_data/tiktoken-cache/abcd", "data/tiktoken-cache/abcd"),
    ("volumes/g3_runtime_data/ast_cache/ast.json", None),
    ("volumes/g3_runtime_output/translated.pdf", None),
    ("volumes/g3_runtime_state/queue.db", None),
    ("volumes/g3_runtime_data/archive/original.pdf", None),
])
def test_seed_uses_only_whitelisted_caches(tmp_path, path, expected):
    entry = tarfile.TarInfo(path)
    dest = lab._cache_destination(entry, tmp_path)
    assert (str(dest.relative_to(tmp_path)).replace("\\", "/") if dest else None) == expected


@pytest.mark.parametrize("name", ["/etc/passwd", "volumes/tectonic_cache/../../escape", "volumes\\tectonic_cache\\evil"])
def test_archive_rejects_traversal_and_windows_backslashes(tmp_path, name):
    with pytest.raises(lab.LabError, match="UNSAFE_ARCHIVE_PATH"):
        lab._cache_destination(tarfile.TarInfo(name), tmp_path)


def test_history_hash_must_match_before_opening(tmp_path):
    path = tmp_path / lab.HISTORY_ZIP
    path.write_bytes(b"fake zip")
    with pytest.raises(lab.LabError, match="HASH_MISMATCH"):
        lab._check_history(path)


def test_missing_history_stops_without_mkdir(tmp_path):
    path = tmp_path / "unavailable.zip"
    with pytest.raises(lab.LabError, match="NOT_FOUND"):
        lab._check_history(path)
    assert list(tmp_path.iterdir()) == []


def test_docker_preflight_rejects_wrong_context_without_running_container(monkeypatch):
    calls = []
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return SimpleNamespace(stdout="remote-server\n")
    monkeypatch.setattr(lab.subprocess, "run", fake_run)
    with pytest.raises(lab.LabError, match="NOT_DESKTOP_LINUX"):
        lab._docker_image_id()
    assert calls == [["docker", "context", "show"]]


def test_docker_preflight_checks_exact_image_digest(monkeypatch):
    calls = []
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return SimpleNamespace(stdout="desktop-linux\n" if cmd[1] == "context" else lab.IMAGE_ID + "\n")
    monkeypatch.setattr(lab.subprocess, "run", fake_run)
    assert lab._docker_image_id() == lab.IMAGE_ID
    assert calls[1] == ["docker", "image", "inspect", lab.RUNTIME_IMAGE, "--format", "{{.Id}}"]


def test_source_pdf_precondition_uses_bytes_not_extension(tmp_path):
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not a pdf")
    with bad.open("rb") as fd:
        assert fd.read(5) != b"%PDF-"
