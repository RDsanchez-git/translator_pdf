"""Tests de integracion de curate_gt.py (Batch 2a, H-5.5-7)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader

REPO = Path(__file__).resolve().parents[2]


def _make_doc(doc_id: str, sha: str, state: str | None = None) -> RawDocumentEntryDTO:
    return RawDocumentEntryDTO(
        document_id=doc_id, sha256=sha, traits=["native_pdf"], page_count=1,
        oracle_hash=None if state is None else f"oracle_{doc_id}",
        ground_truth_state=state,
    )


def _write_manifest(corpus_dir: Path, docs: list[RawDocumentEntryDTO]) -> None:
    LocalFileSystemCorpusLoader(corpus_dir).save_manifest_dto(
        RawCorpusManifestDTO(corpus_version="1.0.0", manifest_hash="dummy_hash", documents=docs)
    )


def _run(corpus_dir: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "tools.evaluation.curate_gt", "--corpus-dir", str(corpus_dir), *extra],
        capture_output=True, text=True, cwd=REPO,
    )


def test_create_curated_entry(tmp_path: Path) -> None:
    _write_manifest(tmp_path, [_make_doc("doc_A", "a" * 64)])
    result = _run(tmp_path, "--doc-id", "doc_A", "--status", "CURATED", "--report-ref", "CURATION_REPORT:§4.2")
    assert result.returncode == 0, result.stderr
    entry = json.loads((tmp_path / "curation_checklist.json").read_text(encoding="utf-8"))["doc_A"]
    assert entry["status"] == "CURATED"
    assert entry["report_ref"] == "CURATION_REPORT:§4.2"
    assert entry["curated_at"]


def test_pending_to_curated_and_back_resets(tmp_path: Path) -> None:
    _write_manifest(tmp_path, [_make_doc("doc_B", "b" * 64)])
    assert _run(tmp_path, "--doc-id", "doc_B", "--status", "PENDING").returncode == 0
    path = tmp_path / "curation_checklist.json"
    pending = json.loads(path.read_text(encoding="utf-8"))["doc_B"]
    assert pending == {"status": "PENDING", "report_ref": None, "curated_at": None}
    assert _run(tmp_path, "--doc-id", "doc_B", "--status", "CURATED", "--report-ref", "CR:§1").returncode == 0
    curated = json.loads(path.read_text(encoding="utf-8"))["doc_B"]
    assert curated["status"] == "CURATED" and curated["report_ref"] == "CR:§1" and curated["curated_at"]
    assert _run(tmp_path, "--doc-id", "doc_B", "--status", "PENDING").returncode == 0
    reset = json.loads(path.read_text(encoding="utf-8"))["doc_B"]
    assert reset == {"status": "PENDING", "report_ref": None, "curated_at": None}


def test_refuse_sealed(tmp_path: Path) -> None:
    _write_manifest(tmp_path, [_make_doc("doc_C", "c" * 64, "sealed")])
    result = _run(tmp_path, "--doc-id", "doc_C", "--report-ref", "CR:§1")
    assert result.returncode == 2
    assert "[CURATE-003]" in result.stderr
    assert not (tmp_path / "curation_checklist.json").exists()


def test_refuse_unknown_doc(tmp_path: Path) -> None:
    _write_manifest(tmp_path, [_make_doc("doc_D", "d" * 64)])
    result = _run(tmp_path, "--doc-id", "doc_Z", "--report-ref", "CR:§1")
    assert result.returncode == 2
    assert "[CURATE-001]" in result.stderr


def test_refuse_empty_report_ref(tmp_path: Path) -> None:
    _write_manifest(tmp_path, [_make_doc("doc_E", "e" * 64)])
    result = _run(tmp_path, "--doc-id", "doc_E", "--status", "CURATED", "--report-ref", "   ")
    assert result.returncode == 2
    assert "[CURATE-004]" in result.stderr


def test_serialization_deterministic(tmp_path: Path) -> None:
    _write_manifest(tmp_path, [_make_doc("doc_F", "f" * 64)])
    assert _run(tmp_path, "--doc-id", "doc_F", "--status", "PENDING").returncode == 0
    first = (tmp_path / "curation_checklist.json").read_bytes()
    assert _run(tmp_path, "--doc-id", "doc_F", "--status", "PENDING").returncode == 0
    second = (tmp_path / "curation_checklist.json").read_bytes()
    assert first == second
    text = first.decode("utf-8")
    assert text.index('"curated_at"') < text.index('"report_ref"') < text.index('"status"')