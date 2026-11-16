#!/usr/bin/env python3
"""B05 sensitivity: in-memory SUT mutations in isolated Python subprocesses.

Opt-in only from run_b05_focal_isolated.ps1. Never edits source files.
Two independent child processes; the baseline must already be green.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

TESTS = {
    "fsm_watchdog": (
        "tests/integration/test_recovery_flow.py::"
        "TestRecoveryAndResumeEndToEnd::test_complete_crash_recovery_and_resume_lifecycle",
        "AssertionError",
        "STALLED",
    ),
    "legacy_cache_read": (
        "tests/integration/test_e2e_walking_skeleton.py::"
        "TestLegacyDispatcherCache::test_legacy_cache_hit_observed_across_two_dispatches",
        "AssertionError",
        "Cache hit must avoid a second fake provider call",
    ),
}

CHILD = r"""
import sys
from unittest.mock import patch
import pytest

case, nodeid = sys.argv[1:]
if case == "fsm_watchdog":
    # Mutate SUT at its public method boundary: watchdog no longer stalls.
    with patch("runtime.recovery.AbandonedProcessWatchdog.execute_sweep", return_value=None):
        code = pytest.main(["-q", "-ra", "--tb=short", "--no-header",
                            "-o", "addopts=", "-p", "no:cacheprovider", nodeid])
elif case == "legacy_cache_read":
    async def always_miss(_self, _prompt_hash):
        return None
    # Mutate SUT at the cache read boundary; all provider calls now miss.
    with patch("apps.llm_workers.cache_provider.CachedLLMProvider._read_cache",
               new=always_miss):
        code = pytest.main(["-q", "-ra", "--tb=short", "--no-header",
                            "-o", "addopts=", "-p", "no:cacheprovider", nodeid])
else:
    raise SystemExit(100)
raise SystemExit(code)
"""


def checked_git(*args: str) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if proc.returncode:
        raise RuntimeError(f"git inspection failed: {args[0]}")
    return proc.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", required=True, type=Path)
    args = parser.parse_args()
    if os.getenv("TST_STAB_SENSITIVITY_OPT_IN") != "1":
        raise RuntimeError("OPT_IN_REQUIRED: use the -CheckSensitivity runner switch")
    root = Path.cwd().resolve()
    reports = args.reports.resolve()
    if not (root / ".git").is_dir() or not (root / "pyproject.toml").is_file():
        raise RuntimeError("INDEPENDENT_GIT_CHECKOUT_REQUIRED")
    if root == reports or root in reports.parents:
        raise RuntimeError("REPORTS_MUST_BE_OUTSIDE_CLONED_REPO")
    if checked_git("remote"):
        raise RuntimeError("CLONE_MUST_HAVE_NO_GIT_REMOTE")
    if checked_git("status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("CLONE_MUST_BE_CLEAN_BEFORE_MUTATION")
    if subprocess.run(["git", "symbolic-ref", "-q", "HEAD"],
                      capture_output=True, cwd=root, check=False).returncode == 0:
        raise RuntimeError("DETACHED_CHECKOUT_REQUIRED")
    head = checked_git("rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise RuntimeError("INVALID_HEAD")
    if not reports.is_dir():
        raise RuntimeError("REPORT_DIRECTORY_MISSING")

    results = []
    for name, (nodeid, expected_type, expected_text) in TESTS.items():
        proc = subprocess.run(
            [sys.executable, "-B", "-c", CHILD, name, nodeid],
            cwd=root,
            env=os.environ.copy(),
            text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=120, check=False,
        )
        log_path = reports / f"mutation_{name}.log"
        log_path.write_text(proc.stdout, encoding="utf-8")
        killed = (
            proc.returncode == 1
            and re.search(r"\b1 failed\b", proc.stdout) is not None
            and expected_type in proc.stdout
            and expected_text in proc.stdout
            and "ERROR collecting" not in proc.stdout
            and "INTERNALERROR" not in proc.stdout
        )
        results.append({
            "mutation": name,
            "target_nodeid": nodeid,
            "python_exit_code": proc.returncode,
            "verdict": "MUTATION_KILLED" if killed else "NOT_ACCREDITED",
            "log": log_path.name,
            "expected_assertion": expected_text,
        })
    if checked_git("status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("MUTATION_DIRTIED_GIT_CHECKOUT")
    verdict = "TWO_KILLED" if all(r["verdict"] == "MUTATION_KILLED" for r in results) else "NOT_ACCREDITED"
    record = {
        "revision_sha": head,
        "scope": "legacy FSM recovery and legacy cache only, NOT supported G3/G5",
        "mechanism": "unittest.mock.patch on SUT in subprocess, source files untouched",
        "baseline_required": "focal 4 PASS before entering mutation mode",
        "verdict": verdict,
        "cases": results,
        "limitations": [
            "Two injected contract violations are not exhaustive mutation coverage.",
            "This is not a full PDF-to-PDF E2E or a scientific test.",
            "A clone does not enforce OS-level filesystem/network security.",
        ],
    }
    (reports / "mutation_summary.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"B05_MUTATION_VERDICT={verdict}")
    for row in results:
        print(f"{row['mutation']}={row['verdict']}; log={row['log']}")
    return 0 if verdict == "TWO_KILLED" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"B05_MUTATION_STOP: {exc}", file=sys.stderr)
        raise SystemExit(3)
