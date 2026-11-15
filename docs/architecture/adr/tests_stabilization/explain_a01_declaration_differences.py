#!/usr/bin/env python3
"""Explain A-01 source-declaration vs pytest-node differences without running tests.

Reads the frozen pytest --collect-only all.json, manifest.json and Python ASTs.
Does not import source modules, invoke pytest, write files or change the repo.
A static decorator count is only a clue; collected node IDs are the evidence.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import tokenize
from typing import Any


def parameter_lengths(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[int | None]:
    lengths: list[int | None] = []
    for deco in node.decorator_list:
        if not isinstance(deco, ast.Call):
            continue
        target = deco.func
        if not (
            isinstance(target, ast.Attribute)
            and target.attr == "parametrize"
            and isinstance(target.value, ast.Attribute)
            and target.value.attr == "mark"
            and isinstance(target.value.value, ast.Name)
            and target.value.value.id == "pytest"
        ):
            continue
        if len(deco.args) < 2:
            lengths.append(None)
            continue
        data = deco.args[1]
        lengths.append(len(data.elts) if isinstance(data, (ast.List, ast.Tuple)) else None)
    return lengths


def source_functions(path: Path, rel: str) -> tuple[int, dict[str, dict[str, Any]], list[str]]:
    with tokenize.open(path) as stream:
        root = ast.parse(stream.read(), filename=rel)
    all_functions = [
        n for n in ast.walk(root)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")
    ]
    cases: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []

    def register(node: ast.FunctionDef | ast.AsyncFunctionDef, parents: list[str]) -> None:
        if not node.name.startswith("test_"):
            return
        key = "::".join([rel, *parents, node.name])
        if key in cases:
            duplicates.append(key)
        lengths = parameter_lengths(node)
        expected = None
        if lengths and all(x is not None for x in lengths):
            expected = 1
            for n in lengths:
                assert n is not None
                expected *= n
        cases[key] = {
            "line": node.lineno,
            "decorator_parametrize_lengths": lengths,
            "literal_decorator_expected_nodes": expected,
        }

    for node in root.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            register(node, [])
        elif isinstance(node, ast.ClassDef):
            # Class name is preserved even if it is not collectable by pytest.
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    register(member, [node.name])
    return len(all_functions), cases, duplicates


def base_nodeid(nodeid: str) -> str:
    # Pytest encodes parameter ids in a trailing [id] suffix.
    # Nodeid may carry class segments separated by ::.
    return nodeid.split("[", 1)[0]


def explain(reports: Path, repo: Path, show: int) -> dict[str, Any]:
    manifest = json.loads((reports / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("modes", {}).get("all", {}).get("exit_code") != 0:
        raise ValueError("The all-mode collection did not exit 0")
    raw = json.loads((reports / "all.json").read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("items"), list):
        raise ValueError("Missing all.json items")
    items = raw["items"]
    if manifest["modes"]["all"].get("selected_nodes_reported") != len(items):
        raise ValueError("Manifest and collection node counts disagree")
    file_nodes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        nodeid = item.get("nodeid")
        if not isinstance(nodeid, str) or "::" not in nodeid:
            raise ValueError(f"Unexpected nodeid in collection: {nodeid!r}")
        file_nodes[nodeid.split("::", 1)[0]].append(item)

    files = sorted(p for p in (repo / "tests").rglob("test_*.py") if p.is_file())
    differences: list[dict[str, Any]] = []
    totals = Counter()
    no_nodes: list[str] = []
    for source in files:
        rel = source.relative_to(repo).as_posix()
        declared, source_map, duplicate_keys = source_functions(source, rel)
        collected = file_nodes.get(rel, [])
        dynamic_count = len(collected)
        per_base = Counter(base_nodeid(x["nodeid"]) for x in collected)
        matched_bases = {key for key in source_map if per_base[key] > 0}
        extra_variants = sum(per_base[key] - 1 for key in matched_bases)
        noncollected_decl = declared - len(matched_bases)
        unknown_nodes = sum(n for base, n in per_base.items() if base not in source_map)
        arithmetic = extra_variants - noncollected_decl + unknown_nodes
        observed_delta = dynamic_count - declared
        expanded = []
        for key in sorted(matched_bases):
            observed = per_base[key]
            if observed < 2:
                continue
            detail = source_map[key]
            declared_expected = detail["literal_decorator_expected_nodes"]
            lengths = detail["decorator_parametrize_lengths"]
            expanded.append({
                "test": key.split("::")[-1],
                "line": detail["line"],
                "nodes": observed,
                "source_parametrize_lengths": lengths,
                "literal_decorator_expected_nodes": declared_expected,
                "decorator_count_matches": declared_expected == observed if declared_expected is not None else None,
            })
        expanded.sort(key=lambda x: (-x["nodes"], x["line"]))
        if not collected:
            no_nodes.append(rel)
        totals["declared"] += declared
        totals["collected"] += dynamic_count
        totals["extra_variants_from_matched_cases"] += extra_variants
        totals["source_declarations_not_collected"] += noncollected_decl
        totals["unmatched_collected_nodes"] += unknown_nodes
        if observed_delta != 0 or unknown_nodes or duplicate_keys:
            differences.append({
                "file": rel,
                "source_declarations": declared,
                "pytest_nodes": dynamic_count,
                "delta": observed_delta,
                "matched_source_tests": len(matched_bases),
                "extra_nodes_for_collected_tests": extra_variants,
                "source_declarations_not_collected": noncollected_decl,
                "nodes_without_matching_source_decl": unknown_nodes,
                "delta_reconciles_arithmetically": arithmetic == observed_delta,
                "duplicate_source_keys": duplicate_keys,
                "examples_expanded": expanded[:show],
                "expanded_cases_with_unknown_or_mismatched_decorators": sum(
                    x["decorator_count_matches"] is not True for x in expanded
                ),
            })
    differences.sort(key=lambda x: (-abs(x["delta"]), x["file"]))
    collected_source_set = {p.relative_to(repo).as_posix() for p in files}
    outside_sources = sorted(set(file_nodes) - collected_source_set)
    return {
        "revision_sha_in_collection": manifest.get("revision_sha"),
        "mode": "READ_ONLY_STATIC_AND_COLLECTION_RECONCILIATION",
        "pytest_execution": "NOT PERFORMED",
        "files_examined": len(files),
        "total_source_test_functions": totals["declared"],
        "total_collected_nodes": totals["collected"],
        "unmatched_source_files_in_collection": outside_sources,
        "files_with_zero_collected_nodes": no_nodes,
        "files_with_nonzero_delta_or_anomalies": len(differences),
        "identity": {
            "net_node_minus_declaration": totals["collected"] - totals["declared"],
            "extra_nodes_for_matched_collected_tests": totals["extra_variants_from_matched_cases"],
            "source_functions_not_collected": totals["source_declarations_not_collected"],
            "nodes_without_matching_source": totals["unmatched_collected_nodes"],
            "arithmetic_verified": (
                totals["collected"] - totals["declared"]
                == totals["extra_variants_from_matched_cases"]
                - totals["source_declarations_not_collected"]
                + totals["unmatched_collected_nodes"]
            ),
        },
        "differences": differences,
        "warnings": [
            "Collection expansion proves multiple node IDs, not independence or quality of assertions.",
            "Literal decorator lengths are a static clue, not a proof for dynamically constructed parameters.",
            "Source functions in nested scopes may be counted by AST but not collected by pytest.",
            "Files with zero nodes are included; they may be empty placeholders or manual scripts.",
            "Changes in tracked tests between collection SHA and source reading invalidate attribution.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--top-tests-per-file", type=int, default=3)
    args = parser.parse_args(argv)
    if not 1 <= args.top_tests_per_file <= 10:
        parser.error("--top-tests-per-file must be 1..10")
    try:
        result = explain(
            args.reports.expanduser().resolve(),
            args.repo_root.expanduser().resolve(),
            args.top_tests_per_file,
        )
    except (OSError, ValueError, SyntaxError, UnicodeError, KeyError, TypeError) as error:
        print(f"A01_DIFF_EXPLANATION_ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
