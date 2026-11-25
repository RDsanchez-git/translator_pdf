"""Read-only post-recovery F18-05 R4–R9/R12 report over an isolated queue snapshot.

Usage: python -m tools.pppr_effect_report --queue-copy PATH --jsonl PATH
       --document-id SHA --ast-hash SHA --start-ns N --end-ns N

Use a separately verified, quiescent copy (including any required WAL), never
the retained original or a live database. SQLite read-only opens can still
touch sidecars. Input logs must cover one document/generation and interval.
No provider, runtime, network, migration, write authority or billing inference.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import sqlite3
from typing import Iterable

from core.finops.effect_observation import (
    RECEIPT_WINDOW, SDK_ENTRY, AttemptKey, build_effect_report,
)


from core.finops.cost_observation import SDK_RESPONSE, observe_attempt_cost


def _digest(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def report_from_snapshot(
    conn: sqlite3.Connection,
    lines: Iterable[str],
    *,
    document_id: str,
    ast_hash: str,
    start_ns: int,
    end_ns: int,
    scope: str,
    capture_complete: bool = False,
) -> dict[str, object]:
    """Correlate recorded events with checked local evidence, never dispatch.

    The selected generation's entire admission population must fit the window;
    a partial historical population is rejected rather than counted as complete.
    Checksums establish local integrity, not provider authenticity. A caller
    must establish snapshot provenance and capture coverage independently.
    """
    if not _digest(document_id) or not _digest(ast_hash):
        raise ValueError("PPPR_EFFECT_INVALID_DOCUMENT_IDENTITY")
    if type(start_ns) is not int or type(end_ns) is not int or start_ns >= end_ns:
        raise ValueError("PPPR_EFFECT_INVALID_OBSERVATION_SCOPE")
    if conn.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
        raise ValueError("PPPR_EFFECT_SNAPSHOT_INTEGRITY_FAILED")
    plans = conn.execute(
        "SELECT manifest_sha256 FROM chunk_plans WHERE document_id=? AND ast_hash=?",
        (document_id, ast_hash),
    ).fetchall()
    if len(plans) != 1 or not _digest(plans[0][0]):
        raise ValueError("PPPR_EFFECT_PLAN_REQUIRED")
    admissions: dict[AttemptKey, str] = {}
    chunk_ids: dict[AttemptKey, str] = {}
    decisions: dict[AttemptKey, dict[str, object]] = {}
    for task, execution, generation, payload, digest, created, chunk in conn.execute(
        "SELECT a.task_id,a.execution_id,a.generation_sha256,a.decision_json,"
        "a.decision_sha256,a.created_at,t.node_id "
        "FROM g3_admission_decisions a JOIN chunk_tasks t ON a.task_id=t.task_id "
        "WHERE t.document_id=? AND t.ast_hash=? AND t.worker_type='LLM'",
        (document_id, ast_hash),
    ):
        if (not isinstance(task, str) or not task or not isinstance(execution, str) or not execution
                or not isinstance(chunk, str) or not chunk or not _digest(generation)
                or not isinstance(payload, str)
                or sha256((generation + payload).encode("utf-8")).hexdigest() != digest):
            raise ValueError("PPPR_EFFECT_ADMISSION_CHECKSUM_OR_IDENTITY")
        decision = json.loads(payload)
        if (not isinstance(decision, dict) or decision.get("contract") != "PPPR_G3_ADMISSION_V1"
                or not _digest(decision.get("request_sha256"))
                or json.dumps(decision, sort_keys=True, ensure_ascii=False,
                              separators=(",", ":")) != payload):
            raise ValueError("PPPR_EFFECT_ADMISSION_PAYLOAD_INVALID")
        if (type(created) not in (int, float) or not math.isfinite(created)
                or not start_ns <= int(created * 1_000_000_000) <= end_ns):
            raise ValueError("PPPR_EFFECT_ADMISSION_OUTSIDE_SCOPE")
        key = (task, execution)
        if key in admissions:
            raise ValueError("PPPR_EFFECT_ADMISSION_DUPLICATE")
        admissions[key] = generation
        chunk_ids[key] = chunk
        decisions[key] = decision
    # Corroborate measured intervals with existing receipt identities. A
    # receipt alone supplies no elapsed time, and an admission alone supplies
    # no result. Do not attempt to reconstruct/repair an incomplete plan.
    receipts: set[AttemptKey] = set()
    for task, execution, generation, raw, digest in conn.execute(
        "SELECT task_id,execution_id,generation_sha256,raw_response,response_sha256 "
        "FROM chunk_result_receipts WHERE document_id=? AND ast_hash=? AND raw_response IS NOT NULL",
        (document_id, ast_hash),
    ):
        key = (task, execution)
        if (key not in admissions or admissions[key] != generation
                or not isinstance(raw, str) or sha256(raw.encode("utf-8")).hexdigest() != digest):
            raise ValueError("PPPR_EFFECT_RECEIPT_CORRELATION_FAILED")
        receipts.add(key)

    events: list[dict[str, object]] = []
    responses: dict[AttemptKey, list[dict[str, object]]] = {}
    sdk_counts: dict[AttemptKey, int] = {}
    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError as exc:
            # Permit ordinary non-JSON log lines, but never silently drop a
            # malformed observation (which could hide a repetition).
            if SDK_ENTRY in line or RECEIPT_WINDOW in line or SDK_RESPONSE in line:
                raise ValueError("PPPR_EFFECT_OBSERVATION_LOG_MALFORMED") from exc
            if capture_complete:
                raise ValueError("PPPR_EFFECT_COMPLETE_CAPTURE_REQUIRES_JSONL") from exc
            continue
        if not isinstance(event, dict) or event.get("message") not in (SDK_ENTRY, RECEIPT_WINDOW, SDK_RESPONSE):
            continue
        task, execution = event.get("task_id"), event.get("execution_id")
        if not isinstance(task, str) or not isinstance(execution, str):
            raise ValueError("PPPR_EFFECT_INVALID_EVENT_IDENTITY")
        key = (task, execution)
        if key not in admissions:
            raise ValueError("PPPR_EFFECT_EVENT_OUTSIDE_SCOPE")
        if event["message"] in (SDK_ENTRY, SDK_RESPONSE) and event.get("chunk_id") != chunk_ids[key]:
            raise ValueError("PPPR_EFFECT_EVENT_CHUNK_MISMATCH")
        if (event["message"] == RECEIPT_WINDOW and event.get("classification") == "MEASURED"
                and key not in receipts):
            raise ValueError("PPPR_EFFECT_MEASURED_WINDOW_WITHOUT_RECEIPT")
        if event["message"] == SDK_RESPONSE:
            stamp = event.get("observed_at_ns")
            if type(stamp) is not int or not start_ns <= stamp <= end_ns:
                raise ValueError("PPPR_EFFECT_EVENT_OUTSIDE_SCOPE")
            if event in responses.get(key, []):
                raise ValueError("PPPR_COST_DUPLICATE_RESPONSE_EVENT")
            responses.setdefault(key, []).append(event)
        else:
            if event["message"] == SDK_ENTRY:
                sdk_counts[key] = sdk_counts.get(key, 0) + 1
            events.append(event)
    report = build_effect_report(
        admissions, events, start_ns=start_ns, end_ns=end_ns, scope=scope,
        capture_complete=capture_complete,
    )
    report["document_id"] = document_id
    report["ast_hash"] = ast_hash
    report["manifest_sha256"] = plans[0][0]
    report["local_receipt_count"] = len(receipts)
    report["external_evidence_scope"] = "NO_PROVIDER_EVIDENCE_ADAPTER"
    report["cost_observations"] = [
        {
            "task_id": key[0], "execution_id": key[1], "generation_sha256": admissions[key],
            **observe_attempt_cost(
                decisions[key], responses.get(key, []),
                sdk_entries=sdk_counts.get(key, 0), capture_complete=capture_complete,
            ),
        }
        for key in sorted(admissions)
    ]
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue-copy", type=Path, required=True,
                        help="Isolated verified snapshot, never live/original queue")
    parser.add_argument("--jsonl", type=Path, required=True)
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--ast-hash", required=True)
    parser.add_argument("--start-ns", type=int, required=True)
    parser.add_argument("--end-ns", type=int, required=True)
    parser.add_argument("--capture-complete", action="store_true",
                        help="Explicit operator attestation of complete scoped JSONL capture")
    args = parser.parse_args(argv)
    if not args.queue_copy.is_file() or args.queue_copy.is_symlink():
        parser.error("Queue snapshot must be an existing regular file")
    if not args.jsonl.is_file() or args.jsonl.is_symlink():
        parser.error("JSONL capture must be an existing regular file")
    with closing(sqlite3.connect(args.queue_copy.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
        conn.execute("PRAGMA query_only=ON")
        with args.jsonl.open(encoding="utf-8") as lines:
            report = report_from_snapshot(
                conn, lines, document_id=args.document_id, ast_hash=args.ast_hash,
                start_ns=args.start_ns, end_ns=args.end_ns, scope="LOCAL_POST_RECOVERY_SNAPSHOT",
                capture_complete=args.capture_complete,
            )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
