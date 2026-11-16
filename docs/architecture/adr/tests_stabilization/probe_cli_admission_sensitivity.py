#!/usr/bin/env python3
"""Opt-in CLI admission/root mutation controls in detached isolated Git clone.

The runner must first pass all eight existing test_pdf_inbox_submission.py tests.
Both mutations patch a production-facing function in memory in a fresh Python
process; no source, GT, CI, fixture, snapshot or runtime file is changed.
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
    "cli_nonatomic_pdf_fallback": {
        "nodeid": (
            "tests/integration/test_pdf_inbox_submission.py::"
            "test_no_nonatomic_fallback_if_hard_links_unavailable"
        ),
        "marker": "DID NOT RAISE",
    },
    "cli_legacy_r1_invocation": {
        "nodeid": (
            "tests/integration/test_pdf_inbox_submission.py::"
            "test_cli_translate_never_invokes_legacy_r1_pipeline"
        ),
        "marker": "R1 must not execute",
    },
}

CHILD = r'''
import hashlib
import shutil
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

case, nodeid, temp_base = sys.argv[1:]
args = [
    "-q", "-ra", "--tb=short", "--no-header", "-o", "addopts=",
    "-p", "no:cacheprovider", "--basetemp", str(Path(temp_base) / case),
    nodeid,
]

if case == "cli_nonatomic_pdf_fallback":
    from apps.cli import pdf_inbox as inbox

    original = inbox.submit_pdf_to_inbox

    def non_atomic_fallback(source, inbox_dir):
        try:
            return original(source, inbox_dir)
        except inbox.PDFInboxSubmissionError as exc:
            if "PDF_INBOX_ATOMIC_PUBLISH_UNAVAILABLE" not in str(exc):
                raise
            # Regression: accepting non-atomic publication after hardlink
            # failure would expose an incomplete final PDF in the inbox.
            source = Path(source)
            inbox_dir = Path(inbox_dir)
            target = inbox_dir / (hashlib.sha256(source.read_bytes()).hexdigest() + ".pdf")
            shutil.copyfile(source, target)
            return inbox.PDFInboxSubmission(target.stem, target, False)

    with patch.object(inbox, "submit_pdf_to_inbox", new=non_atomic_fallback):
        result = pytest.main(args)

elif case == "cli_legacy_r1_invocation":
    from apps.cli import main as cli

    original = cli.handle_translate

    def wrong_route(args):
        # Regression: admission unexpectedly invokes the R1 legacy handler.
        # The test replaces it with an observable forbidden-call sentinel.
        cli.handle_translate_async(args)
        return original(args)

    with patch.object(cli, "handle_translate", new=wrong_route):
        result = pytest.main(args)
else:
    raise SystemExit(100)
raise SystemExit(result)
'''


def git(root: Path, *args: str) -> str:
    run = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=25, check=False,
    )
    if run.returncode:
        raise RuntimeError(f"INSPECTION_FAILED: git {' '.join(args)}")
    return run.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reports", type=Path, required=True)
    args = ap.parse_args()
    if os.environ.get("TST_STAB_CLI_ADMISSION_OPT_IN") != "1":
        raise RuntimeError("OPT_IN_REQUIRED")

    root = Path.cwd().resolve()
    reports = args.reports.resolve()
    if not (root / ".git").is_dir() or not (root / "pyproject.toml").is_file():
        raise RuntimeError("DETACHED_GIT_CHECKOUT_REQUIRED")
    if reports == root or root in reports.parents or not reports.is_dir():
        raise RuntimeError("REPORTS_MUST_BE_OUTSIDE_GIT_CLONE")
    if git(root, "remote"):
        raise RuntimeError("CLONE_MUST_HAVE_NO_REMOTE")
    if subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "-q", "HEAD"],
        capture_output=True, check=False,
    ).returncode == 0:
        raise RuntimeError("DETACHED_HEAD_REQUIRED")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("DIRTY_CLONE_BEFORE_PROBES")
    sha = git(root, "rev-parse", "HEAD")
    if not re.fullmatch("[0-9a-f]{40}", sha):
        raise RuntimeError("INVALID_SHA")

    results = []
    for key, spec in CASES.items():
        p = subprocess.run(
            [sys.executable, "-B", "-c", CHILD, key, spec["nodeid"],
             str(reports.parent / "temp")],
            cwd=root, env=os.environ.copy(), capture_output=True,
            text=True, encoding="utf-8", errors="replace",
            timeout=120, check=False,
        )
        output = p.stdout + ("\n--- STDERR ---\n" + p.stderr if p.stderr else "")
        log = f"cli_admission_mutation_{key}.log"
        (reports / log).write_text(output, encoding="utf-8")
        killed = (
            p.returncode == 1
            and re.search(r"\b1 failed\b", output) is not None
            and spec["marker"] in output
            and ("AssertionError" in output or "Failed:" in output)
            and "ERROR collecting" not in output
            and "INTERNALERROR" not in output
        )
        results.append({
            "mutation": key,
            "nodeid": spec["nodeid"],
            "expected_marker": spec["marker"],
            "exit_code": p.returncode,
            "verdict": "MUTATION_KILLED" if killed else "NOT_ACCREDITED",
            "log": log,
        })

    if git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("DIRTY_CLONE_AFTER_PROBES")

    verdict = (
        "TWO_KILLED"
        if all(x["verdict"] == "MUTATION_KILLED" for x in results)
        else "NOT_ACCREDITED"
    )
    summary = {
        "revision_sha": sha,
        "verdict": verdict,
        "baseline_required": "8 existing PDF inbox / CLI tests PASS first",
        "scope": "atomic inbox publication and CLI R1 exclusion",
        "cases": results,
        "limitations": [
            "No OS-level sandbox, provider, scientific corpus, or PDF-to-PDF E2E.",
            "Only two isolated mutants, not complete coverage.",
            "Git cleanliness observes persistent clone files only.",
        ],
    }
    (reports / "cli_admission_mutation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    print(f"CLI_ADMISSION_VERDICT={verdict}")
    for item in results:
        print(f"{item['mutation']}={item['verdict']}; log={item['log']}")
    return 0 if verdict == "TWO_KILLED" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"CLI_ADMISSION_PROBE_STOP: {exc}", file=sys.stderr)
        raise SystemExit(3)
