#!/usr/bin/env python3
"""Read-only post-collection inventory of retained A-01 isolated clone.

Does not execute tests, import project packages, open PDFs/DBs, or write files.
Lists ignored/untracked paths in tests/ and infra/db/, plus fixed path probes.
A post-only inventory is NOT proof of when a file appeared, OS sandboxing,
absence of network activity, or complete filesystem effects.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys

EXPECTED_SHA = "86cd68672ee692f073b62869e7c9bd177e8d9e3b"
SCOPES = ("tests", "infra/db")
PROBES = (
    "tests/fixtures/sample_3_pages.pdf",
    "tests/fixtures/sample_3_pages.pdf.ast.json",
    "tests/fixtures/sample_chunks.json",
    "tests/golden/sample_3_pages.fingerprint.json",
    "tests/golden/sample_3_pages.semantics.json",
    "tests/fixtures/e2e_cache_real.db",
    "tests/fixtures/e2e_cache_real.db-wal",
    "tests/fixtures/e2e_cache_real.db-shm",
    "infra/db/test_fsm.db",
    "infra/db/test_fsm.db-wal",
    "infra/db/test_fsm.db-shm",
    "infra/db/documents.db",
    "infra/db/documents.db-wal",
    "infra/db/documents.db-shm",
    "tests/stress_report.json",
)


def git(repo: Path, *args: str) -> str:
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    p = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False, timeout=30, env=env,
    )
    if p.returncode:
        raise ValueError(f"Git read failed ({' '.join(args)}): {p.stderr.strip()[:400]}")
    return p.stdout


def paths_from_git(repo: Path, ignored: bool) -> list[str]:
    args = ["ls-files", "--others"]
    if ignored:
        args.append("--ignored")
    args.extend(["--exclude-standard", "-z", "--", *SCOPES])
    # NUL terminators tolerate spaces/newlines in filenames.
    raw = git(repo, *args)
    return sorted(x.replace("\\", "/") for x in raw.split("\0") if x)


def scan(clone: Path, reports: Path, limit: int) -> dict[str, object]:
    if "translator-a01-isolated-" not in str(clone) or clone.name != "repo":
        raise ValueError("This script accepts only a retained translator-a01-isolated-*/repo clone")
    repo_root = Path(git(clone, "rev-parse", "--show-toplevel").strip()).resolve()
    if repo_root != clone.resolve():
        raise ValueError("Provided path is not the Git clone root")
    sha = git(clone, "rev-parse", "HEAD").strip()
    if sha != EXPECTED_SHA:
        raise ValueError(f"Clone SHA {sha} does not match collection SHA {EXPECTED_SHA}")

    manifest = json.loads((reports / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("revision_sha") != EXPECTED_SHA:
        raise ValueError("Collection manifest SHA mismatch")
    if manifest.get("modes", {}).get("all", {}).get("exit_code") != 0:
        raise ValueError("Collection did not complete")
    original_report = json.loads((reports / "all.json").read_text(encoding="utf-8"))
    if len(original_report.get("items", [])) != 1474:
        raise ValueError("Expected 1474 collected all-mode nodeids")
    selected_report = json.loads((reports / "technical.json").read_text(encoding="utf-8"))
    all_items = original_report["items"]
    technical_items = selected_report.get("items", [])
    if len(technical_items) != 1454:
        raise ValueError("Expected 1454 not-e2e technical items")
    technical_ids = {x["nodeid"] for x in technical_items}

    tracked = git(clone, "diff", "--name-only", "HEAD", "--", *SCOPES).strip().splitlines()
    untracked = paths_from_git(clone, ignored=False)
    ignored = paths_from_git(clone, ignored=True)
    statuses = {p: "UNTRACKED" for p in untracked}
    statuses.update({p: "IGNORED" for p in ignored})
    fixed = []
    for rel in PROBES:
        target = clone / rel
        if target.is_file():
            size = target.stat().st_size
            kind = statuses.get(rel, "TRACKED_OR_OTHER_PRESENT")
            exists = True
        elif target.exists():
            size = None
            kind = "OTHER_PRESENT"
            exists = True
        else:
            size = None
            kind = "ABSENT"
            exists = False
        fixed.append({"relative_path": rel, "exists": exists, "bytes": size, "category": kind})

    watched = (
        "tests/integration/test_real_e2e.py",
        "tests/integration/test_e2e_walking_skeleton.py",
        "tests/integration/test_pipeline_orchestration.py",
        "tests/integration/test_real_parser_pipeline.py",
        "tests/integration/test_recovery_flow.py",
        "tests/integration/test_healing_e2e_telemetry.py",
        "tests/integration/test_translation_semantics.py",
    )
    marker_rows = []
    for path in watched:
        selected = [x for x in all_items if x["nodeid"].split("::", 1)[0] == path]
        marker_rows.append({
            "file": path,
            "collected": len(selected),
            "selected_by_not_e2e": sum(x["nodeid"] in technical_ids for x in selected),
            "e2e_marked": sum("e2e" in x.get("markers", []) for x in selected),
        })

    classification = Counter(
        "PY_CACHE" if "__pycache__/" in p or p.endswith(".pyc")
        else "SQLITE" if p.endswith((".db", ".db-wal", ".db-shm", ".sqlite"))
        else "JSON" if p.endswith(".json")
        else "OTHER"
        for p in [*untracked, *ignored]
    )
    return {
        "scope": "RETAINED_CLONE_POSTCOLLECT_READ_ONLY_NOT_BEFORE_AFTER",
        "clone_revision": sha,
        "tracked_changes_within_tests_or_infra_db": tracked,
        "untracked_count": len(untracked),
        "ignored_count": len(ignored),
        "types_of_untracked_and_ignored": dict(sorted(classification.items())),
        "untracked_sample": untracked[:limit],
        "ignored_sample": ignored[:limit],
        "named_path_probes": fixed,
        "historical_test_selector_membership": marker_rows,
        "limitations": [
            "No pre-collection listing exists here: paths found are not necessarily created during pytest collection.",
            "Scope limited to clone/tests and clone/infra/db; other repository, host and external paths not inspected.",
            "Python .pyc and __pycache__ are ordinary import artifacts, not evidence of a test body running.",
            "No OS network/filesystem sandbox certification; egress and imported plugin effects remain unknown.",
            "No source or untracked file content was opened; only file names and size metadata were read.",
            "The owner original repository and intentionally deleted PDF are not accessed or modified.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--isolated-repo", required=True, type=Path)
    parser.add_argument("--reports", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=35)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    try:
        result = scan(args.isolated_repo.resolve(), args.reports.resolve(), args.limit)
    except (OSError, TypeError, KeyError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"A05_ISOLATED_INSPECTION_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
