"""C0/T01 only: initialize fresh Docker volume ownership, then drop privileges.

The pinned historical image runs as uid 10001. Docker's named volumes are
root-owned when nocopy=true, so the first bootstrap cannot create SQLite DBs.
This wrapper runs as root *only* in the isolated Compose laboratory, adjusts
the volume directory entries (never recursively), then execs the existing
bootstrap as uid/gid 10001. It must not be used in product deployments.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys

_AUDIT_UID = 10001
_AUDIT_GID = 10001
_OPT_IN = "EXPLICIT_CONVERGENCE_C0_LAB_ONLY"
_VOLUMES = (
    "/app/state",
    "/app/data",
    "/app/output",
    "/app/.cache/hf",
    "/app/.cache/torch",
    "/app/.cache/tectonic",
)
_BOOTSTRAP = "/workspace/infra/db/bootstrap.py"


def _mount_targets() -> set[str]:
    """Inspect the kernel's mounts, not directory existence alone."""
    with open("/proc/self/mountinfo", encoding="utf-8") as stream:
        return {line.split(" - ", 1)[0].split()[4] for line in stream}


def prepare_volume_owners(mounts: set[str]) -> None:
    """Fail closed before any chown if the expected lab mounts are missing."""
    if os.geteuid() != 0 or os.getenv("TPDF_C0_VOLUME_INIT") != _OPT_IN:
        raise RuntimeError("C0_VOLUME_INIT_REQUIRES_EXPLICIT_LAB_ROOT")
    if not set(_VOLUMES).issubset(mounts) or "/workspace" not in mounts:
        raise RuntimeError("C0_VOLUME_INIT_MOUNT_MISMATCH")
    if not Path(_BOOTSTRAP).is_file():
        raise RuntimeError("C0_VOLUME_INIT_CURRENT_BOOTSTRAP_MISSING")

    directories = [Path(x) for x in _VOLUMES]
    db = Path("/app/state/db")
    if db.is_symlink():
        raise RuntimeError("C0_VOLUME_INIT_DB_SYMLINK_FORBIDDEN")
    for path in directories + ([db] if db.exists() else []):
        if not path.is_dir() or path.is_symlink():
            raise RuntimeError("C0_VOLUME_INIT_DIRECTORY_DRIFT")
        if path.stat().st_uid not in (0, _AUDIT_UID):
            raise RuntimeError("C0_VOLUME_INIT_UNEXPECTED_OWNER")

    for path in directories:
        os.chown(path, _AUDIT_UID, _AUDIT_GID)
    db.mkdir(mode=0o755, exist_ok=True)
    os.chown(db, _AUDIT_UID, _AUDIT_GID)


def main() -> None:
    try:
        prepare_volume_owners(_mount_targets())
    except (OSError, RuntimeError, IndexError) as exc:
        raise SystemExit("C0_VOLUME_INIT_BLOCKED: " + str(exc)) from exc
    # Never execute product bootstrap with root privileges.
    os.setgroups([])
    os.setgid(_AUDIT_GID)
    os.setuid(_AUDIT_UID)
    os.execv(sys.executable, [sys.executable, "-B", _BOOTSTRAP])


if __name__ == "__main__":
    main()
