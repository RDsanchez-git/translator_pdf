"""C0: fail-closed tests for one-shot UID ownership initializer.

All tests run without Docker or root and never chown real volume paths.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from apps.lab import convergence_db_bootstrap as init


def _fixture(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[tuple[str, ...], list[Path]]:
    dirs = [tmp_path / p for p in ("state", "data", "output", "hf", "torch", "tectonic")]
    for path in dirs:
        path.mkdir()
    bootstrap = tmp_path / "bootstrap.py"
    bootstrap.write_text("pass", encoding="utf-8")
    volumes = tuple(str(x) for x in dirs)
    monkeypatch.setattr(init, "_VOLUMES", volumes)
    monkeypatch.setattr(init, "_BOOTSTRAP", str(bootstrap))
    monkeypatch.setattr(init, "_AUDIT_UID", tmp_path.stat().st_uid)
    monkeypatch.setattr(init, "_AUDIT_GID", tmp_path.stat().st_gid)
    monkeypatch.setattr(init.os, "geteuid", lambda: 0, raising=False)
    monkeypatch.setenv("TPDF_C0_VOLUME_INIT", init._OPT_IN)
    return volumes, dirs


def test_prepares_only_expected_volume_roots_and_db(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    volumes, dirs = _fixture(monkeypatch, tmp_path)
    changed: list[Path] = []
    monkeypatch.setattr(init.os, "chown", lambda path, _uid, _gid: changed.append(Path(path)))
    init.prepare_volume_owners(set(volumes) | {"/workspace"})
    assert (dirs[0] / "db").is_dir()
    assert changed == dirs + [dirs[0] / "db"]


def test_denies_missing_mount_before_any_mutation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    volumes, _ = _fixture(monkeypatch, tmp_path)
    monkeypatch.setattr(init.os, "chown", lambda *_: pytest.fail("unexpected chown"))
    with pytest.raises(RuntimeError, match="MOUNT_MISMATCH"):
        init.prepare_volume_owners(set(volumes[:-1]) | {"/workspace"})


def test_denies_missing_explicit_opt_in(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    volumes, _ = _fixture(monkeypatch, tmp_path)
    monkeypatch.delenv("TPDF_C0_VOLUME_INIT")
    with pytest.raises(RuntimeError, match="REQUIRES_EXPLICIT_LAB_ROOT"):
        init.prepare_volume_owners(set(volumes) | {"/workspace"})


def test_denies_non_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    volumes, _ = _fixture(monkeypatch, tmp_path)
    monkeypatch.setattr(init.os, "geteuid", lambda: 10001, raising=False)
    with pytest.raises(RuntimeError, match="REQUIRES_EXPLICIT_LAB_ROOT"):
        init.prepare_volume_owners(set(volumes) | {"/workspace"})


def test_denies_symlink_state_db_before_chown(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    volumes, dirs = _fixture(monkeypatch, tmp_path)
    try:
        (dirs[0] / "db").symlink_to(tmp_path, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Host does not allow symlink creation")
    monkeypatch.setattr(init.os, "chown", lambda *_: pytest.fail("unexpected chown"))
    with pytest.raises(RuntimeError, match="DB_SYMLINK_FORBIDDEN"):
        init.prepare_volume_owners(set(volumes) | {"/workspace"})


def test_drop_privileges_precedes_real_bootstrap_exec(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(init, "_mount_targets", lambda: {"/workspace"})
    monkeypatch.setattr(init, "prepare_volume_owners", lambda _mounts: calls.append("prepared"))
    monkeypatch.setattr(init.os, "setgroups", lambda _: calls.append("setgroups"), raising=False)
    monkeypatch.setattr(init.os, "setgid", lambda _: calls.append("setgid"), raising=False)
    monkeypatch.setattr(init.os, "setuid", lambda _: calls.append("setuid"), raising=False)
    monkeypatch.setattr(init.os, "execv", lambda _python, _args: calls.append("execv"))
    init.main()
    assert calls == ["prepared", "setgroups", "setgid", "setuid", "execv"]
