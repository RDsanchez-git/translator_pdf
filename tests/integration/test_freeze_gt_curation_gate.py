"""Tests del gate O2 de curaduria en freeze_ground_truth.py (H-5.5-7).

Cobertura:
  a) Draft sin entrada CURATED         -> exit 2 + [FREEZE-GT-002]
  b) Draft con entrada CURATED + ref   -> sella, exit 0
  c) --allow-uncurated con sin CURATED -> warning + sella
  d) Corpus totalmente sellado sin checklist -> exit 0 (idempotencia)
  e) Checklist ausente con drafts      -> exit 2 + [FREEZE-GT-001]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload, NodeMetadata
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import LocalFileSystemGroundTruthDraftWriter


def _write_manifest(corpus_dir: Path, documents: list[RawDocumentEntryDTO]) -> None:
    dto = RawCorpusManifestDTO(
        corpus_version="1.0.0",
        manifest_hash="dummy_hash_for_test",
        documents=documents,
    )
    LocalFileSystemCorpusLoader(corpus_dir).save_manifest_dto(dto)


def _write_draft(corpus_dir: Path, doc_id: str) -> None:
    """Escribe un draft minimo valido (2 nodos paragraph) en ground_truth/."""
    draft_writer = LocalFileSystemGroundTruthDraftWriter(corpus_dir)
    metadata = NodeMetadata(
        bboxes=[],
        pages=[1],
        provider_native_id=None,
        confidence=1.0,
        layout_reading_order=1,
    )
    nodes = (
        ASTNode(
            node_id=f"{doc_id}_p1",
            sequence_id=1,
            node_type=ContentNodeType.PARAGRAPH,
            strategy=TranslationStrategy.TRANSLATE,
            metadata=metadata,
            depth=0,
            payload=ParagraphPayload(content="Primer parrafo."),
            control_plane={},
            parent_node_id=None,
            segment_index=0,
            segment_count=1,
        ),
        ASTNode(
            node_id=f"{doc_id}_p2",
            sequence_id=2,
            node_type=ContentNodeType.PARAGRAPH,
            strategy=TranslationStrategy.TRANSLATE,
            metadata=metadata,
            depth=0,
            payload=ParagraphPayload(content="Segundo parrafo."),
            control_plane={},
            parent_node_id=None,
            segment_index=0,
            segment_count=1,
        ),
    )
    draft_writer.save_draft_ast(doc_id, nodes)


def _make_doc(doc_id: str, sha: str, state: str | None) -> RawDocumentEntryDTO:
    """Construye una entrada minima de manifest.

    DocumentId y GroundTruthState son alias Annotated (no callables): la
    validacion de dominio (fail-fast, sin ':' y no vacio) la aplica Pydantic
    al construir el DTO, no una invocacion del alias. Se pasan strings planos.
    """
    return RawDocumentEntryDTO(
        document_id=doc_id,
        sha256=sha,
        traits=["native_pdf"],
        page_count=1,
        oracle_hash=None if state is None else f"oracle_{doc_id}",
        ground_truth_state=state,
    )


def _run_freeze(corpus_dir: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    repo_root = Path(__file__).resolve().parents[2]
    cmd = [
        sys.executable,
        "-m", "tools.evaluation.freeze_ground_truth",
        "--corpus-dir", str(corpus_dir),
    ]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)


def test_draft_without_curated_entry_aborts(tmp_path: Path) -> None:
    """Caso (a): draft pendiente sin entrada CURATED -> FREEZE-GT-002."""
    _write_manifest(tmp_path, [_make_doc("doc_A", "a" * 64, None)])
    _write_draft(tmp_path, "doc_A")
    checklist = tmp_path / "curation_checklist.json"
    checklist.write_text(json.dumps({"doc_A": {"status": "PENDING", "report_ref": None, "curated_at": None}}), encoding="utf-8")

    result = _run_freeze(tmp_path)

    assert result.returncode == 2
    assert "[FREEZE-GT-002]" in result.stderr
    assert "doc_A" in result.stderr


def test_draft_with_curated_entry_seals(tmp_path: Path) -> None:
    """Caso (b): draft con entrada CURATED + report_ref -> sellado exitoso."""
    _write_manifest(tmp_path, [_make_doc("doc_B", "b" * 64, None)])
    _write_draft(tmp_path, "doc_B")
    checklist = tmp_path / "curation_checklist.json"
    checklist.write_text(
        json.dumps({"doc_B": {"status": "CURATED", "report_ref": "CURATION_REPORT:doc_B", "curated_at": "2026-09-14T00:00:00"}}),
        encoding="utf-8",
    )

    result = _run_freeze(tmp_path)

    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "Cryptographic lock complete" in result.stderr


def test_allow_uncurated_overrides_gate_with_warning(tmp_path: Path) -> None:
    """Caso (c): --allow-uncurated con draft sin CURATED -> warning + sella."""
    _write_manifest(tmp_path, [_make_doc("doc_C", "c" * 64, None)])
    _write_draft(tmp_path, "doc_C")
    # sin checklist

    result = _run_freeze(tmp_path, extra_args=["--allow-uncurated"])

    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "[FREEZE-W01]" in result.stderr
    assert "doc_C" in result.stderr


def test_fully_sealed_corpus_without_checklist_is_noop(tmp_path: Path) -> None:
    """Caso (d): corpus totalmente sellado, sin checklist -> exit 0 (idempotencia MIG-06)."""
    _write_manifest(tmp_path, [_make_doc("doc_D", "d" * 64, "sealed")])
    # El oráculo sellado vive en ground_truth/; sin él la biyección falla
    # (FREEZE-004) antes de que el gate de curaduría se evalúe.
    _write_draft(tmp_path, "doc_D")

    result = _run_freeze(tmp_path)

    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "[FREEZE-GT-001]" not in result.stderr
    assert "[FREEZE-GT-002]" not in result.stderr


def test_missing_checklist_with_pending_drafts_aborts(tmp_path: Path) -> None:
    """Caso (e): checklist ausente con drafts pendientes -> FREEZE-GT-001."""
    _write_manifest(tmp_path, [_make_doc("doc_E", "e" * 64, None)])
    _write_draft(tmp_path, "doc_E")
    # sin checklist

    result = _run_freeze(tmp_path)

    assert result.returncode == 2
    assert "[FREEZE-GT-001]" in result.stderr
    assert "curation_checklist.json" in result.stderr