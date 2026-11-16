#!/usr/bin/env python3
"""B01/B02 sensitivity probes on an isolated clone. Never edits source or GT.

Invoke only through run_b05_focal_isolated.ps1 -CheckB01B02Sensitivity
after a green four-nodeid baseline. Each injection runs in its own Python
process. A failed test alone does not suffice: contract-specific assertion
markers must appear with exactly one pytest FAILED, not an infrastructure error.
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
    "parser_text_loss": {
        "nodeid": "tests/integration/test_golden_parser.py::"
                  "test_production_parser_preserves_known_text_from_disposable_pdf",
        "marker": "B01_KNOWN_SOURCE_TEXT_MISSING",
    },
    "chunk_source_byte_loss": {
        "nodeid": "tests/integration/test_chunker_snapshot.py::"
                  "test_semantic_chunker_preserves_members_policy_and_source_exactly",
        "marker": "B02_SOURCE_BYTES_MISMATCH",
    },
}

CHILD = r'''
import sys
from dataclasses import replace
from unittest.mock import patch
import pytest

case, nodeid = sys.argv[1:]
if case == "parser_text_loss":
    from infra.adapters.pdf_parser import PdfParserAdapter

    original_parse = PdfParserAdapter.parse
    def drop_known_line(self, path):
        nodes = original_parse(self, path)
        altered = []
        for node in nodes:
            content = node.text_content or ""
            if "B01 Beta independent observation." in content:
                # Keep the first paragraph intact. Remove only the second
                # independently known statement from the real parser output.
                payload = node.payload.model_copy(update={
                    "content": content.replace("B01 Beta independent observation.", "")
                })
                altered.append(node.model_copy(update={"payload": payload}))
            else:
                altered.append(node)
        return altered

    with patch.object(PdfParserAdapter, "parse", new=drop_known_line):
        code = pytest.main([
            "-q", "-ra", "--tb=short", "--no-header",
            "-o", "addopts=", "-p", "no:cacheprovider", nodeid,
        ])

elif case == "chunk_source_byte_loss":
    # After collection pytest owns item.module. Patch only that module's
    # imported SUT entrypoint during the selected test, never a source file.
    class MutateChunkResult:
        def pytest_runtest_setup(self, item):
            if item.nodeid != nodeid:
                return
            original = item.module.build_semantic_chunks_as_units

            def damaged_units(*args, **kwargs):
                units, report = original(*args, **kwargs)
                if units and units[0].members:
                    first = units[0]
                    member = first.members[0]
                    if "Alpha  text." in member.source_text:
                        damaged = replace(member, source_text=member.source_text.replace(
                            "Alpha  text.", "Alpha text."
                        ))
                        units = [replace(first, members=(damaged, *first.members[1:])), *units[1:]]
                return units, report

            self.patcher = patch.object(
                item.module, "build_semantic_chunks_as_units", new=damaged_units
            )
            self.patcher.start()

        def pytest_runtest_teardown(self, item, nextitem):
            if getattr(self, "patcher", None) is not None:
                self.patcher.stop()
                self.patcher = None

    code = pytest.main([
        "-q", "-ra", "--tb=short", "--no-header",
        "-o", "addopts=", "-p", "no:cacheprovider", nodeid,
    ], plugins=[MutateChunkResult()])
else:
    raise SystemExit(100)
raise SystemExit(code)
'''


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    )
    if proc.returncode:
        raise RuntimeError(f"GIT_INSPECTION_FAILED: {args[0]}")
    return proc.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, required=True)
    args = parser.parse_args()

    if os.environ.get("TST_STAB_B01B02_OPT_IN") != "1":
        raise RuntimeError("OPT_IN_REQUIRED")
    root = Path.cwd().resolve()
    reports = args.reports.resolve()
    if not (root / ".git").is_dir() or not (root / "pyproject.toml").is_file():
        raise RuntimeError("INDEPENDENT_CHECKOUT_REQUIRED")
    if root == reports or root in reports.parents or not reports.is_dir():
        raise RuntimeError("REPORTS_MUST_BE_OUTSIDE_CHECKOUT")
    if git("remote"):
        raise RuntimeError("CLONE_HAS_REMOTE")
    if subprocess.run(
        ["git", "symbolic-ref", "-q", "HEAD"],
        cwd=root, capture_output=True, check=False
    ).returncode == 0:
        raise RuntimeError("DETACHED_CHECKOUT_REQUIRED")
    if git("status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("CLONE_DIRTY_BEFORE_MUTATIONS")
    sha = git("rev-parse", "HEAD")
    if re.fullmatch(r"[0-9a-f]{40}", sha) is None:
        raise RuntimeError("INVALID_GIT_REVISION")

    results = []
    for name, spec in CASES.items():
        child = subprocess.run(
            [sys.executable, "-B", "-c", CHILD, name, spec["nodeid"]],
            cwd=root, env=os.environ.copy(), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8",
            errors="replace", timeout=120, check=False,
        )
        log_name = f"b01b02_mutation_{name}.log"
        (reports / log_name).write_text(child.stdout, encoding="utf-8")
        killed = (
            child.returncode == 1
            and re.search(r"\b1 failed\b", child.stdout) is not None
            and "AssertionError" in child.stdout
            and spec["marker"] in child.stdout
            and "ERROR collecting" not in child.stdout
            and "INTERNALERROR" not in child.stdout
        )
        results.append({
            "mutation": name,
            "nodeid": spec["nodeid"],
            "expected_marker": spec["marker"],
            "exit_code": child.returncode,
            "verdict": "MUTATION_KILLED" if killed else "NOT_ACCREDITED",
            "log": log_name,
        })
    if git("status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("CLONE_DIRTY_AFTER_MUTATIONS")

    verdict = (
        "TWO_KILLED"
        if all(case["verdict"] == "MUTATION_KILLED" for case in results)
        else "NOT_ACCREDITED"
    )
    record = {
        "revision_sha": sha,
        "verdict": verdict,
        "scope": "B01 synthetic PDF parser / B02 synthetic semantic chunk contract",
        "mechanism": "in-memory SUT mutation in fresh subprocesses, not file edits",
        "cases": results,
        "limitations": [
            "Requires separate green baseline of four focal nodeids.",
            "Two targeted mutations do not prove general mutation coverage.",
            "No scientific corpus, production PDF-to-PDF, Docker, or OS sandbox.",
        ],
    }
    (reports / "b01b02_mutation_summary.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"B01B02_MUTATION_VERDICT={verdict}")
    for case in results:
        print(f"{case['mutation']}={case['verdict']}; log={case['log']}")
    return 0 if verdict == "TWO_KILLED" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"B01B02_MUTATION_STOP: {exc}", file=sys.stderr)
        raise SystemExit(3)
