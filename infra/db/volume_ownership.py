"""Shared Linux volume preparation for explicit one-node bootstrap.

Only the six declared mount roots and the state/db directory may be changed.
Callers own the mode-specific root opt-in; application bootstrap runs unprivileged.
"""
from pathlib import Path
import os
import sys

UID = 10001
GID = 10001
VOLUMES = (
    "/app/state", "/app/data", "/app/output",
    "/app/.cache/hf", "/app/.cache/torch", "/app/.cache/tectonic",
)
BOOTSTRAP = "/workspace/infra/db/bootstrap.py"


def mount_targets() -> set[str]:
    with open("/proc/self/mountinfo", encoding="utf-8") as stream:
        return {line.split(" - ", 1)[0].split()[4] for line in stream}


def prepare_owners(
    mounts: set[str], volumes: tuple[str, ...], bootstrap: str,
    uid: int, gid: int,
) -> None:
    if os.geteuid() != 0:
        raise RuntimeError("VOLUME_INIT_ROOT_REQUIRED")
    if not set(volumes).issubset(mounts) or "/workspace" not in mounts:
        raise RuntimeError("VOLUME_INIT_MOUNT_MISMATCH")
    if not Path(bootstrap).is_file():
        raise RuntimeError("VOLUME_INIT_CURRENT_BOOTSTRAP_MISSING")

    directories = [Path(x) for x in volumes]
    db = directories[0] / "db"
    if db.is_symlink():
        raise RuntimeError("VOLUME_INIT_DB_SYMLINK_FORBIDDEN")
    for path in directories + ([db] if db.exists() else []):
        if not path.is_dir() or path.is_symlink():
            raise RuntimeError("VOLUME_INIT_DIRECTORY_DRIFT")
        owner = (path.stat().st_uid, path.stat().st_gid)
        if owner not in ((0, 0), (uid, gid)):
            raise RuntimeError("VOLUME_INIT_UNEXPECTED_OWNER")
        if owner != (uid, gid) and any(path.iterdir()):
            raise RuntimeError("VOLUME_INIT_NONEMPTY_UNOWNED_DIRECTORY")

    # No recursive chown or migration of historical data.
    for path in directories:
        os.chown(path, uid, gid)
    db.mkdir(mode=0o755, exist_ok=True)
    os.chown(db, uid, gid)


def exec_unprivileged(bootstrap: str, uid: int, gid: int) -> None:
    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)
    if (os.geteuid(), os.getegid()) != (uid, gid) or os.getgroups():
        raise RuntimeError("VOLUME_INIT_PRIVILEGE_DROP_FAILED")
    os.execv(sys.executable, [sys.executable, "-B", bootstrap])
