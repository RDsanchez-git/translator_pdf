#!/usr/bin/env python3
"""A01/A04: read-only comparison of two pinned pytest --collect-only inventories.

Consumes JSON reports from collect_a01_isolated.py. Never imports a test,
invokes pytest, modifies Git, updates a fixture or evaluates scientific GT.
Writes one JSON summary only to the NEW reports directory, outside a Git tree.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

OLD_SHA = "86cd68672ee692f073b62869e7c9bd177e8d9e3b"
MODES = ("all", "unit", "integration_nonregression", "technical")
LEVEL_MARKERS = {"unit", "integration", "e2e", "regression", "smoke"}
MARKERS = ("unit", "integration", "regression", "e2e", "smoke",
           "skip", "skipif", "xfail")
CI_FILE_PATTERN = re.compile(
    r"tests/(?:unit|integration|smoke)/test_[A-Za-z_0-9]+\.py"
    r"|tests/test_[A-Za-z_0-9]+\.py"
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, check=False, timeout=25,
        encoding="utf-8", errors="replace",
    )
    if proc.returncode:
        raise ValueError(f"Git inspection failed: {' '.join(args)}: "
                         f"{proc.stderr.strip()[:350]}")
    return proc.stdout.strip()


def inventory(folder: Path) -> dict[str, Any]:
    manifest = read_json(folder / "manifest.json")
    sha = manifest.get("revision_sha")
    if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise ValueError(f"{folder}: invalid revision_sha")
    if not manifest.get("collection_requested"):
        raise ValueError(f"{folder}: only prepared, no collection")
    items: dict[str, dict[str, dict[str, Any]]] = {}
    for mode in MODES:
        meta = manifest.get("modes", {}).get(mode, {})
        if meta.get("exit_code") != 0:
            raise ValueError(f"{folder}: {mode} not collected successfully")
        doc = read_json(folder / f"{mode}.json")
        raw = doc.get("items")
        if not isinstance(raw, list):
            raise ValueError(f"{folder}: invalid items in {mode}.json")
        mapped: dict[str, dict[str, Any]] = {}
        for idx, item in enumerate(raw):
            if not isinstance(item, dict):
                raise ValueError(f"{mode}.json row {idx} is not an object")
            node = item.get("nodeid")
            marks = item.get("markers")
            if (not isinstance(node, str) or not node.startswith("tests/")
                or not isinstance(marks, list)
                or not all(isinstance(m, str) for m in marks)):
                raise ValueError(f"{mode}.json row {idx}: invalid node or markers")
            if node in mapped:
                raise ValueError(f"{mode}.json has duplicate nodeid {node!r}")
            mapped[node] = item
        if meta.get("selected_nodes_reported") != len(raw) or doc.get("count") != len(raw):
            raise ValueError(f"{mode}: manifest or JSON count mismatch")
        items[mode] = mapped

    all_items = items["all"]
    expected: dict[str, set[str]] = {
        "all": set(all_items),
        "unit": {nid for nid, row in all_items.items()
                 if "unit" in row["markers"]},
        "integration_nonregression": {
            nid for nid, row in all_items.items()
            if "integration" in row["markers"] and "regression" not in row["markers"]
        },
        "technical": {
            nid for nid, row in all_items.items() if "e2e" not in row["markers"]
        },
    }
    for mode in MODES:
        if set(items[mode]) != expected[mode]:
            missing = sorted(expected[mode] - set(items[mode]))[:5]
            extra = sorted(set(items[mode]) - expected[mode])[:5]
            raise ValueError(f"{folder} {mode}: selector mismatch: "
                             f"missing={missing}, extra={extra}")
    return {"sha": sha, "items": items}


def counts(inv: dict[str, Any]) -> dict[str, Any]:
    all_rows = list(inv["items"]["all"].values())
    return {
        "modes": {mode: len(inv["items"][mode]) for mode in MODES},
        "markers": {
            mark: sum(mark in row["markers"] for row in all_rows)
            for mark in MARKERS
        },
        "without_level_marker": sum(
            not (set(row["markers"]) & LEVEL_MARKERS) for row in all_rows
        ),
        "parameterized_nodeids": sum(
            row.get("parameter_id") is not None for row in all_rows
        ),
        "files_with_nodes": len({
            row["nodeid"].split("::", 1)[0] for row in all_rows
        }),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-reports", required=True, type=Path)
    parser.add_argument("--new-reports", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()

    old_folder = args.old_reports.resolve()
    new_folder = args.new_reports.resolve()
    root = args.repo_root.resolve()
    if old_folder == new_folder:
        raise ValueError("Old and new reports must be distinct folders")
    for folder in (old_folder, new_folder):
        if not folder.is_dir():
            raise ValueError(f"Missing report directory: {folder}")
        if folder == root or root in folder.parents:
            raise ValueError("Report folders must be outside the owner's Git tree")
    if not (root / "pyproject.toml").is_file():
        raise ValueError("Repo root missing pyproject.toml")
    old = inventory(old_folder)
    new = inventory(new_folder)
    if old["sha"] != OLD_SHA:
        raise ValueError(f"Old collection must be frozen SHA {OLD_SHA}")
    if old["sha"] == new["sha"]:
        raise ValueError("Old and new SHA identical; HEAD was not recollected")
    actual_head = git(root, "rev-parse", "HEAD")
    if new["sha"] != actual_head:
        raise ValueError("Owner checkout HEAD and NEW report SHA differ")
    if subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor",
         old["sha"], new["sha"]],
        capture_output=True, check=False, timeout=25,
    ).returncode != 0:
        raise ValueError("Old collection SHA is not ancestor of new HEAD")
    old_map = old["items"]["all"]
    new_map = new["items"]["all"]
    old_ids, new_ids = set(old_map), set(new_map)
    removed, added = sorted(old_ids - new_ids), sorted(new_ids - old_ids)
    shared = old_ids & new_ids
    marker_changes = [
        {"nodeid": node, "old": old_map[node]["markers"],
         "new": new_map[node]["markers"]}
        for node in sorted(shared)
        if set(old_map[node]["markers"]) != set(new_map[node]["markers"])
    ]
    param_changes = [
        {"nodeid": node, "old": old_map[node].get("parameter_id"),
         "new": new_map[node].get("parameter_id")}
        for node in sorted(shared)
        if old_map[node].get("parameter_id") != new_map[node].get("parameter_id")
    ]

    by_file: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"removed": [], "added": []}
    )
    for node in removed:
        by_file[node.split("::", 1)[0]]["removed"].append(node)
    for node in added:
        by_file[node.split("::", 1)[0]]["added"].append(node)
    files_changed = [
        {"file": path, **entries,
         "renamed_candidate_only": (
             len(entries["removed"]) == len(entries["added"]) == 1
         )}
        for path, entries in sorted(by_file.items())
    ]

    workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    selectors = (
        'python -m pytest -m "unit"',
        'python -m pytest -m "integration and not regression"',
        'python -m pytest -m "not e2e"',
    )
    if not all(token in workflow for token in selectors):
        raise ValueError("CI selectors changed: review ci.yml before attributing selection")
    explicit = sorted(set(CI_FILE_PATTERN.findall(workflow)))
    old_file_counts = Counter(n.split("::", 1)[0] for n in old_ids)
    new_file_counts = Counter(n.split("::", 1)[0] for n in new_ids)
    explicit_ci = [
        {"file": path, "old_nodeids": old_file_counts[path],
         "new_nodeids": new_file_counts[path]}
        for path in explicit
    ]

    def suspicious_name(node: str) -> bool:
        return bool(re.search(r"(^|[/_:])e2e(?:[_:/]|$)", node, re.I))
    name_unmarked = sorted(
        node for node, row in new_map.items()
        if suspicious_name(node) and "e2e" not in row["markers"]
    )
    result = {
        "status": "A01_A04_COLLECTION_RECONCILIATION_ONLY",
        "old_sha": old["sha"],
        "new_sha": new["sha"],
        "old": counts(old),
        "new": counts(new),
        "identities": {
            "unchanged": len(shared),
            "removed": len(removed),
            "added": len(added),
            "marker_changes_same_nodeid": len(marker_changes),
            "parameter_id_changes_same_nodeid": len(param_changes),
            "net_change": len(new_ids) - len(old_ids),
        },
        "removed_nodeids": removed,
        "added_nodeids": added,
        "marker_changes": marker_changes,
        "parameter_id_changes": param_changes,
        "changed_files": files_changed,
        "ci": {
            "selectors_confirmed_in_workflow_source": list(selectors),
            "explicit_paths": explicit_ci,
            "explicit_paths_total": len(explicit),
            "explicit_paths_nodes_new_sum_not_deduplicated": sum(
                x["new_nodeids"] for x in explicit_ci
            ),
            "technical_nodeids_new": len(new["items"]["technical"]),
            "e2e_named_but_unmarked_candidates": name_unmarked,
            "workflow_execution_verified": False,
            "workflow_trigger_note": "No GitHub Actions run checked; source only.",
        },
        "limits": [
            "pytest --collect-only runs imports/hooks, NOT test bodies.",
            "A removed/added nodeid in the same file is only a rename candidate.",
            "CI selectors/paths are parsed statically, not CI PASS results.",
            "No SUT, semantic oracle, mutation or network isolation accreditation.",
            "Do not equate 1474 historical nodeids with the HEAD inventory.",
        ],
    }
    out = new_folder / "a01_head_reconciliation.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"A01_OLD_SHA={old['sha']}")
    print(f"A01_NEW_SHA={new['sha']}")
    print(f"A01_ALL_OLD={len(old_ids)}; A01_ALL_NEW={len(new_ids)}")
    print(f"A01_UNIT_NEW={len(new['items']['unit'])}")
    print(f"A01_TECHNICAL_NEW={len(new['items']['technical'])}")
    print(f"A01_REMOVED={len(removed)}; A01_ADDED={len(added)}; "
          f"A01_MARKER_CHANGES={len(marker_changes)}")
    print(f"A01_CI_EXPLICIT_PATHS={len(explicit)}")
    print(f"A01_E2E_NAMED_UNMARKED={len(name_unmarked)}")
    print("A01_COLLECTION_ONLY; TEST_BODIES_NOT_EXECUTED; CI_NOT_RUN")
    print(f"REPORT={out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"A01_A04_RECONCILIATION_BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(3)