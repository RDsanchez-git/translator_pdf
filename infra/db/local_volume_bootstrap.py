"""One-shot local runtime bootstrap; no dependency on laboratory/provider code."""
import os

from infra.db.volume_ownership import (
    BOOTSTRAP, GID, UID, VOLUMES, exec_unprivileged, mount_targets, prepare_owners,
)

OPT_IN = "EXPLICIT_LOCAL_RUNTIME_VOLUME_INIT"


def main() -> None:
    if os.getenv("TPDF_LOCAL_VOLUME_INIT") != OPT_IN:
        raise SystemExit("LOCAL_VOLUME_INIT_BLOCKED:EXPLICIT_OPT_IN_REQUIRED")
    try:
        prepare_owners(mount_targets(), VOLUMES, BOOTSTRAP, UID, GID)
        exec_unprivileged(BOOTSTRAP, UID, GID)
    except (OSError, RuntimeError, IndexError) as exc:
        raise SystemExit("LOCAL_VOLUME_INIT_BLOCKED:" + str(exc)) from exc


if __name__ == "__main__":
    main()
