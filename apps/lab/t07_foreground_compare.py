"""C3/T07 foreground witness: compare the SAME C2 source in isolated workspace.

Reuses the pinned B03.2 offline launcher and image; zero new named volumes,
no builds/pulls/network. Temporary host cache (~43 MB) and SQLite are removed
on every exit. Does not touch C2 state or start competing daemons.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from apps.lab import offline_pdf_lab as lab

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = (
    "-p", "tpdfconvconv1211b",
    "-f", "docker-compose.yml",
    "-f", "docker-compose.runtime.yml",
    "-f", "docker-compose.convergence-lab.yml",
)
C2_SOURCE_IN_CONTAINER = (
    "/app/data/c2_auto_fixtures/c2_auto_7bde7a829408de26521dc0d5.pdf"
)
SOURCE_SHA = "28a53af840244e4022afb08eb800e6348a866b957779e5b5753215afbc158d0f"
AST_SHA = "b0b4cb12ea5e2a871a8789e5228e428b10eca04380e5a95503ff4f61c89f9c4a"
MANIFEST_SHA = "7724718fd66aff7b570f70a1dad828b2d3391abd14c47ef32fd12fb4a487229d"
UNITS = {
    "isolated_0001_1_c1126087": "preserve",
    "chunk_0002_2_4_fdbea9ce": "translate",
}


class T07Blocked(RuntimeError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise T07Blocked("T07_BLOCKED:" + reason)


def docker(args: list[str], *, capture=True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["docker", *args], cwd=ROOT, text=True, capture_output=capture,
        check=False, timeout=60,
    )
    if result.returncode:
        raise T07Blocked(
            "T07_DOCKER_COMMAND_FAILED:" + " ".join(args[-3:]) +
            " " + (result.stderr or "")[-400:]
        )
    return result


def _verify_running_and_get_source_container() -> str:
    running = docker(["compose", *COMPOSE, "ps", "--status", "running", "--services"])
    require(
        sorted(running.stdout.splitlines()) ==
        ["assembler", "g3_fake", "llm_worker", "ocr_router"],
        "C2_DAEMON_SET_DRIFT",
    )
    container = docker(["compose", *COMPOSE, "ps", "-q", "ocr_router"])
    cid = container.stdout.strip()
    require(len(cid) >= 12 and "\n" not in cid, "OCR_CONTAINER_UNAVAILABLE")
    return cid


def _ro(path: Path):
    require(path.is_file() and not path.is_symlink(), "MISSING_DB:" + path.name)
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    db.execute("PRAGMA query_only=ON")
    return db


def _audit(workspace: Path, stdout: str) -> None:
    with closing(_ro(workspace / "state" / "fsm.db")) as fsm, \
            closing(_ro(workspace / "state" / "queue.db")) as queue, \
            closing(_ro(workspace / "state" / "materialized.db")) as mat:
        fsm_rows = fsm.execute(
            "SELECT ast_hash,current_state,state_version FROM document_fsm WHERE document_id=?",
            (SOURCE_SHA,),
        ).fetchall()
        require(fsm_rows == [(AST_SHA, "COMPLETED", 7)], "FSM_NOT_EQUIVALENT")

        rows = queue.execute(
            "SELECT manifest_json,manifest_sha256 FROM chunk_plans "
            "WHERE document_id=? AND ast_hash=?",
            (SOURCE_SHA, AST_SHA),
        ).fetchall()
        require(len(rows) == 1 and rows[0][1] == MANIFEST_SHA, "PLAN_HASH_DRIFT")
        units = {
            unit["chunk_id"]: unit["chunk_type"]
            for unit in json.loads(rows[0][0])["units"]
        }
        require(units == UNITS, "PLAN_UNIT_DRIFT")

        tasks = queue.execute(
            "SELECT worker_type,node_id,task_state FROM chunk_tasks "
            "WHERE document_id=? AND ast_hash=? ORDER BY worker_type,node_id",
            (SOURCE_SHA, AST_SHA),
        ).fetchall()
        require(
            tasks == [
                ("ASSEMBLER", "ROOT_ASSEMBLY", "COMPLETED"),
                ("LLM", "chunk_0002_2_4_fdbea9ce", "COMPLETED"),
                ("LLM", "isolated_0001_1_c1126087", "COMPLETED"),
            ], "TASK_DRIFT",
        )

        receipts = queue.execute(
            "SELECT chunk_id, raw_response IS NULL FROM chunk_result_receipts "
            "WHERE document_id=? AND ast_hash=? ORDER BY chunk_id",
            (SOURCE_SHA, AST_SHA),
        ).fetchall()
        require(receipts == [
            ("chunk_0002_2_4_fdbea9ce", 0),
            ("isolated_0001_1_c1126087", 1),
        ], "RECEIPTS_DRIFT")

        publication = mat.execute(
            "SELECT manifest_sha256,projection_version "
            "FROM g3_plan_publications WHERE document_id=? AND ast_hash=?",
            (SOURCE_SHA, AST_SHA),
        ).fetchall()
        require(publication == [(MANIFEST_SHA, 1)], "PUBLICATION_DRIFT")
        projections = mat.execute(
            "SELECT COUNT(*) FROM valid_chunks_cache "
            "WHERE document_id=? AND ast_hash=? AND projection_version=1",
            (SOURCE_SHA, AST_SHA),
        ).fetchone()[0]
        require(projections == 4, "PROJECTION_COUNT_DRIFT")

    events = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except (ValueError, TypeError):
            continue
        if isinstance(value, dict) and str(value.get("event", "")).startswith("G3_FAKE_"):
            events.append(value)
    counts = {
        kind: sum(e.get("event") == "G3_FAKE_" + kind for e in events)
        for kind in ("POST_ATTEMPT", "REQUEST_ACCEPTED", "REQUEST_REJECTED")
    }
    require(counts == {
        "POST_ATTEMPT": 1, "REQUEST_ACCEPTED": 1, "REQUEST_REJECTED": 0,
    }, "FAKE_HTTP_COUNT_DRIFT:" + str(counts))
    accepted = next(e for e in events if e["event"] == "G3_FAKE_REQUEST_ACCEPTED")
    require(
        (accepted.get("document_id"), accepted.get("ast_hash"),
         accepted.get("manifest_sha256"), accepted.get("chunk_id"), accepted.get("status"))
        == (SOURCE_SHA, AST_SHA, MANIFEST_SHA, "chunk_0002_2_4_fdbea9ce", 200),
        "FAKE_ACCEPTED_IDENTITY_DRIFT",
    )
    require(re.search(
        r"B032_VERIFIED_COMPLETE doc=" + SOURCE_SHA + r" ast=" +
        AST_SHA + r" requests=1\b", stdout,
    ) is not None, "FOREGROUND_COMPLETION_MARKER_MISSING")

    pdf_path = workspace / "output" / ("translated_" + SOURCE_SHA + ".pdf")
    require(pdf_path.is_file() and not pdf_path.is_symlink(), "OUTPUT_MISSING")
    pdf_bytes = pdf_path.read_bytes()
    require(len(pdf_bytes) > 1000 and pdf_bytes.startswith(b"%PDF-"), "PDF_INVALID")
    import pymupdf
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        require(len(pdf) == 1 and bool(pdf[0].get_text().strip()), "PDF_STRUCTURE_INVALID")

    print("T07_SOURCE_SHA:", SOURCE_SHA, flush=True)
    print("T07_AST_SHA:", AST_SHA, flush=True)
    print("T07_MANIFEST_SHA:", MANIFEST_SHA, flush=True)
    print("T07_UNIT_TYPES:", units, flush=True)
    print("T07_TASKS: 3 COMPLETED; RECEIPTS: 2; PUBLICATIONS: 1; PROJECTIONS: 4", flush=True)
    print("T07_HTTP: 1 attempt / 1 TRANSLATE accepted / 0 rejected / 0 PRESERVE", flush=True)
    print("T07_PDF_BYTES:", len(pdf_bytes), flush=True)
    print("T07_PDF_SHA256:", hashlib.sha256(pdf_bytes).hexdigest(), flush=True)
    print("T07_FOREGROUND_CONTRACT_EQUIVALENCE_PASS", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="One-shot isolated T07 vs C2, auto-cleanup")
    parser.add_argument("--history-zip", type=Path, default=Path.home() / "Downloads" / lab.HISTORY_ZIP)
    args = parser.parse_args()

    require(Path.cwd().resolve() == ROOT, "RUN_FROM_REPO_ROOT")
    require(shutil.disk_usage(tempfile.gettempdir()).free > 256 * 1024**2,
            "FREE_DISK_BELOW_256_MIB")
    lab._check_checkout(ROOT)
    lab._check_history(args.history_zip)
    lab._docker_image_id()
    cid = _verify_running_and_get_source_container()

    with tempfile.TemporaryDirectory(prefix="tpdf_t07_") as scratch:
        workspace = Path(scratch)
        for name in ("data", "output", "state", "cache"):
            (workspace / name).mkdir()
        source = workspace / "source.pdf"
        docker(["cp", f"{cid}:{C2_SOURCE_IN_CONTAINER}", str(source)])
        require(source.stat().st_size == 1544 and lab._sha(source) == SOURCE_SHA,
                "C2_SOURCE_NOT_IDENTICAL")
        cache_counts = lab._seed_caches(args.history_zip, workspace)
        require(cache_counts == (294, 1), "CACHE_SEED_DRIFT")
        print("T07_SOURCE_REUSED_FROM_C2: True", flush=True)
        print("T07_TRANSIENT_CACHE_FILES: 294", flush=True)
        cmd = lab._container_command(ROOT, workspace, source=source)
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True,
                                timeout=240, check=False)
        if result.returncode:
            raise T07Blocked(
                f"T07_FOREGROUND_EXIT_{result.returncode}: " +
                (result.stdout + "\n" + result.stderr)[-2800:]
            )
        _audit(workspace, result.stdout)

    require(not workspace.exists(), "TEMP_WORKSPACE_NOT_REMOVED")
    print("T07_TEMP_WORKSPACE_CLEANUP_PASS", flush=True)
    print("C3_T07_FOREGROUND_ISOLATED_PASS", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (T07Blocked, OSError, RuntimeError, sqlite3.Error, subprocess.TimeoutExpired) as exc:
        print("T07_STOP:", exc, file=sys.stderr)
        raise SystemExit(1) from exc
