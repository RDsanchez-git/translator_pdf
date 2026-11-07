"""W08-2d read-only audit of an ALREADY FROZEN cross-plane state bundle.

This does not take a live backup, stop processes or authorize a cutover.
Only isolated SQLite copies with no WAL sidecars and AST JSON copies are accepted.
No production DB connection factory, provider, CLI or mutation is used.
"""
from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode
from core.chunking.manifest_contract import ChunkPlan
from core.execution.exceptions import PipelineIntegrityError


_DB_NAMES = ("queue.db", "fsm.db", "materialized.db", "event.db")


@dataclass(frozen=True, slots=True)
class FrozenBundleAudit:
    bundle_sha256: str
    generation_count: int
    pending_generations: int
    uncertain_generations: int
    receipt_only_generations: int
    published_generations: int
    orphan_fsm_generations: int


def _open_frozen(path: Path) -> sqlite3.Connection:
    if not path.is_file() or path.is_symlink():
        raise PipelineIntegrityError("W08_BUNDLE_REQUIRED_DB_MISSING")
    if any(Path(str(path) + suffix).exists() for suffix in ("-wal", "-shm", "-journal")):
        raise PipelineIntegrityError("W08_BUNDLE_UNCHECKPOINTED_SQLITE")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    connection.execute("PRAGMA query_only=ON")
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        if integrity != ("ok",):
            raise PipelineIntegrityError("W08_BUNDLE_SQLITE_INTEGRITY_FAILURE")
    except BaseException:
        connection.close()
        raise
    return connection


def _require_tables(conn: sqlite3.Connection, tables: tuple[str, ...]) -> None:
    actual = {
        name for (name,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if not set(tables).issubset(actual):
        raise PipelineIntegrityError("W08_BUNDLE_SCHEMA_MISSING")


def _ast_from_copy(directory: Path, document_id: str, ast_hash: str) -> list[ASTNode]:
    # Never allow generation strings to navigate out of an isolated bundle.
    if (not document_id or not ast_hash
            or any(c not in "0123456789abcdef" for c in document_id)
            or any(c not in "0123456789abcdef" for c in ast_hash)):
        raise PipelineIntegrityError("W08_BUNDLE_UNSAFE_GENERATION_ID")
    path = directory / "ast_cache" / f"{document_id}.{ast_hash}.ast.json"
    if not path.is_file() or path.is_symlink():
        raise PipelineIntegrityError("W08_BUNDLE_AST_COPY_MISSING")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(raw, dict)
            or raw.get("document_id") != document_id
            or raw.get("ast_hash") != ast_hash
            or not isinstance(raw.get("nodes"), list)):
        raise PipelineIntegrityError("W08_BUNDLE_AST_ENVELOPE_INVALID")
    ast = [ASTNode.model_validate(item) for item in raw["nodes"]]
    if not ast or compute_ast_hash(ast) != ast_hash:
        raise PipelineIntegrityError("W08_BUNDLE_AST_GENERATION_DRIFT")
    return ast


def audit_frozen_bundle(directory: Path) -> FrozenBundleAudit:
    """Fail closed on inconsistent generations. No mutations to source copies.

    Required: queue.db, fsm.db, materialized.db, ast_cache/. event.db is
    optional only if absent: if included, it must be a complete valid SQLite.
    An auditor cannot prove the files were captured at the same instant.
    """
    directory = directory.resolve(strict=True)
    if not directory.is_dir() or (directory / "ast_cache").is_symlink():
        raise PipelineIntegrityError("W08_BUNDLE_INVALID_DIRECTORY")
    with ExitStack() as stack:
        connections = {
            name: stack.enter_context(_closing_sqlite(_open_frozen(directory / name)))
            for name in _DB_NAMES[:3]
        }
        event = directory / "event.db"
        if event.exists():
            connections["event.db"] = stack.enter_context(
                _closing_sqlite(_open_frozen(event))
            )
        queue, fsm, material = (
            connections["queue.db"], connections["fsm.db"],
            connections["materialized.db"],
        )
        _require_tables(queue, ("chunk_plans", "chunk_tasks", "chunk_result_receipts", "system_leases"))
        _require_tables(fsm, ("document_fsm",))
        _require_tables(material, ("g3_plan_publications", "valid_chunks_cache"))
        if "event.db" in connections:
            _require_tables(connections["event.db"], ("chunk_events_log",))

        fsm_rows = {
            (document_id, ast_hash): state
            for document_id, ast_hash, state in fsm.execute(
                "SELECT document_id,ast_hash,current_state FROM document_fsm"
            )
        }
        plans = queue.execute(
            "SELECT document_id,ast_hash,manifest_sha256,manifest_json "
            "FROM chunk_plans ORDER BY document_id,ast_hash"
        ).fetchall()
        pending = uncertain = receipt_only = published = 0
        digests: list[dict[str, object]] = []
        plan_keys: set[tuple[str, str]] = set()
        for document_id, ast_hash, digest, manifest_json in plans:
            if not isinstance(document_id, str) or not isinstance(ast_hash, str):
                raise PipelineIntegrityError("W08_BUNDLE_GENERATION_INVALID")
            plan_keys.add((document_id, ast_hash))
            ast = _ast_from_copy(directory, document_id, ast_hash)
            plan = ChunkPlan.from_json(
                manifest_json, ast, document_id=document_id, ast_hash=ast_hash,
            )
            if digest != plan.digest:
                raise PipelineIntegrityError("W08_BUNDLE_MANIFEST_DRIFT")
            if (document_id, ast_hash) not in fsm_rows:
                raise PipelineIntegrityError("W08_BUNDLE_FSM_GENERATION_MISSING")
            tasks = queue.execute(
                "SELECT node_id,task_state,task_id,execution_id "
                "FROM chunk_tasks WHERE document_id=? AND ast_hash=? AND worker_type='LLM'",
                (document_id, ast_hash),
            ).fetchall()
            if len(tasks) != len(plan.units) or {t[0] for t in tasks} != {
                unit.chunk_id for unit in plan.units
            }:
                raise PipelineIntegrityError("W08_BUNDLE_TASK_COVERAGE")
            states = {t[1] for t in tasks}
            receipts = queue.execute(
                "SELECT chunk_id,task_id,execution_id FROM chunk_result_receipts "
                "WHERE document_id=? AND ast_hash=?",
                (document_id, ast_hash),
            ).fetchall()
            by_chunk = {row[0]: row for row in tasks}
            if len(receipts) != len({r[0] for r in receipts}):
                raise PipelineIntegrityError("W08_BUNDLE_RECEIPT_DUPLICATION")
            if any(
                chunk_id not in by_chunk
                or (by_chunk[chunk_id][2], by_chunk[chunk_id][3]) != (task_id, execution_id)
                or by_chunk[chunk_id][1] not in ("RESULT_STAGED", "COMPLETED")
                for chunk_id, task_id, execution_id in receipts
            ):
                raise PipelineIntegrityError("W08_BUNDLE_RECEIPT_BINDING")
            if states <= {"RESULT_STAGED", "COMPLETED"} and len(states) == 1:
                if len(receipts) != len(plan.units):
                    raise PipelineIntegrityError("W08_BUNDLE_RECEIPT_COVERAGE")
                receipt_only += 1
            elif any(state in {"RESULT_STAGED", "COMPLETED"} for state in states):
                # Partial states are not an authorisation for provider replay.
                pending += 1
            elif "G3_EXTERNAL_UNKNOWN" in states:
                uncertain += 1
            else:
                pending += 1
            if "G3_EXTERNAL_UNKNOWN" in states:
                uncertain += (0 if len(states) != 1 or "G3_EXTERNAL_UNKNOWN" in states and not states <= {"RESULT_STAGED", "COMPLETED"} and not any(s in {"RESULT_STAGED", "COMPLETED"} for s in states) else 1)
            publication = material.execute(
                "SELECT manifest_sha256,result_sha256 FROM g3_plan_publications "
                "WHERE document_id=? AND ast_hash=?",
                (document_id, ast_hash),
            ).fetchone()
            projections = material.execute(
                "SELECT node_id,content_hash,normalized_hash FROM valid_chunks_cache "
                "WHERE document_id=? AND ast_hash=? ORDER BY node_id",
                (document_id, ast_hash),
            ).fetchall()
            if publication is not None:
                if publication[0] != plan.digest or len(projections) != len(ast):
                    raise PipelineIntegrityError("W08_BUNDLE_PUBLICATION_DRIFT")
                published += 1
            elif projections:
                raise PipelineIntegrityError("W08_BUNDLE_UNOWNED_PROJECTION")
            if fsm_rows[(document_id, ast_hash)] == "READY_FOR_ASSEMBLY" and (
                publication is None or states != {"COMPLETED"}
            ):
                raise PipelineIntegrityError("W08_BUNDLE_READY_WITHOUT_PUBLICATION")
            digests.append({
                "document_id": document_id, "ast_hash": ast_hash,
                "manifest": plan.digest, "states": sorted(states),
                "receipts": len(receipts), "published": publication is not None,
            })

        orphan_tasks = queue.execute(
            "SELECT document_id,ast_hash FROM chunk_tasks"
        ).fetchall()
        if any((doc, ast_hash) not in plan_keys for doc, ast_hash in orphan_tasks):
            raise PipelineIntegrityError("W08_BUNDLE_ORPHAN_TASK")
        orphans = len(set(fsm_rows) - plan_keys)
        summary = json.dumps(digests, sort_keys=True, separators=(",", ":"))
        return FrozenBundleAudit(
            bundle_sha256=sha256(summary.encode("utf-8")).hexdigest(),
            generation_count=len(plans), pending_generations=pending,
            uncertain_generations=uncertain,
            receipt_only_generations=receipt_only,
            published_generations=published,
            orphan_fsm_generations=orphans,
        )


class _closing_sqlite:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def __enter__(self) -> sqlite3.Connection:
        return self.connection

    def __exit__(self, *_: object) -> None:
        self.connection.close()
