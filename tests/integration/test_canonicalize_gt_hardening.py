"""Tests del hardening Batch 2a de canonicalize_gt.py (codigos CANON-*)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, NodeMetadata, ParagraphPayload
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import LocalFileSystemGroundTruthDraftWriter

REPO = Path(__file__).resolve().parents[2]


def _write_manifest(corpus_dir: Path, doc_id: str, state: str | None = None) -> None:
    LocalFileSystemCorpusLoader(corpus_dir).save_manifest_dto(
        RawCorpusManifestDTO(
            corpus_version="1.0.0", manifest_hash="dummy_hash",
            documents=[RawDocumentEntryDTO(
                document_id=doc_id, sha256="a" * 64, traits=["native_pdf"], page_count=1,
                oracle_hash=None if state is None else f"oracle_{doc_id}", ground_truth_state=state,
            )],
        )
    )


def _write_draft(corpus_dir: Path, doc_id: str, node_ids: tuple[str, ...]) -> None:
    md = NodeMetadata(bboxes=[], pages=[1])
    nodes = tuple(
        ASTNode(node_id=nid, sequence_id=i + 1, node_type=ContentNodeType.PARAGRAPH,
                metadata=md, payload=ParagraphPayload(content=f"texto {i}"))
        for i, nid in enumerate(node_ids)
    )
    LocalFileSystemGroundTruthDraftWriter(corpus_dir).save_draft_ast(doc_id, nodes)


def _run(corpus_dir: Path, doc_id: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "tools.evaluation.canonicalize_gt", "--corpus-dir", str(corpus_dir), "--doc-id", doc_id],
        capture_output=True, text=True, cwd=REPO,
    )


def test_no_legacy_ids_is_noop(tmp_path: Path) -> None:
    _write_manifest(tmp_path, "doc_A")
    _write_draft(tmp_path, "doc_A", ("p1_b0",))
    gt = tmp_path / "ground_truth" / "doc_A.json"
    before = gt.read_bytes()
    result = _run(tmp_path, "doc_A")
    assert result.returncode == 0, result.stderr
    assert gt.read_bytes() == before
    assert not (tmp_path / "doc_A_canonicalization_lineage.json").exists()


def test_legacy_ids_canonicalized_with_lineage(tmp_path: Path) -> None:
    _write_manifest(tmp_path, "doc_B")
    _write_draft(tmp_path, "doc_B", ("value='p1_b0'", "p1_b1"))
    result = _run(tmp_path, "doc_B")
    assert result.returncode == 0, result.stderr
    import json
    nodes = json.loads((tmp_path / "ground_truth" / "doc_B.json").read_text(encoding="utf-8"))
    assert [n["node_id"] for n in nodes] == ["p1_b0", "p1_b1"]
    lineage = json.loads((tmp_path / "doc_B_canonicalization_lineage.json").read_text(encoding="utf-8"))
    assert lineage == [{"old_id": "value='p1_b0'", "new_id": "p1_b0"}]


def test_collision_aborts(tmp_path: Path) -> None:
    _write_manifest(tmp_path, "doc_C")
    _write_draft(tmp_path, "doc_C", ("value='p1_b0'", "value='p1_b0'"))
    result = _run(tmp_path, "doc_C")
    assert result.returncode == 2
    assert "[CANON-002]" in result.stderr


def test_refuse_sealed(tmp_path: Path) -> None:
    _write_manifest(tmp_path, "doc_D", "sealed")
    _write_draft(tmp_path, "doc_D", ("value='p1_b0'",))
    gt = tmp_path / "ground_truth" / "doc_D.json"
    before = gt.read_bytes()
    result = _run(tmp_path, "doc_D")
    assert result.returncode == 2
    assert "[CANON-003]" in result.stderr
    assert gt.read_bytes() == before