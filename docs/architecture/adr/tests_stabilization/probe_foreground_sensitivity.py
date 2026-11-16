#!/usr/bin/env python3
"""Foreground fail-closed sensitivity probes in an independent detached clone.

Invocation is opt-in through the PowerShell focal runner after a green baseline.
The SUT is apps.cli.pdf_product.run_admitted_pdf with fake stage boundaries.
All mutations occur in memory in separate Python processes; no runtime,
fixture, corpus, CI or Ground Truth file is edited.
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
    "foreground_incomplete_g3": {
        "nodeid": (
            "tests/integration/test_b03_foreground_pdf_product.py::"
            "test_foreground_fails_on_incomplete_g3_before_g5"
        ),
        "expected": "DID NOT RAISE",
    },
    "foreground_missing_pdf": {
        "nodeid": (
            "tests/integration/test_b03_foreground_pdf_product.py::"
            "test_foreground_fails_when_g5_did_not_publish"
        ),
        "expected": "DID NOT RAISE",
    },
}

CHILD = r'''
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from apps.cli import pdf_product as product

case, nodeid, temp_base = sys.argv[1:]
pytest_args = [
    "-q", "-ra", "--tb=short", "--no-header", "-o", "addopts=",
    "-p", "no:cacheprovider", "--basetemp", str(Path(temp_base) / case),
    nodeid,
]

if case == "foreground_incomplete_g3":
    original = product._require_state

    def accept_incomplete_stage(document_id, expected):
        # Regression: erroneously report READY_FOR_ASSEMBLY after G3 has left
        # the actual FSM in PROCESSING. The real coordinator then calls G5,
        # contrary to the existing fail-closed contract.
        if expected == "READY_FOR_ASSEMBLY":
            current = product._read_status(document_id)
            if current is not None and current.current_state == "PROCESSING":
                return SimpleNamespace(
                    current_state="READY_FOR_ASSEMBLY",
                    ast_hash=current.ast_hash,
                )
        return original(document_id, expected)

    with patch.object(product, "_require_state", new=accept_incomplete_stage):
        result = pytest.main(pytest_args)

elif case == "foreground_missing_pdf":
    original = product._verify_published_pdf

    def permit_missing_pdf(root, document_id, ast_hash):
        # Regression: falsely report operational COMPLETED even if G5 did not
        # publish the required artifact. Keep the actual output path absent.
        output = Path(root) / "output" / f"translated_{document_id}.pdf"
        if not output.exists():
            return product.PDFProductResult(
                document_id=document_id, ast_hash=ast_hash, output_pdf=output,
            )
        return original(root, document_id, ast_hash)

    with patch.object(product, "_verify_published_pdf", new=permit_missing_pdf):
        result = pytest.main(pytest_args)

else:
    raise SystemExit(100)
raise SystemExit(result)
'''


def git(root: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True,
        text=True, encoding="utf-8", errors="replace",
        timeout=25, check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(f"GIT_CHECK_FAILED: {' '.join(args)}")
    return p.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reports", required=True, type=Path)
    args = ap.parse_args()

    if os.environ.get("TST_STAB_FOREGROUND_OPT_IN") != "1":
        raise RuntimeError("OPT_IN_REQUIRED")
    root = Path.cwd().resolve()
    reports = args.reports.resolve()
    if not (root / ".git").is_dir() or not (root / "pyproject.toml").is_file():
        raise RuntimeError("INDEPENDENT_GIT_CLONE_REQUIRED")
    if reports == root or root in reports.parents or not reports.is_dir():
        raise RuntimeError("REPORTS_MUST_BE_OUTSIDE_CLONE")
    if git(root, "remote"):
        raise RuntimeError("CLONE_HAS_GIT_REMOTE")
    if subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "-q", "HEAD"],
        capture_output=True, check=False,
    ).returncode == 0:
        raise RuntimeError("DETACHED_HEAD_REQUIRED")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("CLONE_DIRTY_BEFORE_PROBES")

    sha = git(root, "rev-parse", "HEAD")
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise RuntimeError("INVALID_SHA")
    results = []
    for name, spec in CASES.items():
        p = subprocess.run(
            [sys.executable, "-B", "-c", CHILD, name, spec["nodeid"],
             str(reports.parent / "temp")],
            cwd=root, env=os.environ.copy(), capture_output=True,
            text=True, encoding="utf-8", errors="replace",
            timeout=120, check=False,
        )
        out = p.stdout + ("\n--- STDERR ---\n" + p.stderr if p.stderr else "")
        logfile = f"foreground_mutation_{name}.log"
        (reports / logfile).write_text(out, encoding="utf-8")
        killed = (
            p.returncode == 1
            and re.search(r"\b1 failed\b", out) is not None
            and "Failed: DID NOT RAISE" in out
            and "ERROR collecting" not in out
            and "INTERNALERROR" not in out
        )
        results.append({
            "mutation": name,
            "nodeid": spec["nodeid"],
            "exit_code": p.returncode,
            "verdict": "MUTATION_KILLED" if killed else "NOT_ACCREDITED",
            "log": logfile,
        })
    if git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("CLONE_DIRTY_AFTER_PROBES")
    verdict = (
        "TWO_KILLED" if all(row["verdict"] == "MUTATION_KILLED" for row in results)
        else "NOT_ACCREDITED"
    )
    report = {
        "revision_sha": sha,
        "verdict": verdict,
        "baseline_required": "two named foreground coordinator tests PASS first",
        "scope": "foreground G3 incomplete and G5 missing publication",
        "cases": results,
        "limits": [
            "Stages OCR/G3/G5 are fakes; coordinator SUT is real.",
            "No real daemon/renderer, no PDF-to-PDF E2E or science evaluation.",
            "No OS-level sandbox; Git check excludes only persistent clone changes.",
            "Two specific mutations do not prove exhaustive coverage.",
        ],
    }
    (reports / "foreground_mutation_summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(f"FOREGROUND_MUTATION_VERDICT={verdict}")
    for case in results:
        print(f"{case['mutation']}={case['verdict']}; log={case['log']}")
    return 0 if verdict == "TWO_KILLED" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"FOREGROUND_MUTATION_STOP: {exc}", file=sys.stderr)
        raise SystemExit(3)
