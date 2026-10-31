"""G3-B4/4: durable OCR profile and verified projection at assembly read.

Real disposable SQLite connections and AST registry. No OCR provider, Groq,
Tectonic or network calls; no claim of physical PDF->PDF end-to-end coverage.
"""
from hashlib import sha256
import sqlite3
from typing import cast

import pytest

from core.ast.enums import ContentNodeType
from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode, ParagraphPayload
from core.ast.registry import ASTRegistry
from core.compiler.assembler import AssemblyPolicy, DocumentAssembler
from core.compiler.context_resolver import CQRSAssemblyContextResolver
from core.compiler.rendering.mapper import DefaultRenderUnitMapper
from core.compiler.service import CompilationService
from core.document_profile.models import InferredDocumentProfile, PageLayout
from core.domain.document import DocumentType
from infra.db.materialized_repo import MaterializedPlaneRepository
from infra.db.profile_store import SQLiteProfileStore


def _profile(layout=PageLayout.SINGLE_COLUMN, kind=None):
    return InferredDocumentProfile(layout=layout, document_type=kind)


def _materialized(conn):
    conn.execute("""CREATE TABLE valid_chunks_cache (
        document_id TEXT NOT NULL, ast_hash TEXT NOT NULL,
        node_id TEXT NOT NULL, content_hash TEXT NOT NULL,
        normalized_response TEXT NOT NULL, normalized_hash TEXT NOT NULL,
        projection_version INTEGER NOT NULL, last_updated REAL NOT NULL,
        PRIMARY KEY (document_id, ast_hash, node_id)
    )""")
    conn.commit()
    return MaterializedPlaneRepository(conn)


def _insert_projection(conn, document_id, ast_hash, node_id, text, version=1):
    conn.execute(
        "INSERT INTO valid_chunks_cache "
        "(document_id, ast_hash, node_id, content_hash, normalized_response, "
        "normalized_hash, projection_version, last_updated) VALUES (?,?,?,?,?,?,?,?)",
        (document_id, ast_hash, node_id, sha256(b"source").hexdigest(), text,
         sha256(text.encode("utf-8")).hexdigest(), version, 1.0),
    )
    conn.commit()


def test_profile_survives_independent_connection_and_restart(tmp_path):
    path = tmp_path / "documents.db"
    chosen_kind = next(iter(DocumentType))
    expected = _profile(PageLayout.DOUBLE_COLUMN, chosen_kind)
    with sqlite3.connect(path) as router:
        SQLiteProfileStore(router).save("doc", expected)
    with sqlite3.connect(path) as assembler:
        assert SQLiteProfileStore(assembler).get("doc") == expected


def test_profile_replay_is_idempotent(tmp_path):
    path = tmp_path / "documents.db"
    with sqlite3.connect(path) as conn:
        store = SQLiteProfileStore(conn)
        store.save("doc", _profile())
        store.save("doc", _profile())
        assert conn.execute("SELECT COUNT(*) FROM inferred_document_profiles").fetchone() == (1,)


def test_conflicting_profile_replay_never_overwrites(tmp_path):
    path = tmp_path / "documents.db"
    with sqlite3.connect(path) as conn:
        store = SQLiteProfileStore(conn)
        store.save("doc", _profile())
        with pytest.raises(ValueError, match="G3_B4_4_PROFILE_REPLAY_CONFLICT"):
            store.save("doc", _profile(PageLayout.DOUBLE_COLUMN))
        assert store.get("doc") == _profile()


def test_profile_not_found_returns_none(tmp_path):
    with sqlite3.connect(tmp_path / "documents.db") as conn:
        assert SQLiteProfileStore(conn).get("unknown") is None


def test_profile_document_isolation(tmp_path):
    with sqlite3.connect(tmp_path / "documents.db") as conn:
        store = SQLiteProfileStore(conn)
        store.save("one", _profile())
        store.save("two", _profile(PageLayout.DOUBLE_COLUMN))
        assert store.get("one") == _profile()
        assert store.get("two") == _profile(PageLayout.DOUBLE_COLUMN)


def test_profile_integrity_rejects_tampered_row(tmp_path):
    with sqlite3.connect(tmp_path / "documents.db") as conn:
        store = SQLiteProfileStore(conn)
        store.save("doc", _profile())
        conn.execute("UPDATE inferred_document_profiles SET layout='double_column'")
        conn.commit()
        with pytest.raises(ValueError, match="G3_B4_4_PROFILE_HASH_DRIFT"):
            store.get("doc")


def test_profile_invalid_enum_rejected_on_read_even_if_hash_matches(tmp_path):
    with sqlite3.connect(tmp_path / "documents.db") as conn:
        store = SQLiteProfileStore(conn)
        store.save("doc", _profile())
        layout = "unrecognized_layout"
        conn.execute("UPDATE inferred_document_profiles SET layout=?, profile_sha256=?",
                     (layout, store._digest("doc", layout, None)))
        conn.commit()
        with pytest.raises(ValueError, match="G3_B4_4_CORRUPT_PROFILE_ENUM"):
            store.get("doc")


def test_profile_invalid_type_rejected(tmp_path):
    with sqlite3.connect(tmp_path / "documents.db") as conn:
        store = SQLiteProfileStore(conn)
        with pytest.raises(ValueError, match="G3_B4_4_INVALID_PROFILE_ENUM"):
            store.save("doc", _profile(cast(PageLayout, "single_column")))


def test_assembly_projection_validates_digest(tmp_path):
    with sqlite3.connect(tmp_path / "materialized.db") as conn:
        repo = _materialized(conn)
        _insert_projection(conn, "doc", "generation", "node", "Texto traducido")
        projections = repo.get_assemblable_chunks("doc", "generation", ["node"], 1)
        assert len(projections) == 1
        assert projections[0].normalized_response == "Texto traducido"


def test_tampered_projection_fails_at_assembly_read(tmp_path):
    with sqlite3.connect(tmp_path / "materialized.db") as conn:
        repo = _materialized(conn)
        _insert_projection(conn, "doc", "generation", "node", "Texto original")
        conn.execute("UPDATE valid_chunks_cache SET normalized_response='Inyeccion'")
        conn.commit()
        with pytest.raises(ValueError, match="G3_B4_4_PROJECTION_HASH_DRIFT"):
            repo.get_assemblable_chunks("doc", "generation", ["node"], 1)


def test_tampered_hash_fails_at_assembly_read(tmp_path):
    with sqlite3.connect(tmp_path / "materialized.db") as conn:
        repo = _materialized(conn)
        _insert_projection(conn, "doc", "generation", "node", "Texto")
        conn.execute("UPDATE valid_chunks_cache SET normalized_hash=?", ("0" * 64,))
        conn.commit()
        with pytest.raises(ValueError, match="G3_B4_4_PROJECTION_HASH_DRIFT"):
            repo.get_assemblable_chunks("doc", "generation", ["node"], 1)


def test_wrong_generation_or_projection_version_not_consumed(tmp_path):
    with sqlite3.connect(tmp_path / "materialized.db") as conn:
        repo = _materialized(conn)
        _insert_projection(conn, "doc", "generation", "node", "Texto", version=1)
        assert repo.get_assemblable_chunks("doc", "other_generation", ["node"], 1) == []
        assert repo.get_assemblable_chunks("doc", "generation", ["node"], 2) == []
        assert repo.get_assemblable_chunks("doc", "generation", [], 1) == []


def test_restarted_ast_profile_and_projection_build_tex_without_external_services(tmp_path):
    doc_id = sha256(b"PDF fixture; no physical PDF renderer").hexdigest()
    ast = [ASTNode(node_id="p1", sequence_id=1, node_type=ContentNodeType.PARAGRAPH,
                   payload=ParagraphPayload(content="Source paragraph"))]
    ast_hash = compute_ast_hash(ast)
    ASTRegistry(workspace_dir=str(tmp_path)).register_ast(doc_id, ast_hash, ast)

    profile_db = tmp_path / "documents.db"
    materialized_db = tmp_path / "materialized.db"
    with sqlite3.connect(profile_db) as ocr_conn:
        SQLiteProfileStore(ocr_conn).save(doc_id, _profile())

    with sqlite3.connect(profile_db) as compiler_conn, sqlite3.connect(materialized_db) as mat_conn:
        profile_store = SQLiteProfileStore(compiler_conn)
        mat_repo = _materialized(mat_conn)
        _insert_projection(mat_conn, doc_id, ast_hash, "p1", "Translated paragraph")
        context = CQRSAssemblyContextResolver(
            ast_provider=ASTRegistry(workspace_dir=str(tmp_path)),
            materialized_plane=mat_repo,
        ).resolve(doc_id, ast_hash)

        class NoFallback:
            def get_verified_payload(self, job_id: str, chunk_id: str, expected_sha256: str) -> str:
                pytest.fail("unexpected fallback from complete G3 projections")

        class NoGeometry:
            def extract(self, node):
                return None

        class NoAsset:
            def extract(self, node):
                return None

        repository = NoFallback()
        service = CompilationService(
            assembler=DocumentAssembler(repository, policy=AssemblyPolicy()),
            payload_repository=repository,
            profile_store=profile_store,
            mapper=DefaultRenderUnitMapper(NoGeometry(), NoAsset()),
        )
        tex = service.compile_document(context)
        assert "Translated paragraph" in tex
        assert "p1" in tex
