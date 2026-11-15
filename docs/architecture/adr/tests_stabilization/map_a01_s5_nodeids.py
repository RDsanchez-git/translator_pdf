#!/usr/bin/env python3
"""Inventory of A01-S5 nodeids linked to documented witness FILES (not approved contracts).

Reads frozen pytest collection JSON and TR-001..TR-035 Markdown tables.
No pytest, dynamic imports of tests, network calls, PDF processing or writes.
The output intentionally does NOT assign contract truth or "trusted" to nodeids.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

FROZEN_COLLECTION_SHA = "86cd68672ee692f073b62869e7c9bd177e8d9e3b"
DOCS = (
    "A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md",
    "A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md",
)
ROW_RE = re.compile(r"^\| \*\*TR-(\d{3})\*\*", re.MULTILINE)
LINK_RE = re.compile(r"\]\(\.\./\.\./\.\./\.\./(tests/(?:unit|integration|smoke)/[^)#?]+\.py)\)")
# Rows that explicitly say "mismo archivo" or otherwise omit their own path.
SAME_FILE_AS = {
    "TR-002": "TR-001",
    "TR-007": "TR-006",
    "TR-010": "TR-009",
    "TR-014": "TR-013",
    "TR-015": "TR-013",
}
KNOWN_SOURCE_DEFECTS = {
    "tests/integration/test_golden_parser.py": "ORACULO_AUTORREFERENTE_PARSER_MOCK",
    "tests/integration/test_chunker_snapshot.py": "AUTOGENERACION_SNAPSHOT_Y_ASERCIONES_PARCIALES",
    "tests/integration/test_real_parser_pipeline.py": "NOMBRE_PARSER_REAL_CON_PARSE_SIMULADO",
    "tests/integration/test_real_e2e.py": "NOMBRE_E2E_CON_PIPELINE_EXECUTE_SIMULADO",
}
# The last two are *scope/name mismatches*, not evidence of no utility.
EXPECTED_TOTAL = 1474


def git_read_only(root: Path, *args: str) -> str:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, check=False, timeout=20,
    )
    if completed.returncode:
        raise ValueError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def verify_tests_unchanged(root: Path) -> str:
    head = git_read_only(root, "rev-parse", "HEAD")
    if not re.fullmatch(r"[a-f0-9]{40}", head):
        raise ValueError("Invalid repository HEAD")
    checks = (
        ("committed", ("diff", "--name-only", FROZEN_COLLECTION_SHA, "HEAD", "--", "tests")),
        ("worktree", ("diff", "--name-only", "--", "tests")),
        ("staged", ("diff", "--cached", "--name-only", "--", "tests")),
    )
    for stage, command in checks:
        changed = git_read_only(root, *command)
        if changed:
            raise ValueError(
                f"tests/ changed relative to frozen collection ({stage}): "
                + changed.replace("\n", ", ")[:400]
            )
    return head


def read_contract_file_mapping(folder: Path) -> dict[str, list[str]]:
    explicit: dict[str, list[str]] = {}
    for filename in DOCS:
        doc = (folder / filename).read_text(encoding="utf-8")
        for row in doc.splitlines():
            match = ROW_RE.match(row)
            if match is None:
                continue
            key = "TR-" + match.group(1)
            if key in explicit:
                raise ValueError(f"Duplicate contract ID in docs: {key}")
            paths = sorted(set(LINK_RE.findall(row)))
            explicit[key] = paths
    expected = {f"TR-{i:03d}" for i in range(1, 36)}
    if set(explicit) != expected:
        raise ValueError(f"Missing/extraneous TR entries: {sorted(expected ^ set(explicit))}")
    for key, parent in SAME_FILE_AS.items():
        if explicit[key]:
            raise ValueError(f"Expected same-file ref without path: {key}")
        if not explicit[parent]:
            raise ValueError(f"Parent TR ref has no path: {parent}")
        explicit[key] = explicit[parent]
    empty = [key for key, paths in explicit.items() if not paths]
    if empty:
        raise ValueError(f"TR file associations unresolved: {empty}")
    return explicit


def analyze(root: Path, reports: Path, top: int) -> dict[str, Any]:
    manifest = json.loads((reports / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("revision_sha") != FROZEN_COLLECTION_SHA:
        raise ValueError("Manifest SHA differs from frozen collection: do not merge data")
    if manifest.get("modes", {}).get("all", {}).get("exit_code") != 0:
        raise ValueError("all collection failed; cannot map cases")
    report = json.loads((reports / "all.json").read_text(encoding="utf-8"))
    items = report.get("items")
    if not isinstance(items, list) or len(items) != EXPECTED_TOTAL:
        raise ValueError(f"all.json must contain {EXPECTED_TOTAL} collected nodeids")
    if manifest["modes"]["all"].get("selected_nodes_reported") != len(items):
        raise ValueError("all.json and manifest node counts differ")
    ids = [item.get("nodeid") for item in items]
    if any(not isinstance(v, str) or "::" not in v for v in ids):
        raise ValueError("Malformed collection nodeid")
    if len(set(ids)) != EXPECTED_TOTAL:
        raise ValueError("Duplicate nodeids in collection")
    head = verify_tests_unchanged(root)
    folder = root / "docs/architecture/adr/tests_stabilization"
    catalog = read_contract_file_mapping(folder)

    file_to_trs: dict[str, list[str]] = defaultdict(list)
    for tr, paths in sorted(catalog.items()):
        for path in paths:
            if not (root / path).is_file():
                raise ValueError(f"TR ref path not found: {tr} {path}")
            file_to_trs[path].append(tr)
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        path = item["nodeid"].split("::", 1)[0]
        by_file[path].append(item)
    missing = sorted(set(file_to_trs) - set(by_file))
    if missing:
        raise ValueError(f"Documented witness files not collected: {missing}")

    with_refs = sum(len(by_file[p]) for p in file_to_trs)
    no_refs = len(items) - with_refs
    markerless = lambda row: not (
        set(row.get("markers", [])) & {"unit", "integration", "e2e", "regression", "smoke"}
    )
    groups = {
        "witness_file_only_not_nodeid_reviewed": [i for i in items if i["nodeid"].split("::", 1)[0] in file_to_trs],
        "file_not_yet_documented_in_35_TRs": [i for i in items if i["nodeid"].split("::", 1)[0] not in file_to_trs],
    }
    rows = [
        {
            "file": p,
            "nodeids": len(by_file[p]),
            "without_level_marker": sum(markerless(i) for i in by_file[p]),
            "candidate_TRs_FILE_SCOPE_ONLY": sorted(file_to_trs[p]),
            "semantic_nodeid_verified": 0,
        }
        for p in file_to_trs
    ]
    rows.sort(key=lambda x: (-x["nodeids"], x["file"]))
    uncovered = [
        {
            "file": p,
            "nodeids": len(v),
            "without_level_marker": sum(markerless(i) for i in v),
            "status": "PENDING_REVIEW_NO_TR_FILE_EVIDENCE",
        }
        for p, v in by_file.items() if p not in file_to_trs
    ]
    uncovered.sort(key=lambda x: (-x["nodeids"], x["file"]))
    alerts = [
        {
            "file": p,
            "nodeids": len(by_file.get(p, [])),
            "verified_by_source_inspection": True,
            "issue": problem,
            "scope": "STATIC_TEST_QUALITY_FINDING_NOT_A_TEST_RESULT",
        }
        for p, problem in KNOWN_SOURCE_DEFECTS.items()
    ]
    if any(a["nodeids"] == 0 for a in alerts):
        raise ValueError("Known alert file not collected: review source/collection mismatch")
    checks = {
        "all_unique": len(set(ids)) == len(ids),
        "partitions_add_to_all": with_refs + no_refs == len(items),
        "group_partition_adds_to_all": sum(map(len, groups.values())) == len(items),
        "all_35_TR_mapped_to_existing_files": len(catalog) == 35,
        "no_tests_changed_from_collection": True,
    }
    if not all(checks.values()):
        raise ValueError(f"Failed reconciliation: {checks}")
    return {
        "collection_sha": FROZEN_COLLECTION_SHA,
        "current_head": head,
        "mode": "READ_ONLY_FILE_WITNESS_BRIDGE_NO_TEST_EXECUTION",
        "source_verification": "git diff SHA..HEAD, worktree and index under tests/: no changes",
        "test_execution": "NOT_PERFORMED",
        "test_nodeids_total": len(items),
        "test_nodeids_unique": len(set(ids)),
        "documented_contract_fichas": len(catalog),
        "distinct_documented_witness_files": len(file_to_trs),
        "nodeids_in_documented_witness_FILES_not_semantically_verified": with_refs,
        "nodeids_in_other_FILES_pending_review": no_refs,
        "without_level_marker_total": sum(markerless(i) for i in items),
        "semantic_nodeids_individually_accredited": 0,
        "by_group": {
            group: {"nodeids": len(v), "without_level_marker": sum(markerless(i) for i in v)}
            for group, v in groups.items()
        },
        "files_with_TR_refs_top": rows[:top],
        "files_without_TR_refs_top": uncovered[:top],
        "files_without_TR_refs_total": len(uncovered),
        "source_confirmed_quality_alerts": alerts,
        "checks": checks,
        "limitations": [
            "TR links are FILE-level candidates, NOT independent oracles per pytest nodeid.",
            "Counts do not prove tests are relevant, correct, executed, or mutation-sensitive.",
            "Unmapped tests include potentially valid technical, scientific, historical and legacy suites; none is presumed defective.",
            "The four source alerts are prior static-review findings, not runtime PASS/FAIL measurements.",
            "A clean tests/ diff does not prove imports had no effects outside Git or on ignored files.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--top", type=int, default=18, help="Top file counts, 1..100")
    args = parser.parse_args(argv)
    if not 1 <= args.top <= 100:
        parser.error("--top must be in 1..100")
    try:
        result = analyze(args.repo_root.resolve(), args.reports.resolve(), args.top)
    except (OSError, KeyError, TypeError, ValueError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"A01_S5_READ_ONLY_MAPPING_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
