#!/usr/bin/env python3
"""Opt-in G5 worker fail-closed mutations after a green three-test baseline.

Patches only the real SUT methods in fresh Python subprocesses inside the
runner's detached clone. No edits to runtime, tests, corpus, GT or CI.
Compilation/renderer remain the original tests' controlled doubles.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


CASES = {
    "g5_worker_stale_publish": {
        "nodeid": (
            "tests/integration/test_g5_assembler_worker_integration.py::"
            "test_real_worker_method_rejects_expired_lease_without_final_publication"
        ),
        "markers": ("Failed: DID NOT RAISE",),
    },
    "g5_worker_unrecorded_compiler_failure": {
        "nodeid": (
            "tests/integration/test_g5_assembler_worker_integration.py::"
            "test_real_worker_method_fences_failure_state"
        ),
        "markers": ("FAILED_RETRYABLE", "AssertionError"),
    },
}

CHILD = r'''
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from infra.db.assembly_recovery import AssemblyLeaseRepository

case, nodeid, base_temp = sys.argv[1:]
options = [
    "-q", "-ra", "--tb=short", "--no-header",
    "-o", "addopts=", "-p", "no:cacheprovider",
    "--basetemp", str(Path(base_temp) / case), nodeid,
]

if case == "g5_worker_stale_publish":
    original = AssemblyLeaseRepository._has_authority

    def ignores_expiry_during_publish(
        self, lease, now,
        phases=("ASSEMBLING", "READY_FOR_COMPILATION", "COMPILING"),
    ):
        # Regression: publication accepts a lease whose expiration has passed,
        # while all other ownership, execution-id and FSM checks still apply.
        if phases == ("COMPILING",):
            return original(self, lease, 0.0, phases)
        return original(self, lease, now, phases)

    with patch.object(
        AssemblyLeaseRepository, "_has_authority",
        new=ignores_expiry_during_publish,
    ):
        result = pytest.main(options)

elif case == "g5_worker_unrecorded_compiler_failure":
    # Regression: the compiler error escapes, but the worker fails to persist
    # its required FAILED_RETRYABLE/FAILED durable state.
    with patch.object(
        AssemblyLeaseRepository, "fail_authorized",
        new=lambda self, lease, reason: False,
    ):
        result = pytest.main(options)

else:
    raise SystemExit(100)

raise SystemExit(result)
'''


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True,
        text=True, encoding="utf-8", errors="replace",
        timeout=25, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"GIT_INSPECTION_FAILED: {' '.join(args)}")
    return proc.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reports", required=True, type=Path)
    args = ap.parse_args()

    if os.environ.get("TST_STAB_G5_WORKER_OPT_IN") != "1":
        raise RuntimeError("OPT_IN_REQUIRED")
    root = Path.cwd().resolve()
    reports = args.reports.resolve()
    if not (root / ".git").is_dir() or not (root / "pyproject.toml").is_file():
        raise RuntimeError("DETACHED_INDEPENDENT_GIT_CLONE_REQUIRED")
    if reports == root or root in reports.parents or not reports.is_dir():
        raise RuntimeError("REPORTS_MUST_BE_OUTSIDE_CLONE")
    if git(root, "remote"):
        raise RuntimeError("GIT_CLONE_MUST_HAVE_NO_REMOTES")
    if subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "-q", "HEAD"],
        capture_output=True, check=False,
    ).returncode == 0:
        raise RuntimeError("DETACHED_HEAD_REQUIRED")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("GIT_CLONE_DIRTY_BEFORE_PROBES")
    sha = git(root, "rev-parse", "HEAD")
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise RuntimeError("INVALID_SHA")

    cases = []
    for name, item in CASES.items():
        proc = subprocess.run(
            [sys.executable, "-B", "-c", CHILD, name, item["nodeid"],
             str(reports.parent / "temp")],
            cwd=root, env=os.environ.copy(),
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=120, check=False,
        )
        output = proc.stdout + (
            "\n--- STDERR ---\n" + proc.stderr if proc.stderr else ""
        )
        log = f"g5_worker_mutation_{name}.log"
        (reports / log).write_text(output, encoding="utf-8")
        killed = (
            proc.returncode == 1
            and re.search(r"\b1 failed\b", output) is not None
            and all(marker in output for marker in item["markers"])
            and "ERROR collecting" not in output
            and "INTERNALERROR" not in output
        )
        cases.append({
            "mutation": name,
            "nodeid": item["nodeid"],
            "expected_markers": list(item["markers"]),
            "exit_code": proc.returncode,
            "verdict": "MUTATION_KILLED" if killed else "NOT_ACCREDITED",
            "log": log,
        })

    if git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("GIT_CLONE_DIRTY_AFTER_PROBES")
    verdict = (
        "TWO_KILLED"
        if all(item["verdict"] == "MUTATION_KILLED" for item in cases)
        else "NOT_ACCREDITED"
    )
    summary = {
        "revision_sha": sha,
        "verdict": verdict,
        "baseline_required": "three existing G5 worker tests PASS before mutation",
        "scope": "G5 worker publication after expired lease / failure state recording",
        "mechanism": "in-memory patch per new Python process, no source edits",
        "cases": cases,
        "limitations": [
            "No OS-level sandbox, Docker, real Tectonic or scientific corpus.",
            "Compiler/renderer are fakes; real worker method and SQLite lease.",
            "Only two mutations, not comprehensive G5 worker coverage.",
            "Git before/after cannot detect all ephemeral external side effects.",
        ],
    }
    (reports / "g5_worker_mutation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"G5_WORKER_MUTATION_VERDICT={verdict}")
    for item in cases:
        print(f"{item['mutation']}={item['verdict']}; log={item['log']}")
    return 0 if verdict == "TWO_KILLED" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"G5_WORKER_MUTATION_STOP: {exc}", file=sys.stderr)
        raise SystemExit(3)
