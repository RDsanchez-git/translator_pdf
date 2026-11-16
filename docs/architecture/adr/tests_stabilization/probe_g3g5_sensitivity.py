#!/usr/bin/env python3
"""C03-C05: three opt-in, in-memory contract mutations in detached Git clone.

All mutations are transient and run in distinct Python subprocesses.
No source/GT/runtime/CI files are modified. First run the nine-nodeid
G3/G5 baseline; then use this helper via the isolated PowerShell runner.
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
    "c03_g3_unknown_retry": {
        "nodeid": "tests/integration/test_w06_g3_uncertain_effect_offline.py::"
                  "test_w06_lost_reply_is_quarantined_without_second_provider_call",
        "marker": "W06_UNSAFE_RETRY",
    },
    "c04_g3_projection_drift": {
        "nodeid": "tests/integration/test_g3_b4_3b_publication_recovery.py::"
                  "test_corrupt_projection_never_advances_fsm",
        "marker": "DID NOT RAISE",
    },
    "c05_g5_expired_lease_publish": {
        "nodeid": "tests/integration/test_g5_assembler_lease_recovery.py::"
                  "test_expired_lease_old_worker_cannot_publish_even_without_takeover",
        "marker": "G5_STALE_LEASE_PUBLISHED_PDF",
    },
}

CHILD = r'''
import sys
from unittest.mock import patch
import pytest

case, nodeid = sys.argv[1:]
options = ["-q", "-ra", "--tb=short", "--no-header",
           "-o", "addopts=", "-p", "no:cacheprovider", nodeid]

if case == "c03_g3_unknown_retry":
    from apps.llm_workers.sync_bridge import SyncProviderBridge

    real = SyncProviderBridge.execute_chunk
    def unsafe_retry(self, plan, unit):
        try:
            return real(self, plan, unit)
        except TimeoutError:
            # Regression: a timeout may mean the provider accepted the request.
            # An automatic retry causes the forbidden second accepted effect.
            return real(self, plan, unit)

    with patch.object(SyncProviderBridge, "execute_chunk", new=unsafe_retry):
        exit_code = pytest.main(options)

elif case == "c04_g3_projection_drift":
    # Regression: the durable projection verifier stops comparing persisted
    # node bytes. The selected test must fail because drift is accepted.
    with patch("infra.db.staged_publication._verify_rows", return_value=None):
        exit_code = pytest.main(options)

elif case == "c05_g5_expired_lease_publish":
    from infra.db.assembly_recovery import AssemblyLeaseRepository

    real = AssemblyLeaseRepository._has_authority
    def ignores_expiry(self, lease, now, phases=("ASSEMBLING", "READY_FOR_COMPILATION", "COMPILING")):
        # Regression: owner, generation and FSM remain checked, but positive
        # expired timestamps erroneously count as valid lease authority.
        return real(self, lease, 0.0, phases)

    with patch.object(AssemblyLeaseRepository, "_has_authority", new=ignores_expiry):
        exit_code = pytest.main(options)

else:
    raise SystemExit(100)
raise SystemExit(exit_code)
'''


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], capture_output=True,
                          text=True, check=False)
    if proc.returncode:
        raise RuntimeError(f"GIT_INSPECTION_FAILED: {args[0]}")
    return proc.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reports", type=Path, required=True)
    args = ap.parse_args()

    if os.environ.get("TST_STAB_G3G5_OPT_IN") != "1":
        raise RuntimeError("OPT_IN_REQUIRED")
    root = Path.cwd().resolve()
    reports = args.reports.resolve()
    if not (root / ".git").is_dir() or not (root / "pyproject.toml").is_file():
        raise RuntimeError("INDEPENDENT_GIT_CHECKOUT_REQUIRED")
    if root == reports or root in reports.parents or not reports.is_dir():
        raise RuntimeError("REPORTS_MUST_BE_OUTSIDE_CLONED_REPO")
    if git("remote"):
        raise RuntimeError("GIT_CLONE_HAS_REMOTE")
    if subprocess.run(["git", "symbolic-ref", "-q", "HEAD"],
                      cwd=root, capture_output=True, check=False).returncode == 0:
        raise RuntimeError("DETACHED_HEAD_REQUIRED")
    if git("status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("DIRTY_CLONE_BEFORE_MUTATION")
    revision = git("rev-parse", "HEAD")
    if re.fullmatch("[0-9a-f]{40}", revision) is None:
        raise RuntimeError("INVALID_REVISION")

    result_cases = []
    for case, spec in CASES.items():
        process = subprocess.run(
            [sys.executable, "-B", "-c", CHILD, case, spec["nodeid"]],
            cwd=root, env=os.environ.copy(), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8",
            errors="replace", timeout=120, check=False,
        )
        name = f"g3g5_mutation_{case}.log"
        (reports / name).write_text(process.stdout, encoding="utf-8")
        killed = (
            process.returncode == 1
            and re.search(r"\b1 failed\b", process.stdout) is not None
            and (("AssertionError" in process.stdout) or ("Failed:" in process.stdout))
            and spec["marker"] in process.stdout
            and "ERROR collecting" not in process.stdout
            and "INTERNALERROR" not in process.stdout
        )
        result_cases.append({
            "mutation": case,
            "nodeid": spec["nodeid"],
            "marker": spec["marker"],
            "exit_code": process.returncode,
            "verdict": "MUTATION_KILLED" if killed else "NOT_ACCREDITED",
            "log": name,
        })

    dirty = git("status", "--porcelain=v1", "--untracked-files=all", "--ignored")
    if dirty:
        raise RuntimeError("DIRTY_CLONE_AFTER_MUTATION")
    verdict = "THREE_KILLED" if all(
        x["verdict"] == "MUTATION_KILLED" for x in result_cases
    ) else "NOT_ACCREDITED"
    report = {
        "revision_sha": revision,
        "verdict": verdict,
        "scope": "Active G3 UNKNOWN, G3 projection verification, G5 stale lease publish",
        "baseline_required": "9 selected G3/G5 nodeids must pass first",
        "mechanism": "unittest.mock.patch on SUT methods, fresh Python process per mutation",
        "cases": result_cases,
        "limitations": [
            "No OS-level sandbox or real HTTP provider request.",
            "No full OCR/G3/G5 PDF-to-PDF lab, Tectonic or scientific corpus.",
            "Three mutants do not establish exhaustive protection.",
        ],
    }
    (reports / "g3g5_mutation_summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(f"G3G5_MUTATION_VERDICT={verdict}")
    for item in result_cases:
        print(f"{item['mutation']}={item['verdict']}; log={item['log']}")
    return 0 if verdict == "THREE_KILLED" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"G3G5_MUTATION_STOP: {exc}", file=sys.stderr)
        raise SystemExit(3)
