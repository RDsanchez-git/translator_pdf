#!/usr/bin/env python3
"""Read-only reconciliation of A-01 pytest --collect-only JSON evidence.

Inputs: manifest.json, all.json, unit.json, integration_nonregression.json,
technical.json created by collect_a01_isolated.py. The optional repository root
is used to read source files and the tracked CI configuration, never to import
or execute tests. No output files are created or modified.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys
import tokenize
from typing import Any


SELECTORS: dict[str, str | None] = {
    "all": None,
    "unit": "unit",
    "integration_nonregression": "integration and not regression",
    "technical": "not e2e",
}
LEVEL_MARKERS = {"unit", "integration", "e2e", "regression", "smoke"}
RELEVANT_MARKERS = ("unit", "integration", "regression", "e2e", "smoke", "skip", "skipif", "xfail")
PATH_PATTERN = re.compile(r"tests/(?:unit|integration|smoke)/test_[A-Za-z_0-9]+\.py|tests/test_[A-Za-z_0-9]+\.py")


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def parse_nodes(path: Path) -> list[dict[str, Any]]:
    doc = read_json(path)
    if not isinstance(doc, dict) or not isinstance(doc.get("items"), list):
        raise ValueError(f"{path.name} has no items array")
    result: list[dict[str, Any]] = []
    for i, row in enumerate(doc["items"]):
        if not isinstance(row, dict):
            raise ValueError(f"{path.name}, index {i} is not an object")
        nodeid = row.get("nodeid")
        marks = row.get("markers")
        if not isinstance(nodeid, str) or not nodeid or not isinstance(marks, list):
            raise ValueError(f"{path.name}, index {i} has invalid nodeid/markers")
        if any(not isinstance(m, str) for m in marks):
            raise ValueError(f"{path.name}, index {i} has invalid marker strings")
        result.append(row)
    return result


def function_declarations(path: Path) -> int | None:
    """Rough source reference; decorators/classes do not imply pytest selection."""
    try:
        with tokenize.open(path) as stream:  # UTF-8 BOM-compatible
            tree = ast.parse(stream.read(), filename=str(path))
    except (OSError, SyntaxError, UnicodeError):
        return None
    return sum(
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name.startswith("test_")
        for n in ast.walk(tree)
    )


def summarize(reports: Path, repo: Path | None, top: int) -> dict[str, Any]:
    manifest = read_json(reports / "manifest.json")
    if not isinstance(manifest, dict):
        raise ValueError("manifest.json must be an object")
    sha = manifest.get("revision_sha")
    if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{40}", sha) is None:
        raise ValueError("manifest lacks a valid pinned revision_sha")
    nodes = {name: parse_nodes(reports / f"{name}.json") for name in SELECTORS}
    for name, rows in nodes.items():
        if manifest.get("modes", {}).get(name, {}).get("exit_code") != 0:
            raise ValueError(f"{name}: collection exit code is not zero")
        if manifest["modes"][name].get("selected_nodes_reported") != len(rows):
            raise ValueError(f"{name}: manifest count differs from JSON")
    all_nodes = nodes["all"]
    all_map = {n["nodeid"]: n for n in all_nodes}
    all_ids = set(all_map)
    duplicates = {name: len(rows) - len({x["nodeid"] for x in rows}) for name, rows in nodes.items()}
    def marks(row: dict[str, Any]) -> set[str]:
        return set(row["markers"])
    expected = {
        "all": all_ids,
        "unit": {x["nodeid"] for x in all_nodes if "unit" in marks(x)},
        "integration_nonregression": {
            x["nodeid"] for x in all_nodes
            if "integration" in marks(x) and "regression" not in marks(x)
        },
        "technical": {x["nodeid"] for x in all_nodes if "e2e" not in marks(x)},
    }
    selections = {}
    for name, rows in nodes.items():
        observed = {row["nodeid"] for row in rows}
        selections[name] = {
            "selected": len(rows),
            "unique": len(observed),
            "missing_expected": len(expected[name] - observed),
            "unexpected": len(observed - expected[name]),
            "duplicates": duplicates[name],
        }
    marker_counts = {
        marker: sum(marker in marks(row) for row in all_nodes)
        for marker in RELEVANT_MARKERS
    }
    uncovered = [n for n in all_nodes if not (marks(n) & LEVEL_MARKERS)]
    by_file = Counter(n["nodeid"].split("::", 1)[0] for n in all_nodes)
    files = sorted(by_file, key=lambda p: (-by_file[p], p))
    file_breakdown: list[dict[str, Any]] = []
    for path in files:
        items = by_file[path]
        declared = function_declarations(repo / path) if repo is not None else None
        file_breakdown.append({
            "file": path,
            "nodes": items,
            "declared_functions": declared,
            "node_minus_declarations": (items - declared if declared is not None else None),
        })
    file_mismatches = sorted(
        (x for x in file_breakdown if x["node_minus_declarations"] not in (None, 0)),
        key=lambda x: (-abs(x["node_minus_declarations"]), x["file"]),
    )
    explicit_ci: list[dict[str, Any]] = []
    if repo is not None:
        workflow_path = repo / ".github" / "workflows" / "ci.yml"
        if workflow_path.is_file():
            ci_paths = sorted(set(PATH_PATTERN.findall(workflow_path.read_text(encoding="utf-8"))))
            explicit_ci = [{"file": p, "collected_nodes": by_file.get(p, 0)} for p in ci_paths]

    log_health: dict[str, Any] = {}
    for mode in SELECTORS:
        log_file = reports / f"{mode}.log"
        if log_file.exists():
            content = log_file.read_text(encoding="utf-8", errors="replace")
            log_health[mode] = {
                "collection_error_lines": len(re.findall(r"(?m)^ERROR collecting\b", content)),
                "warnings_summary_sections": len(re.findall(r"(?mi)^\s*warnings summary\s*$", content)),
                "pytest_collection_warning_mentions": content.count("PytestCollectionWarning"),
            }
        else:
            log_health[mode] = {"missing_log": True}

    return {
        "revision_sha": sha,
        "assessment": "COLLECTION_ONLY; NO TEST EXECUTION; NO SCIENTIFIC CERTIFICATION",
        "total_nodes": len(all_nodes),
        "unique_nodeids": len(all_ids),
        "with_parameter_id": sum(n.get("parameter_id") is not None for n in all_nodes),
        "without_level_marker": len(uncovered),
        "marker_counts": marker_counts,
        "selections": selections,
        "declared_skipif_nodes": [
            {"nodeid": n["nodeid"], "markers": sorted(marks(n))}
            for n in all_nodes if "skipif" in marks(n)
        ],
        "files_with_collected_nodes": len(by_file),
        "top_files_by_collected_nodes": file_breakdown[:top],
        "files_with_nonzero_source_node_difference": len(file_mismatches) if repo else None,
        "top_declaration_node_differences": file_mismatches[:top],
        "explicit_ci_paths": explicit_ci,
        "logs": log_health,
        "warnings": [
            "Source function counts are approximate: include nested functions and not only pytest-collectable definitions.",
            "parameter_id count is not the number of parametrization expansions.",
            "skipif marker existence does not reveal a runtime skip or test PASS.",
            "Clean Git status does not establish OS-level network/filesystem isolation.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, required=True, help="Path to A-01 collection reports directory")
    parser.add_argument("--repo-root", type=Path, help="Optional read-only source tree for per-file AST counts and CI paths")
    parser.add_argument("--top", type=int, default=12, help="Top N files (default 12)")
    args = parser.parse_args(argv)
    if args.top < 1 or args.top > 50:
        parser.error("--top must be between 1 and 50")
    try:
        result = summarize(
            args.reports.expanduser().resolve(),
            args.repo_root.expanduser().resolve() if args.repo_root is not None else None,
            args.top,
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"A01_READ_ONLY_RECONCILIATION_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
