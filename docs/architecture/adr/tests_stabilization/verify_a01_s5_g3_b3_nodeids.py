#!/usr/bin/env python3
"""Verify collected G3-B3 nodeids against 12 source functions / 33 variants.

Read-only; does NOT import tests, run pytest, write files, or mutate git.
Prints each real nodeid + parameter_id exactly as recorded in all.json.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import sys
import tokenize

FROZEN_SHA = "86cd68672ee692f073b62869e7c9bd177e8d9e3b"
TARGET = "tests/integration/test_g3_b3_structured_result_contract.py"
EXPECTED = {
    "test_two_nodes_one_chunk_response_order_is_identity_based_not_positional": 1,
    "test_fragments_across_chunks_reassemble_without_added_delimiters": 1,
    "test_preserve_is_bypassed_and_partial_remains_explicit": 1,
    "test_only_preserve_nodes_materialize_without_provider_results": 1,
    "test_invalid_member_responses_fail_closed": 17,
    "test_invalid_json_is_rejected": 6,
    "test_unknown_chunk_rejected_before_payload_parse": 1,
    "test_incomplete_or_extra_chunks_never_return_partial_nodes": 1,
    "test_source_boundary_whitespace_preserved_through_segmented_translation": 1,
    "test_whitespace_only_source_never_silently_disappears_in_translation": 1,
    "test_response_size_bound_rejects_uncontrolled_payload": 1,
    "test_translated_unicode_surrogates_rejected_before_projection": 1,
}


def verify(reports: Path, repo: Path) -> dict[str, object]:
    manifest = json.loads((reports / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("revision_sha") != FROZEN_SHA:
        raise ValueError("Collection SHA changed: do not compare different revisions")
    if manifest.get("modes", {}).get("all", {}).get("exit_code") != 0:
        raise ValueError("Collection all exit was not zero")
    raw = json.loads((reports / "all.json").read_text(encoding="utf-8"))
    items = raw.get("items")
    if not isinstance(items, list) or len(items) != 1474:
        raise ValueError("Unexpected all.json item count")
    if manifest["modes"]["all"].get("selected_nodes_reported") != len(items):
        raise ValueError("Collection manifest count mismatch")
    with tokenize.open(repo / TARGET) as stream:
        source = ast.parse(stream.read(), filename=TARGET)
    functions = {
        node.name for node in source.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }
    if functions != set(EXPECTED):
        raise ValueError("Source functions differ from the audited 12-function inventory")
    selected = []
    for item in items:
        nodeid = item.get("nodeid")
        if not isinstance(nodeid, str):
            raise ValueError("Non-string nodeid")
        if not nodeid.startswith(TARGET + "::"):
            continue
        tail = nodeid.removeprefix(TARGET + "::")
        name = tail.split("[", 1)[0]
        if name not in EXPECTED:
            raise ValueError(f"Unexpected function or class nodeid: {nodeid}")
        selected.append({
            "nodeid": nodeid,
            "function": name,
            "parameter_id": item.get("parameter_id"),
        })
    if len(selected) != 33:
        raise ValueError(f"Expected 33 G3-B3 collected items, got {len(selected)}")
    if len({item["nodeid"] for item in selected}) != len(selected):
        raise ValueError("G3-B3 nodeids duplicated")
    count = Counter(item["function"] for item in selected)
    if count != EXPECTED:
        raise ValueError(f"Function cardinalities differ: {dict(count)}")
    for item in selected:
        expected_parametrized = EXPECTED[item["function"]] > 1
        # A parametrized nodeid has a [<param id>] suffix; plain nodes do not.
        if ("[" in item["nodeid"]) != expected_parametrized:
            raise ValueError(f"Unexpected parameter suffix: {item['nodeid']}")
    return {
        "collection_sha": FROZEN_SHA,
        "target": TARGET,
        "mode": "READ_ONLY_NO_TEST_EXECUTION",
        "source_functions": len(functions),
        "collected_nodeids": len(selected),
        "unique_nodeids": len(set(item["nodeid"] for item in selected)),
        "standalone_functions": 10,
        "parametrized_member_mutations": count["test_invalid_member_responses_fail_closed"],
        "parametrized_invalid_json": count["test_invalid_json_is_rejected"],
        "source_and_collection_cardinality_match": True,
        "nodeids_exactly_as_collected": selected,
        "caveat": (
            "This verifies identities and cardinalities, not pytest execution, "
            "oracle independence, mutation kills, or scenario order."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--reports", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.reports.resolve(), args.repo_root.resolve())
    except (OSError, ValueError, SyntaxError, UnicodeError, KeyError, TypeError) as error:
        print(f"A01_S5_G3_B3_NODEID_ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
