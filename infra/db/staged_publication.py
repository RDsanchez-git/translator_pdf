"""G3-B3/3a: recover staged chunk receipts into atomic node projections.

The queue receipt is the durable input and materialized.db is the output.
No cross-database atomicity, queue acknowledgement or daemon routing is claimed.
"""
from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import json
import sqlite3
import time
import uuid
from typing import Sequence

from core.ast.models import ASTNode
from core.ast.enums import TranslationStrategy
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.result_contract import NodeMaterialization, materialize_node_results
from infra.db.control_repo import ControlPlaneRepository


_PUBLICATION_DDL = """CREATE TABLE IF NOT EXISTS g3_plan_publications (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    manifest_sha256 TEXT NOT NULL CHECK(length(manifest_sha256) = 64),
    result_sha256 TEXT NOT NULL CHECK(length(result_sha256) = 64),
    projection_version INTEGER NOT NULL CHECK(projection_version > 0),
    created_at REAL NOT NULL,
    PRIMARY KEY (document_id, ast_hash)
)"""


@contextmanager
def _write_scope(conn: sqlite3.Connection):
    # SAVEPOINT commits stand-alone but never commits an enclosing caller transaction.
    name = f"g3_publish_{uuid.uuid4().hex}"
    conn.execute(f"SAVEPOINT {name}")
    try:
        yield
    except BaseException:
        try:
            conn.execute(f"ROLLBACK TO SAVEPOINT {name}")
        finally:
            conn.execute(f"RELEASE SAVEPOINT {name}")
        raise
    else:
        conn.execute(f"RELEASE SAVEPOINT {name}")


def _expected_rows(
    plan: ChunkPlan, ast: Sequence[ASTNode], nodes: Sequence[NodeMaterialization],
) -> tuple[list[tuple[str, str, str, str, str, int]], str]:
    """Build deterministic rows and a digest bound to original sources and plan."""
    if plan != ChunkPlan.build(plan.document_id, plan.ast_hash, ast, plan.units):
        raise ValueError("G3_B3_3_INVALID_PLAN")
    original = {str(n.node_id): n for n in ast}
    expected_ids: list[str] = []
    origins: dict[str, list[str]] = {}
    for unit in plan.units:
        for member in unit.members:
            if member.node_id not in origins:
                expected_ids.append(member.node_id)
                origins[member.node_id] = []
            if not origins[member.node_id] or origins[member.node_id][-1] != unit.chunk_id:
                origins[member.node_id].append(unit.chunk_id)
    if [n.node_id for n in nodes] != expected_ids:
        raise ValueError("G3_B3_3_NODE_COVERAGE_OR_ORDER")
    rows: list[tuple[str, str, str, str, str, int]] = []
    canonical: list[dict[str, object]] = []
    for node in nodes:
        if (node.document_id != plan.document_id or node.ast_hash != plan.ast_hash
                or node.node_id not in original or original[node.node_id].strategy == TranslationStrategy.OMIT
                or tuple(node.chunk_ids) != tuple(origins[node.node_id])):
            raise ValueError("G3_B3_3_NODE_BINDING_MISMATCH")
        if type(node.text) is not str or not node.text.strip():
            raise ValueError("G3_B3_3_INVALID_NODE_TEXT")
        digest = sha256(node.text.encode("utf-8")).hexdigest()
        if node.text_sha256 != digest:
            raise ValueError("G3_B3_3_NODE_HASH_MISMATCH")
        source_hash = sha256((original[node.node_id].text_content or "").encode("utf-8")).hexdigest()
        rows.append((plan.document_id, plan.ast_hash, node.node_id, source_hash, node.text, digest))
        canonical.append({"node_id": node.node_id, "source_sha256": source_hash,
                          "normalized_sha256": digest, "chunk_ids": list(node.chunk_ids)})
    payload = {"manifest_sha256": plan.digest, "nodes": canonical}
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return rows, sha256(serialized.encode("utf-8")).hexdigest()


def _verify_rows(
    conn: sqlite3.Connection, plan: ChunkPlan,
    rows: list[tuple[str, str, str, str, str, str]], result_sha256: str,
    projection_version: int,
) -> None:
    publication = conn.execute(
        "SELECT manifest_sha256, result_sha256, projection_version "
        "FROM g3_plan_publications WHERE document_id=? AND ast_hash=?",
        (plan.document_id, plan.ast_hash),
    ).fetchone()
    if publication != (plan.digest, result_sha256, projection_version):
        raise ValueError("G3_B3_3_PUBLICATION_CONFLICT_OR_MISSING")
    actual = conn.execute(
        "SELECT document_id, ast_hash, node_id, content_hash, normalized_response, "
        "normalized_hash, projection_version FROM valid_chunks_cache "
        "WHERE document_id=? AND ast_hash=? ORDER BY node_id",
        (plan.document_id, plan.ast_hash),
    ).fetchall()
    expected = sorted([(*r, projection_version) for r in rows], key=lambda row: row[2])
    if actual != expected:
        raise ValueError("G3_B3_3_PROJECTION_DRIFT")


def verify_published_nodes(
    conn: sqlite3.Connection, plan: ChunkPlan, ast: Sequence[ASTNode],
    nodes: Sequence[NodeMaterialization], *, projection_version: int = 1,
) -> None:
    """Read-only verification for later queue finalization and crash recovery."""
    if type(projection_version) is not int or projection_version < 1:
        raise ValueError("G3_B3_3_INVALID_VERSION")
    rows, result_hash = _expected_rows(plan, ast, nodes)
    _verify_rows(conn, plan, rows, result_hash, projection_version)


def publish_staged_plan(
    queue_repo: ControlPlaneRepository,
    materialized_conn: sqlite3.Connection,
    plan: ChunkPlan,
    ast: Sequence[ASTNode],
    *,
    projection_version: int = 1,
) -> bool:
    """Publish all node projections atomically in materialized.db.

    Requires every queue task to be RESULT_STAGED with a validated receipt.
    Returns True on first publication and False for an identical replay.
    Does NOT complete tasks, alter queue.db, write event.db or call any provider.
    """
    if type(projection_version) is not int or projection_version < 1:
        raise ValueError("G3_B3_3_INVALID_VERSION")
    responses = queue_repo.load_staged_chunk_responses(plan, ast)
    nodes = materialize_node_results(plan, responses)
    rows, result_hash = _expected_rows(plan, ast, nodes)
    with _write_scope(materialized_conn):
        materialized_conn.execute(_PUBLICATION_DDL)
        existing = materialized_conn.execute(
            "SELECT 1 FROM g3_plan_publications WHERE document_id=? AND ast_hash=?",
            (plan.document_id, plan.ast_hash),
        ).fetchone()
        if existing is not None:
            _verify_rows(materialized_conn, plan, rows, result_hash, projection_version)
            return False
        prior = materialized_conn.execute(
            "SELECT 1 FROM valid_chunks_cache WHERE document_id=? AND ast_hash=? LIMIT 1",
            (plan.document_id, plan.ast_hash),
        ).fetchone()
        if prior:
            raise ValueError("G3_B3_3_UNOWNED_PROJECTIONS")
        now = time.time()
        materialized_conn.executemany(
            "INSERT INTO valid_chunks_cache "
            "(document_id,ast_hash,node_id,content_hash,normalized_response,normalized_hash,"
            "projection_version,last_updated) VALUES (?,?,?,?,?,?,?,?)",
            [(*row, projection_version, now) for row in rows],
        )
        materialized_conn.execute(
            "INSERT INTO g3_plan_publications "
            "(document_id,ast_hash,manifest_sha256,result_sha256,projection_version,created_at) "
            "VALUES (?,?,?,?,?,?)",
            (plan.document_id, plan.ast_hash, plan.digest, result_hash, projection_version, now),
        )
        _verify_rows(materialized_conn, plan, rows, result_hash, projection_version)
    return True
