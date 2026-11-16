#!/usr/bin/env python3
"""A03 C-02/C-07 focal sensitivity: in-memory mutations on a detached Git clone.

Called only by run_b05_focal_isolated.ps1 -CheckA03Sensitivity after the
39-case technical baseline passes. Never writes source, runtime, fixtures,
scientific corpus, snapshots, or Git state. No Docker or real providers.
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
    "g3_utf8_byte_limit": {
        "nodeid": (
            "tests/integration/test_g3_b3_structured_result_contract.py::"
            "test_response_limit_is_utf8_bytes_not_character_count"
        ),
        "required_error": "Failed: DID NOT RAISE",
    },
    "parser_dropped_source": {
        "nodeid": (
            "tests/integration/test_verification_pipeline_connection.py::"
            "TestVerificationPipelineConnection::"
            "test_pipeline_extracts_nonempty_ast_from_text_pdf"
        ),
        "required_error": "B02_EXTRACTED_SOURCE_TEXT_MISSING",
    },
}

CHILD = r'''
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

if case == "g3_utf8_byte_limit":
    from core.chunking import result_contract as rc

    original = rc.parse_chunk_response
    real_limit = rc._MAX_RESPONSE_BYTES

    def incorrect_character_limited_parse(plan, chunk_id, raw_json):
        # Regression: invalidly judge the limit by characters rather than
        # actual UTF-8 bytes. Use the real parser for every other contract.
        if (
            isinstance(raw_json, str)
            and len(raw_json) <= real_limit
            and len(raw_json.encode("utf-8")) > real_limit
        ):
            with patch.object(rc, "_MAX_RESPONSE_BYTES", len(raw_json.encode("utf-8"))):
                return original(plan, chunk_id, raw_json)
        return original(plan, chunk_id, raw_json)

    with patch.object(
        rc, "parse_chunk_response", new=incorrect_character_limited_parse
    ):
        code = pytest.main(args)

elif case == "parser_dropped_source":
    from infra.adapters.pdf_parser import PdfParserAdapter

    original = PdfParserAdapter.parse
    missing = "Scientific observations must remain traceable."

    def discard_one_known_line(self, file_path):
        actual = original(self, file_path)
        edited = []
        for node in actual:
            content = node.text_content or ""
            if missing in content:
                new_content = content.replace(missing, "")
                payload = node.payload.model_copy(update={"content": new_content})
                edited.append(node.model_copy(update={"payload": payload}))
            else:
                edited.append(node)
        return edited

    with patch.object(PdfParserAdapter, "parse", new=discard_one_known_line):
        code = pytest.main(args)

else:
    raise SystemExit(100)
raise SystemExit(code)
'''


def inspect_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=25, check=False,
    )
    if result.returncode:
        raise RuntimeError(f"GIT_INSPECTION_FAILED: {' '.join(args)}")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("TST_STAB_A03_OPT_IN") != "1":
        raise RuntimeError("OPT_IN_REQUIRED")

    root = Path.cwd().resolve()
    reports = args.reports.resolve()
    if not (root / ".git").is_dir() or not (root / "pyproject.toml").is_file():
        raise RuntimeError("DETACHED_GIT_CLONE_REQUIRED")
    if reports == root or root in reports.parents or not reports.is_dir():
        raise RuntimeError("REPORTS_MUST_BE_OUTSIDE_CLONE")
    if inspect_git(root, "remote"):
        raise RuntimeError("CLONE_MUST_HAVE_NO_REMOTES")
    if subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "-q", "HEAD"],
        capture_output=True, check=False,
    ).returncode == 0:
        raise RuntimeError("DETACHED_HEAD_REQUIRED")
    if inspect_git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("CLONE_DIRTY_BEFORE_MUTATION")
    revision = inspect_git(root, "rev-parse", "HEAD")
    if re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise RuntimeError("INVALID_GIT_SHA")

    results = []
    for name, spec in CASES.items():
        child = subprocess.run(
            [sys.executable, "-B", "-c", CHILD, name, spec["nodeid"],
             str(reports.parent / "temp")],
            cwd=root, env=os.environ.copy(), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8",
            errors="replace", timeout=120, check=False,
        )
        log_name = f"a03_mutation_{name}.log"
        (reports / log_name).write_text(child.stdout, encoding="utf-8")
        killed = (
            child.returncode == 1
            and re.search(r"\b1 failed\b", child.stdout) is not None
            and spec["required_error"] in child.stdout
            and "ERROR collecting" not in child.stdout
            and "INTERNALERROR" not in child.stdout
        )
        results.append({
            "mutation": name,
            "nodeid": spec["nodeid"],
            "expected_failure": spec["required_error"],
            "python_exit_code": child.returncode,
            "verdict": "MUTATION_KILLED" if killed else "NOT_ACCREDITED",
            "log": log_name,
        })

    if inspect_git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"):
        raise RuntimeError("CLONE_DIRTY_AFTER_MUTATIONS")

    verdict = (
        "TWO_KILLED"
        if all(row["verdict"] == "MUTATION_KILLED" for row in results)
        else "NOT_ACCREDITED"
    )
    summary = {
        "revision_sha": revision,
        "verdict": verdict,
        "baseline_required": "A03 39 selected nodeids PASS before any mutation",
        "scope": "G3-B3 UTF-8 byte cap and PDF->AST preservation of known text",
        "mechanism": "in-memory SUT patch per fresh Python process",
        "cases": results,
        "limits": [
            "No OS-level sandbox, Docker, real provider or scientific GT.",
            "Only two targeted mutants; not comprehensive mutation coverage.",
            "Git pre/post checks cannot detect ephemeral external I/O.",
        ],
    }
    (reports / "a03_mutation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"A03_MUTATION_VERDICT={verdict}")
    for item in results:
        print(f"{item['mutation']}={item['verdict']}; log={item['log']}")
    return 0 if verdict == "TWO_KILLED" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"A03_MUTATION_STOP: {exc}", file=sys.stderr)
        raise SystemExit(3)
