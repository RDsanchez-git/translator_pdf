#!/usr/bin/env python3
"""A05-Q1/Q2/Q3: preflight de solo lectura para VM Linux descartable.

No ejecuta pytest, imports del proyecto, mutaciones, probes de red ni limpieza.
No puede certificar el firewall/hipervisor desde el guest: requiere evidencia
del host y revisión humana antes de habilitar A-06.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys

TARGET = "tests/integration/test_g3_b3_structured_result_contract.py"
NAMES = (
    "test_two_nodes_one_chunk_response_order_is_identity_based_not_positional",
    "test_only_preserve_nodes_materialize_without_provider_results",
    "test_unknown_chunk_rejected_before_payload_parse",
    "test_translated_unicode_surrogates_rejected_before_projection",
)
HOST_FS = {"9p", "vboxsf", "virtiofs", "cifs", "nfs", "nfs4", "drvfs", "fuse.vmhgfs-fuse"}
WATCH = ("tests/fixtures", "tests/golden", "infra/db")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], text=True,
                            capture_output=True, check=False)
    if result.returncode:
        raise ValueError("git " + args[0] + " failed: " + result.stderr[:250])
    return result.stdout.strip()


def inside(parent: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected JSON object: " + path.name)
    return value


def mount_type(path: Path) -> str | None:
    info = Path("/proc/self/mountinfo")
    if not info.is_file():
        return None
    best = (0, None)
    for line in info.read_text(encoding="utf-8").splitlines():
        left, separator, right = line.partition(" - ")
        if not separator:
            continue
        fields = left.split()
        types = right.split()
        if len(fields) < 5 or not types:
            continue
        mountpoint = fields[4].replace("\\040", " ")
        if inside(Path(mountpoint), path) and len(mountpoint) > best[0]:
            best = (len(mountpoint), types[0])
    return best[1]


def inventory(root: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    blockers: list[str] = []
    for prefix in WATCH:
        watched = root / prefix
        if watched.is_symlink():
            blockers.append("SYMLINK_WATCH_ROOT:" + prefix)
            continue
        if not watched.exists():
            records.append({"path": prefix, "state": "absent"})
            continue
        for folder, dirs, files in os.walk(watched, followlinks=False):
            for name in dirs:
                path = Path(folder) / name
                if path.is_symlink():
                    blockers.append("SYMLINK_DIR:" + path.relative_to(root).as_posix())
            for name in sorted(files):
                path = Path(folder) / name
                rel = path.relative_to(root).as_posix()
                if path.is_symlink() or not path.is_file():
                    blockers.append("NONREGULAR_FILE:" + rel)
                    continue
                size = path.stat().st_size
                if size > 32 * 1024 * 1024:
                    blockers.append("LARGE_FILE_NOT_HASHED:" + rel)
                    records.append({"path": rel, "size": size, "sha256": None})
                    continue
                digest = sha256()
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                records.append({"path": rel, "size": size, "sha256": digest.hexdigest()})
    return sorted(records, key=lambda v: v["path"]), blockers


def collection_check(root: Path, reports: Path) -> tuple[dict, list[str]]:
    problems: list[str] = []
    manifest = load(reports / "manifest.json")
    collection = load(reports / "all.json")
    revision = manifest.get("revision_sha", "")
    if (manifest.get("repository") != "RDsanchez-git/translator_pdf"
            or not isinstance(revision, str)
            or not re.fullmatch("[0-9a-f]{40}", revision)):
        return {}, ["COLLECTION_MANIFEST_INVALID"]
    try:
        same = git(root, "rev-parse", revision + ":tests") == git(root, "rev-parse", "HEAD:tests")
    except ValueError:
        return {}, ["COLLECTION_REVISION_NOT_IN_GUEST_HISTORY"]
    if not same:
        problems.append("TESTS_TREE_DIFFERS_FROM_FROZEN_COLLECTION")
    items = collection.get("items")
    if not isinstance(items, list) or collection.get("count") != len(items):
        return {}, problems + ["COLLECTION_ITEMS_INVALID"]
    ids = [v.get("nodeid") for v in items if isinstance(v, dict)]
    if len(ids) != 1474 or len(ids) != len(set(ids)):
        problems.append("FROZEN_COLLECTION_CARDINALITY_MISMATCH")
    expected = [TARGET + "::" + name for name in NAMES]
    matching = [v for v in items if isinstance(v, dict) and v.get("nodeid") in expected]
    if len(matching) != 4:
        problems.append("FOCAL_NODEIDS_NOT_EXACTLY_FOUR")
    if any({"skip", "skipif", "xfail", "e2e"} & set(v.get("markers") or ()) for v in matching):
        problems.append("FOCAL_MARKER_UNSAFE")
    return {
        "frozen_collection_sha": revision, "tests_tree_matches": same,
        "all_nodes": len(ids), "focal_nodeids": expected,
        "matched_focal_nodeids": len(matching),
        "scope": "CANDIDATES_NOT_EXECUTED",
    }, problems


def host_evidence(path: Path | None) -> tuple[dict, list[str]]:
    if path is None:
        return {"status": "NOT_PROVIDED"}, ["HOST_OS_ISOLATION_UNVERIFIED"]
    data = load(path)
    required = (
        "guest_private_disk_no_host_shares",
        "guest_checkout_without_host_bind_mounts",
        "no_host_secrets_or_agents_mounted",
        "network_egress_denied_by_host_or_hypervisor",
    )
    if not all(data.get(flag) is True for flag in required):
        return {"status": "INCOMPLETE_DECLARATION"}, ["HOST_EVIDENCE_INCOMPLETE"]
    method = data.get("verification_method", "")
    if not isinstance(method, str) or len(method.strip()) < 20:
        return {"status": "NO_VERIFICATION_METHOD"}, ["HOST_METHOD_UNDOCUMENTED"]
    return {
        "status": "DECLARED_NOT_INDEPENDENTLY_VERIFIED",
        "declared_guards": list(required), "verification_method": method,
    }, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host-evidence", type=Path, default=None)
    args = parser.parse_args()
    root, reports, output = (p.resolve() for p in (args.repo_root, args.reports, args.output))
    if sys.platform != "linux":
        raise ValueError("ONLY_GUEST_LINUX_SUPPORTED; never run on owner Windows checkout")
    if not (root / ".git").is_dir() or not (root / "pyproject.toml").is_file():
        raise ValueError("GUEST_STANDALONE_REPOSITORY_REQUIRED")
    if output.exists() or inside(root, output) or inside(output, root):
        raise ValueError("OUTPUT_MUST_BE_NEW_AND_OUTSIDE_REPOSITORY")
    if inside(root, reports):
        raise ValueError("COLLECTION_REPORTS_MUST_BE_OUTSIDE_REPOSITORY")
    if args.host_evidence and inside(root, args.host_evidence):
        raise ValueError("HOST_EVIDENCE_MUST_BE_OUTSIDE_REPOSITORY")

    issues: list[str] = []
    head = git(root, "rev-parse", "HEAD")
    dirty = bool(git(root, "status", "--porcelain=v1", "--untracked-files=all"))
    remote = bool(git(root, "remote"))
    if dirty:
        issues.append("GUEST_WORKTREE_NOT_CLEAN")
    if remote:
        issues.append("GUEST_GIT_REMOTE_NOT_REMOVED")
    if os.geteuid() == 0:
        issues.append("GUEST_PROCESS_IS_ROOT")
    mounts = {label: mount_type(path) for label, path in
              (("repo", root), ("reports", reports), ("output", output.parent))}
    if any(value is None for value in mounts.values()):
        issues.append("MOUNT_INFORMATION_UNAVAILABLE")
    if any(value in HOST_FS for value in mounts.values()):
        issues.append("KNOWN_HOST_SHARED_FILESYSTEM_DETECTED")
    sensitive = sorted(key for key in os.environ
                       if re.search(r"(^|_)(TOKEN|SECRET|PASSWORD|PASSWD|API_KEY|ACCESS_KEY|PRIVATE_KEY|CREDENTIAL)($|_)", key, re.I)
                       or key.startswith(("AWS_", "AZURE_", "GCP_", "OPENAI_", "GEMINI_")))
    if sensitive:
        issues.append("CREDENTIAL_LIKE_ENVIRONMENT_NAMES_PRESENT")
    records, inv_issues = inventory(root)
    issues.extend(inv_issues)
    collection, col_issues = collection_check(root, reports)
    issues.extend(col_issues)
    attestation, host_issues = host_evidence(args.host_evidence)
    issues.extend(host_issues)
    output.mkdir(parents=True, exist_ok=False)
    evidence = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "READ_ONLY_PREFLIGHT_NO_PYTEST_NO_NETWORK_PROBES",
        "guest_git_head": head,
        "guest_status_clean": not dirty, "guest_has_no_remote": not remote,
        "guest_unprivileged": os.geteuid() != 0,
        "guest_mount_filesystems": mounts,
        "credential_like_environment_variable_NAMES_ONLY": sensitive,
        "host_evidence": attestation,
        "technical_input_inventory": records,
        "focal_selection": collection,
        "blockers": sorted(set(issues)),
        "gate": "BLOCKED" if issues else "READY_FOR_INDEPENDENT_HOST_REVIEW",
        "limits": [
            "A guest cannot independently prove absence of host mounts or OS-level egress.",
            "Filesystem snapshot covers technical fixture paths only, never corpus canonical.",
            "No tests, imports, collection, provider calls, or mutations were executed.",
            "No approval for full suite; host evidence requires human verification.",
        ],
    }
    (output / "preflight.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "focal_nodeids.txt").write_text(
        "\n".join(collection.get("focal_nodeids", [])) + "\n", encoding="utf-8")
    print("A05_PREFLIGHT=" + evidence["gate"])
    print("PINNED_GUEST_HEAD=" + head)
    print("Q2_INVENTORY_ENTRIES=" + str(len(records)))
    print("Q3_MATCHED=" + str(collection.get("matched_focal_nodeids", 0)) + "/4")
    print("BLOCKERS=" + ",".join(evidence["blockers"]))
    print("OUTPUT=" + str(output))
    print("TEST_BODIES_EXECUTED=0")
    return 2 if issues else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print("A05_PREPARATION_ERROR: " + str(exc), file=sys.stderr)
        raise SystemExit(3)
