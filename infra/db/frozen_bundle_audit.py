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
import re
from pathlib import Path
import sqlite3

from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode, TranslationTaskType
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.result_contract import materialize_node_results, parse_chunk_response
from core.context.plan_context_contract import derive_verified_plan_contexts
from core.context.snapshot_contract import ContextSnapshotV1
from core.execution.exceptions import PipelineIntegrityError
from core.execution.state import DocumentState
from infra.db.control_repo import ControlPlaneRepository
from infra.db.staged_publication import verify_published_nodes


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
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", document_id)
            or not re.fullmatch(r"[0-9a-f]{64}", ast_hash)):
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
        valid_fsm_states = {state.value for state in DocumentState}
        if any(state not in valid_fsm_states for state in fsm_rows.values()):
            raise PipelineIntegrityError("W08_BUNDLE_UNKNOWN_FSM_STATE")
        plans = queue.execute(
            "SELECT document_id,ast_hash,manifest_sha256,manifest_json "
            "FROM chunk_plans ORDER BY document_id,ast_hash"
        ).fetchall()
        snapshot_table_exists = queue.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' "
            "AND name='g3_context_snapshots'"
        ).fetchone() is not None
        queue_repo = ControlPlaneRepository(queue)
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

            # Existing B2 reader enforces the deterministic task IDs, manifest
            # and generation with SELECT only; no queue write scope is entered.
            queue_repo.load_chunk_plan(document_id, ast_hash, ast)
            tasks = queue.execute(
                "SELECT node_id,task_state,task_id,execution_id "
                "FROM chunk_tasks WHERE document_id=? AND ast_hash=? AND worker_type='LLM'",
                (document_id, ast_hash),
            ).fetchall()
            if len(tasks) != len(plan.units) or {t[0] for t in tasks} != {
                unit.chunk_id for unit in plan.units
            }:
                raise PipelineIntegrityError("W08_BUNDLE_TASK_COVERAGE")
            states = {task[1] for task in tasks}
            by_chunk = {task[0]: task for task in tasks}
            units = {unit.chunk_id: unit for unit in plan.units}

            receipt_rows = queue.execute(
                "SELECT chunk_id,task_id,execution_id,raw_response,response_sha256 "
                "FROM chunk_result_receipts WHERE document_id=? AND ast_hash=?",
                (document_id, ast_hash),
            ).fetchall()
            if len(receipt_rows) != len({row[0] for row in receipt_rows}):
                raise PipelineIntegrityError("W08_BUNDLE_RECEIPT_DUPLICATION")
            for chunk_id, task_id, execution_id, raw, response_hash in receipt_rows:
                task = by_chunk.get(chunk_id)
                unit = units.get(chunk_id)
                if (task is None or unit is None
                        or (task[2], task[3]) != (task_id, execution_id)
                        or task[1] not in ("RESULT_STAGED", "COMPLETED")):
                    raise PipelineIntegrityError("W08_BUNDLE_RECEIPT_BINDING")
                if unit.chunk_type == TranslationTaskType.PRESERVE:
                    if raw is not None or response_hash is not None:
                        raise PipelineIntegrityError("W08_BUNDLE_PRESERVE_RECEIPT_DRIFT")
                else:
                    if not isinstance(raw, str) or not isinstance(response_hash, str):
                        raise PipelineIntegrityError("W08_BUNDLE_RECEIPT_PAYLOAD_DRIFT")
                    if sha256(raw.encode("utf-8")).hexdigest() != response_hash:
                        raise PipelineIntegrityError("W08_BUNDLE_RECEIPT_HASH_DRIFT")
                    # A correct checksum is not proof of a valid G3 response.
                    parse_chunk_response(plan, chunk_id, raw)

            snapshot_rows = (
                queue.execute(
                    "SELECT context_id,manifest_sha256,snapshot_sha256,snapshot_json "
                    "FROM g3_context_snapshots WHERE document_id=? AND ast_hash=?",
                    (document_id, ast_hash),
                ).fetchall()
                if snapshot_table_exists else []
            )
            modern_context = (
                bool(snapshot_rows)
                or any(node.control_plane.get("context_id") is not None for node in ast)
                or any(unit.context_id.startswith("CTX_") for unit in plan.units)
            )
            if modern_context:
                # The production W08-2b verifier derives required contexts from
                # this same AST. Missing modern rows must not masquerade as legacy.
                expected_snapshots = derive_verified_plan_contexts(plan, ast)
                actual_contexts = {row[0] for row in snapshot_rows}
                if (len(snapshot_rows) != len(actual_contexts)
                        or actual_contexts != set(expected_snapshots)):
                    raise PipelineIntegrityError("W08_BUNDLE_CONTEXT_SNAPSHOT_COVERAGE")
                for context_id, manifest_ref, snapshot_ref, snapshot_json in snapshot_rows:
                    expected_snapshot = expected_snapshots[context_id]
                    snapshot = ContextSnapshotV1.from_json(snapshot_json)
                    if (manifest_ref != plan.digest
                            or snapshot_ref != expected_snapshot.snapshot_sha256
                            or snapshot != expected_snapshot):
                        raise PipelineIntegrityError("W08_BUNDLE_CONTEXT_SNAPSHOT_DRIFT")
            # A pre-W08 plan without CTX provenance and without snapshots is
            # historical, not authorized for inference or automatic recovery.

            publication = material.execute(
                "SELECT manifest_sha256,result_sha256,projection_version "
                "FROM g3_plan_publications WHERE document_id=? AND ast_hash=?",
                (document_id, ast_hash),
            ).fetchone()
            has_projections = material.execute(
                "SELECT 1 FROM valid_chunks_cache "
                "WHERE document_id=? AND ast_hash=? LIMIT 1",
                (document_id, ast_hash),
            ).fetchone() is not None

            if publication is not None:
                if states not in ({"RESULT_STAGED"}, {"COMPLETED"}):
                    raise PipelineIntegrityError("W08_BUNDLE_PUBLICATION_TASK_STATES")
                if len(receipt_rows) != len(plan.units):
                    raise PipelineIntegrityError("W08_BUNDLE_RECEIPT_COVERAGE")
                # Use the B3 publication verifier rather than a weaker parallel
                # hash check: this rebuilds node outputs from original receipts.
                responses = queue_repo.load_staged_chunk_responses(
                    plan, ast, allow_completed=True,
                )
                nodes = materialize_node_results(plan, responses)
                verify_published_nodes(
                    material, plan, ast, nodes,
                    projection_version=publication[2],
                )
                published += 1
            elif has_projections:
                raise PipelineIntegrityError("W08_BUNDLE_UNOWNED_PROJECTION")
            elif states in ({"RESULT_STAGED"}, {"COMPLETED"}):
                if len(receipt_rows) != len(plan.units):
                    raise PipelineIntegrityError("W08_BUNDLE_RECEIPT_COVERAGE")
                queue_repo.load_staged_chunk_responses(
                    plan, ast, allow_completed=True,
                )
                receipt_only += 1
            elif "G3_EXTERNAL_UNKNOWN" in states:
                uncertain += 1
            else:
                pending += 1

            # Any FSM state beyond the G3 barrier requires committed and
            # finalized publication, not only READY_FOR_ASSEMBLY.
            post_g3_states = {
                "READY_FOR_ASSEMBLY", "ASSEMBLING",
                "READY_FOR_COMPILATION", "COMPILING", "COMPLETED",
            }
            if fsm_rows[(document_id, ast_hash)] in post_g3_states and (
                publication is None or states != {"COMPLETED"}
            ):
                raise PipelineIntegrityError("W08_BUNDLE_READY_WITHOUT_PUBLICATION")

            digests.append({
                "document_id": document_id, "ast_hash": ast_hash,
                "manifest": plan.digest, "states": sorted(states),
                "receipts": len(receipt_rows), "published": publication is not None,
            })

        if any((doc, ast_hash) not in plan_keys for doc, ast_hash in queue.execute(
            "SELECT document_id,ast_hash FROM chunk_tasks"
        )):
            raise PipelineIntegrityError("W08_BUNDLE_ORPHAN_TASK")
        for table, column in (
            ("chunk_result_receipts", "document_id,ast_hash"),
            ("g3_plan_publications", "document_id,ast_hash"),
            ("valid_chunks_cache", "document_id,ast_hash"),
        ):
            conn = queue if table == "chunk_result_receipts" else material
            if any(tuple(row) not in plan_keys for row in conn.execute(
                f"SELECT DISTINCT {column} FROM {table}"
            )):
                raise PipelineIntegrityError("W08_BUNDLE_ORPHAN_DURABLE_EVIDENCE")
        if snapshot_table_exists and any(
            tuple(row) not in plan_keys for row in queue.execute(
                "SELECT DISTINCT document_id,ast_hash FROM g3_context_snapshots"
            )
        ):
            raise PipelineIntegrityError("W08_BUNDLE_ORPHAN_CONTEXT_SNAPSHOT")
        orphans = len(set(fsm_rows) - plan_keys)

        # Include EVERY file in the isolated bundle, including custody metadata
        # and unreferenced ASTs. Reject symlinks rather than dereferencing files
        # outside the supplied immutable snapshot. Stream hashes for large DBs.
        content_fingerprints: list[tuple[str, str]] = []
        for file in sorted(directory.rglob("*")):
            if file.is_symlink():
                raise PipelineIntegrityError("W08_BUNDLE_SYMLINK_FORBIDDEN")
            if file.is_file():
                file_hash = sha256()
                with file.open("rb") as source:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        file_hash.update(block)
                content_fingerprints.append((
                    file.relative_to(directory).as_posix(), file_hash.hexdigest(),
                ))
            elif not file.is_dir():
                raise PipelineIntegrityError("W08_BUNDLE_UNSUPPORTED_FILE")
        summary = json.dumps(
            {"generations": digests, "files": content_fingerprints},
            sort_keys=True, separators=(",", ":"),
        )
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
